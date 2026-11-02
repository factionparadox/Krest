"""Wiring checks: scripts parse, every file the build copies exists, the desktop's settings refer
to programs Pustota installs, and the lessons cover the commands the tools point to."""
import importlib.machinery
import importlib.util
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
DESK = ROOT / 'desktop/root'
PACKAGES = set(' '.join(l for l in (ROOT / 'packages.txt').read_text().splitlines()
                        if not l.startswith('#')).split())


def shell_scripts():
    for path in [*ROOT.glob('build/*.sh'), *ROOT.glob('installer/*'), *(DESK / 'usr/bin').iterdir(),
                 *ROOT.glob('srcpkgs/*/files/*/run')]:
        if path.is_file() and path.read_text(errors='ignore').startswith('#!') and 'python' not in path.read_text().splitlines()[0]:
            yield path


class Scripts(unittest.TestCase):
    def test_shell_syntax(self):
        for path in shell_scripts():
            shell = 'bash' if 'bash' in path.read_text().splitlines()[0] else 'sh'
            r = subprocess.run([shell, '-n', str(path)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, f'{path}: {r.stderr}')

    def test_python_compiles(self):
        for path in (ROOT / 'installer/pustota-installer.py', ROOT / 'learn/pustota-learn',
                     ROOT / 'russian/pustota-russian', ROOT / 'russian/pustota-content'):
            subprocess.run(['python3', '-m', 'py_compile', str(path)], check=True)

    def test_executables_are_executable(self):
        for path in [*(DESK / 'usr/bin').iterdir(), ROOT / 'learn/pustota-learn',
                     ROOT / 'russian/pustota-russian', ROOT / 'russian/pustota-content',
                     ROOT / 'srcpkgs/ollama-bin/files/ollama/run', ROOT / 'installer/pustota-installer',
                     *(p for p in ROOT.glob('build/*.sh') if p.name != 'void-mirrors.sh'),
                     ROOT / 'build/make-branding.py']:
            self.assertTrue(path.stat().st_mode & 0o111, path)


class Build(unittest.TestCase):
    def test_files_the_iso_build_copies_exist(self):
        text = (ROOT / 'build/make-iso.sh').read_text()
        made_by_the_build = {'out', 'out/pustota-x86_64.iso'}
        for rel in re.findall(r'"\$root/([^"$]+)"', text):
            if rel not in made_by_the_build:
                self.assertTrue((ROOT / rel).exists(), rel)

    def test_files_the_package_build_copies_exist(self):
        text = (ROOT / 'build/build-packages.sh').read_text()
        for rel in re.findall(r'"\$root/([^"*{}$]+)"', text):
            self.assertTrue((ROOT / rel).exists(), rel)

    def test_kernel_and_pins(self):
        text = (ROOT / 'build/make-iso.sh').read_text()
        self.assertIn('-v linux-mainline', text)
        self.assertIn('rev=3aa194bdea9c83de0b5d78fb889a88f000a44fab', text)
        self.assertIn('linux-mainline', PACKAGES)
        self.assertNotIn('linux', PACKAGES)               # Void's default kernel stays out

    def test_package_list_has_no_duplicates(self):
        words = ' '.join(l for l in (ROOT / 'packages.txt').read_text().splitlines()
                         if not l.startswith('#')).split()
        self.assertEqual(len(words), len(set(words)))


class Desktop(unittest.TestCase):
    rc = (DESK / 'etc/pustota/ratpoisonrc').read_text()
    # ratpoison 1.4.9 commands used in the file (man ratpoison)
    KNOWN = {'startup_message', 'escape', 'set', 'definekey', 'exec', 'next', 'prev', 'windows',
             'delete', 'vsplit', 'hsplit', 'remove', 'only', 'focusleft', 'focusright', 'focusup',
             'focusdown', 'exchangeleft', 'exchangeright', 'exchangeup', 'exchangedown', 'select',
             'source', 'gselect', 'gmove', 'addhook'}

    def test_ratpoison_commands_are_real(self):
        for line in self.rc.splitlines():
            if not line.strip() or line.startswith('#'):
                continue
            words = line.split()
            self.assertIn(words[0], self.KNOWN, line)
            if words[0] == 'definekey':
                self.assertIn(words[3], self.KNOWN, line)

    def test_programs_bound_to_keys_are_installed(self):
        provided = {'pustota-menu', 'pustota-acme', 'pustota-keys', 'pustota-screenshot', 'loginctl',
                    'networkmanager_dmenu', 'dmenu_run', 'pustota-open', 'pustota-overview',
                    'pustota-width', 'pustota-workstations', 'pustota-term', 'pustota-nightlight', 'pustota-handbook', 'pustota-sleepcheck',
                    'clipmenu'}
        for script in provided:
            if script.startswith('pustota-'):
                self.assertTrue((DESK / 'usr/bin' / script).is_file(), script)
        packages_of = {'xterm': 'xterm', 'firefox': 'firefox', 'pamixer': 'pamixer',
                       'brightnessctl': 'brightnessctl', 'bluetuith': 'bluetuith', 'pulsemixer': 'pulsemixer',
                       'mc': 'mc', 'networkmanager_dmenu': 'networkmanager-dmenu', 'dmenu_run': 'dmenu',
                       'loginctl': 'elogind'}
        for line in self.rc.splitlines():
            m = re.match(r'definekey top \S+ exec (\S+)', line)
            if m:
                prog = m.group(1)
                self.assertTrue(prog in provided or packages_of.get(prog) in PACKAGES, line)
                if prog in packages_of:
                    self.assertIn(packages_of[prog], PACKAGES, prog)

    def test_session_programs_are_installed(self):
        session = (DESK / 'usr/bin/pustota-session').read_text()
        for prog, pkg in (('xss-lock', 'xss-lock'), ('slock', 'slock'), ('dunst', 'dunst'),
                          ('pipewire', 'pipewire'), ('udiskie', 'udiskie'), ('xbanish', 'xbanish'),
                          ('polybar', 'polybar'), ('ratpoison', 'ratpoison'), ('xrdb', 'xrdb'),
                          ('xsetroot', 'xsetroot'), ('xset', 'xset'), ('feh', 'feh')):
            self.assertIn(prog, session)
            self.assertIn(pkg, PACKAGES)

    def test_bar_leaves_room_and_floats(self):
        bar = (DESK / 'etc/pustota/polybar.ini').read_text()
        height = int(re.search(r'^height = (\d+)', bar, re.M).group(1))
        self.assertIn(f'set padding 0 {height} 0 0', self.rc)
        self.assertIn('override-redirect = true', bar)
        for module in re.search(r'^modules-left = (.*)$', bar, re.M).group(1).split() + \
                      re.search(r'^modules-right = (.*)$', bar, re.M).group(1).split():
            self.assertIn(f'[module/{module}]', bar)

    def test_keys_sheet_matches_bindings(self):
        sheet = (DESK / 'usr/share/pustota/keys.txt').read_text()
        for key, bind in (('Super+Space', 's-space'), ('Super+Tab', 's-Tab'), ('Super+q', 's-q'),
                          ('Super+f', 's-f'), ('Super+r', 's-r'), ('Super+Shift+s', 's-S-s'),
                          ('Super+x', 's-x'), ('Super+z', 's-z'), ('Super+o', 's-o'),
                          ('Super+Escape', 's-Escape')):
            self.assertIn(key, sheet)
            self.assertIn(f'definekey top {bind} ', self.rc)
        # the Ctrl+Super chords for programs
        for letter in 'wtdveapcrnbmoyg':
            column = ' '.join(l[43:55] for l in sheet.splitlines())     # the PROGRAMS column
            self.assertRegex(column, rf'(^|\s){letter}(\s|$)', letter)
            self.assertIn(f'definekey top C-s-{letter} exec ', self.rc)

    def test_workstations(self):
        for n in '123456789':
            self.assertIn(f'definekey top s-{n} gselect {n}\n', self.rc)
            self.assertIn(f'definekey top s-S-{n} gmove {n}\n', self.rc)
        self.assertIn('definekey top s-S-sterling gmove 3', self.rc)     # Shift+3 on a UK keyboard
        bar = (DESK / 'etc/pustota/polybar.ini').read_text()
        self.assertIn('[module/workstation]', bar)
        self.assertIn('#workstation.hook.0', self.rc)
        ws = (DESK / 'usr/bin/pustota-workstations').read_text()
        self.assertIn('gnewbg', ws)

    def test_chord_programs_are_installed(self):
        opener = (DESK / 'usr/bin/pustota-open').read_text()
        for prog in ('firefox', 'pustota-term', 'mpv', 'mc', 'ani-cli'):
            self.assertIn(prog, opener)
        for pkg in ('firefox', 'mpv', 'mc', 'ani-cli', 'x-terminal', 'xterm'):
            self.assertIn(pkg, PACKAGES)
        for opt in ('web', 'terminal', 'discord', 'youtube', 'games', 'video', 'files', 'anime', 'vpn', 'office'):
            self.assertIn(f'pustota-open {opt}', self.rc)
            self.assertRegex(opener, rf'(?m)^  {opt}\)')
        self.assertIn('NetworkManager', PACKAGES)               # pustota-vpn uses nmcli

    def test_user_files_include_the_packaged_defaults(self):
        self.assertIn('source /etc/pustota/ratpoisonrc', (DESK / 'etc/skel/.ratpoisonrc').read_text())
        self.assertIn('include-file = /etc/pustota/polybar.ini',
                      (DESK / 'etc/skel/.config/polybar/config.ini').read_text())
        self.assertIn('exec /usr/bin/pustota-session', (DESK / 'etc/skel/.xinitrc').read_text())
        self.assertIn('exec startx', (DESK / 'etc/skel/.bash_profile').read_text())


class Learn(unittest.TestCase):
    def setUp(self):
        loader = importlib.machinery.SourceFileLoader('learn', str(ROOT / 'learn/pustota-learn'))
        spec = importlib.util.spec_from_loader('learn', loader)
        self.learn = importlib.util.module_from_spec(spec)
        loader.exec_module(self.learn)

    def test_every_alias_has_a_lesson(self):
        topics = {p.stem for p in (ROOT / 'learn/topics').glob('*.md')}
        for command, topic in self.learn.ALIASES.items():
            self.assertIn(topic, topics, command)

    def test_lessons_have_titles_and_no_old_names(self):
        for path in (ROOT / 'learn/topics').glob('*.md'):
            text = path.read_text()
            self.assertTrue(text.startswith('# '), path)
            self.assertNotRegex(text, r'(?i)cognoscenti|sddm|flwm|kitty|constellation-', path)

    def test_explain_does_not_run_anything(self):
        import contextlib, io
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.learn.DOC_ROOT = ROOT / 'learn'
            self.learn.explain(['touch', '/tmp/pustota-explain-must-not-create-this'])
        self.assertFalse(Path('/tmp/pustota-explain-must-not-create-this').exists())
        self.assertIn('NOT executed', out.getvalue())


if __name__ == '__main__':
    unittest.main()


class SourcePackages(unittest.TestCase):
    """srcpkgs/: xbps-src templates for what Void lacks."""

    def template(self, name):
        text = (ROOT / 'srcpkgs' / name / 'template').read_text()
        return text, dict(re.findall(r'^(\w+)=["]?([^"\n]*)', text, re.M))

    def test_every_template_pins_its_sources(self):
        for path in (ROOT / 'srcpkgs').iterdir():
            text, f = self.template(path.name)
            for field in ('pkgname', 'version', 'revision', 'short_desc', 'license', 'homepage'):
                self.assertIn(field, f, (path.name, field))
            self.assertEqual(f['pkgname'], path.name)
            self.assertLessEqual(len(f['short_desc']), 72, path.name)
            if 'distfiles' not in f:
                # fetched with git instead (do_fetch): pinned to a full commit, checked after checkout
                self.assertRegex(f.get('_commit', ''), r'^[0-9a-f]{40}$', path.name)
                self.assertIn('rev-parse HEAD', text, path.name)
                continue
            dist = re.search(r'^distfiles="([^"]*)"', text, re.M | re.S).group(1).split()
            sums = re.search(r'^checksum="?([^"\n]*(?:\n [^"\n]*)*)"?', text, re.M).group(1).split()
            self.assertEqual(len(dist), len(sums), path.name)
            for s in sums:
                self.assertRegex(s, r'^[0-9a-f]{64}$')
            # archs lists target machines; "noarch" matches none, so xbps-src refuses the package
            self.assertNotIn('noarch', f.get('archs', ''), path.name)

    def test_ollama_is_the_pinned_release_with_a_service(self):
        text, f = self.template('ollama-bin')
        self.assertIn('c9490e0f520be21271d969e6703f012268b1d39f8b70dd58854e5bfef7a75bb6', text)
        self.assertIn('vsv ollama', text)
        self.assertIn('system_accounts="_ollama"', text)
        run = (ROOT / 'srcpkgs/ollama-bin/files/ollama/run').read_text()
        self.assertIn('127.0.0.1', run)
        self.assertIn('chpst -u _ollama:_ollama /usr/bin/ollama serve', run)
        self.assertIn('ollama-bin', (ROOT / 'build/build-packages.sh').read_text())

    def test_ani_cli_is_installed_and_pinned(self):
        text, f = self.template('ani-cli')
        self.assertEqual(f['version'], '5.1')
        self.assertIn('c99221dcecb35c66815a7a77e5ebebde16c8d06a', text)
        for pkg in ('ani-cli', 'fastfetch', 'framework-system'):
            self.assertIn(pkg, PACKAGES)

    def test_build_uses_xbps_src_and_signs(self):
        srcpkgs = (ROOT / 'build/build-srcpkgs.sh').read_text()
        self.assertIn('rev=7be87667ad95aff4124fdcccb68e2c22b5453a26', srcpkgs)
        self.assertIn('XBPS_CHROOT_CMD=ethereal', srcpkgs)
        self.assertIn('/.pustota-build-root', srcpkgs)       # ethereal only in the disposable root
        self.assertIn('/current/bootstrap', srcpkgs)          # where base-chroot is published
        self.assertNotIn('xbps-src -m masterdir', srcpkgs)    # ethereal needs the unresolved default
        make = (ROOT / 'build/make-iso.sh').read_text()
        steps = [make.index(f'bash "$root/build/{s}"') for s in ('build-srcpkgs.sh', 'build-packages.sh', 'sign-repo.sh')]
        self.assertEqual(steps, sorted(steps))
        self.assertIn('var/db/xbps/keys', make)
        self.assertIn('--sign-pkg', (ROOT / 'build/sign-repo.sh').read_text())
        repo = (DESK / 'usr/share/xbps.d/20-pustota-repository.conf').read_text()
        self.assertIn('repository=https://github.com/factionparadox/Pustota/releases/download/repo-x86_64', repo)
        self.assertIn('repo-x86_64', (ROOT / 'build/publish-repo.sh').read_text())


class Mirrors(unittest.TestCase):
    def test_every_download_from_void_goes_through_the_chosen_mirror(self):
        for script in ('build/build-iso.sh', 'build/make-iso.sh', 'build/build-srcpkgs.sh',
                       'build/patch-void-mklive.py', 'installer/pustota-installer.py'):
            text = (ROOT / script).read_text()
            hits = [l for l in text.splitlines() if 'repo-default.voidlinux.org' in l
                    and 'VOID_MIRROR' not in l and 'MIRRORS' not in l and not l.lstrip().startswith(('#', "'--repository"))]
            self.assertEqual(hits, [], script)

    def test_pick_void_mirror(self):
        r = subprocess.run(['bash', '-c', '. build/void-mirrors.sh; VOID_MIRROR=https://example/void/ pick_void_mirror'],
                           cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(r.stdout.strip(), 'https://example/void')
        r = subprocess.run(['bash', '-c', '. build/void-mirrors.sh; VOID_MIRRORS="http://127.0.0.1:9"; pick_void_mirror'],
                           cwd=ROOT, capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)


class Compression(unittest.TestCase):
    def test_iso_is_zstd_level_3(self):
        make = (ROOT / 'build/make-iso.sh').read_text()
        self.assertIn('-i zstd -s zstd', make)
        self.assertNotRegex(make, r'-[is] (xz|gzip)')
        patch = (ROOT / 'build/patch-void-mklive.py').read_text()
        self.assertIn('-Xcompression-level 3', patch)
        self.assertIn('--compress=zstd -3 -q -T0', patch)


class Branding(unittest.TestCase):
    def test_fastfetch_config_and_logo(self):
        """The block logo: the roundel in true colour, two pixels per character."""
        import json
        raw = (DESK / 'etc/xdg/fastfetch/config.jsonc.in').read_text()
        config = json.loads(re.sub(r'^\s*//.*$', '', raw, flags=re.M))
        logo = config['logo']
        self.assertEqual((logo['type'], logo['source']), ('file-raw', '/usr/share/pustota/fastfetch-logo.txt'))
        art = (DESK / 'usr/share/pustota/fastfetch-logo.txt').read_text(encoding='utf-8')
        lines = art.splitlines()
        self.assertEqual(len(lines), logo['height'])
        for line in lines:
            self.assertEqual(len(re.sub(r'\x1b\[[0-9;]*m', '', line)), logo['width'])
        # the flag's three colours are all there: white, blue and red
        colours = {tuple(map(int, m)) for m in re.findall(r'\x1b\[[34]8;2;(\d+);(\d+);(\d+)m', art)}
        self.assertTrue(any(r > 220 and g > 220 and b > 220 for r, g, b in colours), 'white')
        self.assertTrue(any(b > 150 and r < 60 and g < 90 for r, g, b in colours), 'blue')
        self.assertTrue(any(r > 180 and g < 60 and b < 70 for r, g, b in colours), 'red')
        self.assertTrue(any('Пустота' in str(m) for m in config['modules']))
        self.assertIn('@VERSION@', raw)
        self.assertIn('config.jsonc.in', (ROOT / 'build/build-packages.sh').read_text())

    def test_logo_files(self):
        for rel in ('usr/share/pustota/pustota-wallpaper.png', 'usr/share/pustota/pustota-logo.png',
                    'usr/share/pixmaps/pustota.png'):
            self.assertGreater((DESK / rel).stat().st_size, 1000, rel)
        self.assertIn('pustota-wallpaper.png', (DESK / 'usr/bin/pustota-session').read_text())
        self.assertIn('feh', PACKAGES)


class NonfreeTests(unittest.TestCase):
    """intel-ucode is in Void's nonfree repository: the ISO build, installer and system need it."""

    def test_iso_build_uses_nonfree_and_not_musl_or_aarch64(self):
        src = (ROOT / 'build/make-iso.sh').read_text()
        self.assertIn('export XBPS_REPOSITORY="--repository=$VOID_MIRROR/current/nonfree"', src)
        self.assertLess(src.index('export XBPS_REPOSITORY'), src.index('./mkiso.sh'))

    def test_installed_system_keeps_nonfree(self):
        words = (ROOT / 'packages.txt').read_text().split()
        self.assertIn('intel-ucode', words)
        self.assertIn('void-repo-nonfree', words)


class Terminal(unittest.TestCase):
    """X-терминал: st through st-flexipatch, Plan 9 look, installed as x-terminal."""
    d = ROOT / 'srcpkgs/x-terminal'

    def test_patches_switched_on(self):
        patches = (self.d / 'files/patches.h').read_text()
        for p in ('SCROLLBACK_PATCH', 'SCROLLBACK_MOUSE_ALTSCREEN_PATCH', 'CLIPBOARD_PATCH',
                  'ANYSIZE_PATCH', 'BOXDRAW_PATCH', 'RIGHTCLICKTOPLUMB_PATCH',
                  'SELECTION_COLORS_PATCH', 'BOLD_IS_NOT_BRIGHT_PATCH'):
            self.assertIn(f'#define {p} 1\n', patches)

    def test_plan9_look(self):
        config = (self.d / 'files/config.h').read_text()
        self.assertIn('"Go Mono:size=11', config)
        self.assertIn('"#ffffea", /* 258 -> bg', config)
        self.assertIn('"#eeee9e", /* 260 -> selection', config)
        self.assertIn('unsigned int selectionbg = 260;', config)
        self.assertIn('static char *plumb_cmd = "pustota-plumb";', config)
        self.assertTrue((DESK / 'usr/bin/pustota-plumb').is_file())
        self.assertIn('font-go-ttf', PACKAGES)

    def test_never_clashes_with_st(self):
        t = (self.d / 'template').read_text()
        self.assertIn('usr/bin/x-terminal', t)
        self.assertIn('st-terminfo', t)
        self.assertIn('X-терминал', t)

    def test_every_terminal_goes_through_pustota_term(self):
        for f in (DESK / 'usr/bin').iterdir():
            if f.name != 'pustota-term':
                self.assertNotIn('xterm', f.read_text(), f.name)
        self.assertNotIn('xterm', (DESK / 'etc/pustota/ratpoisonrc').read_text())


class Extras(unittest.TestCase):
    def test_packages(self):
        for pkg in ('ufw', 'clipmenu', 'redshift', 'fprintd', 'ipafont-fonts-otf'):
            self.assertIn(pkg, PACKAGES)

    def test_session_and_keys(self):
        session = (DESK / 'usr/bin/pustota-session').read_text()
        self.assertIn('clipmenud &', session)
        self.assertIn('pustota-nightlight &', session)
        self.assertIn('definekey top s-v exec clipmenu', (DESK / 'etc/pustota/ratpoisonrc').read_text())
        self.assertIn('Super+v', (DESK / 'usr/share/pustota/keys.txt').read_text())

    def test_nightlight_finds_the_timezone_city(self):
        tab = ROOT / 'tests' / '_zone1970.tab'
        script = (DESK / 'usr/bin/pustota-nightlight').read_text()
        awk = re.search(r"place=\$\(awk -F'\\t' -v z=\"\$zone\" '(.*?)' /usr/share", script, re.S).group(1)
        tab.write_text('GB,GG\t+513030-0000731\tEurope/London\nJP\t+353916+1394441\tAsia/Tokyo\n')
        try:
            for zone, want in (('Europe/London', '51.51:-0.13'), ('Asia/Tokyo', '35.65:139.74')):
                out = subprocess.run(['awk', '-F\t', '-v', f'z={zone}', awk, str(tab)],
                                     capture_output=True, text=True, check=True).stdout
                self.assertEqual(out, want)
        finally:
            tab.unlink()


class GitOwnership(unittest.TestCase):
    """root runs git in folders the builder's user owns: both chroots must trust them."""
    def test_safe_directory(self):
        for f in ('build/build-iso.sh', 'build/build-srcpkgs.sh'):
            self.assertIn("GIT_CONFIG_KEY_0=safe.directory GIT_CONFIG_VALUE_0='*'", (ROOT / f).read_text(), f)


class Wiki(unittest.TestCase):
    """learn/wiki: the reference pages behind pustota-learn wiki."""
    root = ROOT / 'learn/wiki'

    def setUp(self):
        loader = importlib.machinery.SourceFileLoader('learnw', str(ROOT / 'learn/pustota-learn'))
        spec = importlib.util.spec_from_loader('learnw', loader)
        self.learn = importlib.util.module_from_spec(spec)
        loader.exec_module(self.learn)
        self.learn.DOC_ROOT = ROOT / 'learn'

    def test_pages_are_whole(self):
        pages = {p.stem for p in self.root.glob('*.md')}
        self.assertGreaterEqual(len(pages), 18)
        index = (self.root / 'index.md').read_text()
        for name in pages - {'index'}:
            text = (self.root / f'{name}.md').read_text()
            self.assertTrue(text.startswith('# '), name)
            self.assertIn('See also:', text, name)
            self.assertRegex(index, rf'(?m)^  {re.escape(name)} ', name)       # listed in the index
            for line in text.splitlines():
                self.assertLessEqual(len(line), 100, (name, line))

    def test_commands_point_at_real_pages(self):
        pages = {p.stem for p in self.root.glob('*.md')}
        for command, page in self.learn.WIKI_FOR.items():
            self.assertIn(page, pages, command)

    def test_logging_services_are_the_real_names(self):
        # Void's Handbook: socklog-unix and nanoklogd (there is no "nologd")
        import importlib.util as u
        spec = u.spec_from_file_location('inst', ROOT / 'installer/pustota-installer.py')
        inst = u.module_from_spec(spec); spec.loader.exec_module(inst)
        self.assertIn('nanoklogd', inst.SERVICES_OPTIONAL)
        self.assertIn('socklog', inst.GROUPS)
        for path in [*self.root.glob('*.md'), *(ROOT / 'learn/topics').glob('*.md')]:
            self.assertNotIn('nologd', path.read_text().replace('nanoklogd', ''), path.name)

    def test_wiki_and_search_work(self):
        import contextlib, io
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(self.learn.wiki('sv'), 0)            # a command finds its page
            self.assertEqual(self.learn.search(['vkpurge']), 0)
        self.assertIn('# runit', out.getvalue())
        self.assertIn('wiki kernel:', out.getvalue())
        self.assertEqual(self.learn.wiki('../../etc/passwd'), 2)

    def test_packaged(self):
        self.assertIn('learn/wiki/*.md', (ROOT / 'build/build-packages.sh').read_text())


class FrameworkAndOffice(unittest.TestCase):
    """What nixos-hardware's Framework 13 (Intel Core Ultra Series 3) module does, and the rest."""
    def test_framework_fixes(self):
        self.assertIn('blacklist cros_usbpd_charger',
                      (DESK / 'etc/modprobe.d/pustota-framework.conf').read_text())
        rules = (DESK / 'etc/udev/rules.d/50-pustota-framework.rules').read_text()
        self.assertIn('ATTR{idVendor}=="0bda", ATTR{idProduct}=="8156"', rules)
        trim = DESK / 'etc/cron.weekly/fstrim'
        self.assertTrue(trim.stat().st_mode & 0o111)
        self.assertIn('fstrim -a', trim.read_text())
        self.assertTrue({'snooze', 'run-parts', 'fwupd', 'fprintd', 'framework-system'} <= PACKAGES)

    def test_handbook_and_office(self):
        hb = (DESK / 'usr/bin/pustota-handbook').read_text()
        self.assertIn('mc "$docs/markdown" /usr/share/pustota/learn/wiki', hb)
        self.assertIn('void-docs', PACKAGES)
        self.assertIn('pustota-handbook', (DESK / 'usr/bin/pustota-menu').read_text())
        self.assertTrue({'libreoffice-writer', 'libreoffice-calc', 'libreoffice-i18n-en-GB',
                         'libreoffice-i18n-ru', 'hunspell-en_GB-all', 'hunspell-ru_RU'} <= PACKAGES)


class PersonalIso(unittest.TestCase):
    def test_music_never_committed_and_wired_through(self):
        self.assertIn('local/', (ROOT / '.gitignore').read_text().split())
        build = (ROOT / 'build/build-iso.sh').read_text()
        self.assertIn('music=$project/local/music', build)
        self.assertIn('--no-music', build)
        self.assertIn('PUSTOTA_MUSIC="$inmusic"', build)
        self.assertIn('pustota-personal-x86_64.iso', build)
        make = (ROOT / 'build/make-iso.sh').read_text()
        self.assertIn('"$ov/usr/lib/pustota/music/"', make)
        self.assertIn('iso=pustota-personal-x86_64.iso', make)


class Battery(unittest.TestCase):
    def test_battery_settings(self):
        watch = (DESK / 'usr/bin/pustota-battery').read_text()
        self.assertIn('BAT_HZ=60 AC_HZ=120', watch)
        self.assertIn('xrandr --output "$out" --rate', watch)
        self.assertIn('xrandr', PACKAGES)
        self.assertIn('hwdec=auto-safe', (DESK / 'etc/mpv/mpv.conf').read_text())
        self.assertIn('pref("media.ffmpeg.vaapi.enabled", true);',
                      (DESK / 'usr/lib/firefox/browser/defaults/preferences/pustota.js').read_text())
        self.assertIn('wifi.powersave = 3',
                      (DESK / 'etc/NetworkManager/conf.d/50-pustota-wifi-powersave.conf').read_text())

    def test_watch_switches_on_plug(self):
        """Run the watcher's power logic against a fake /sys and fake xrandr/xset."""
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / 'bin').mkdir()
            for tool, out in (('xrandr', 'echo "eDP-1 connected primary 2880x1920+0+0"; echo "xrandr $*" >> "$LOG"'),
                              ('xset', 'echo "xset $*" >> "$LOG"')):
                (d / 'bin' / tool).write_text(f'#!/bin/sh\n[ "$1" = --query ] && {{ echo "eDP-1 connected"; exit; }}\n{out}\n')
                (d / 'bin' / tool).chmod(0o755)
            src = (DESK / 'usr/bin/pustota-battery').read_text()
            funcs = src[src.index('BAT_HZ='):src.index('power=\n')]
            script = funcs.replace('/sys/class/power_supply', str(d / 'ps')) + 'apply bat\napply ac\n'
            log = d / 'log'
            subprocess.run(['sh', '-c', script], env={'PATH': f"{d / 'bin'}:/usr/bin:/bin", 'LOG': str(log)},
                           check=True)
            lines = log.read_text().splitlines()
            self.assertEqual(lines[0], 'xrandr --output eDP-1 --rate 60')
            self.assertEqual(lines[1], 'xset s 300 300 dpms 300 420 600')
            self.assertEqual(lines[2], 'xrandr --output eDP-1 --rate 120')


class Battery(unittest.TestCase):
    """intel-lpmd without systemd, the sleep check, uBlock Origin."""
    d = ROOT / 'srcpkgs/intel-lpmd'

    def test_lpmd_package(self):
        t = (self.d / 'template').read_text()
        self.assertIn('_commit=956df747e56aca1739b39bff8cff77e81758af9a', t)     # tag v0.1.0
        self.assertIn('--with-systemdsystemunitdir=no', t)
        self.assertIn('elogind-devel', t)                  # libsystemd.pc and sd-bus come from elogind
        self.assertIn('vsv intel_lpmd', t)
        run = (self.d / 'files/intel_lpmd/run').read_text()
        self.assertIn('exec intel_lpmd --no-daemon --dbus-enable', run)
        self.assertIn('intel_lpmd_control AUTO', run)
        import xml.dom.minidom
        conf = xml.dom.minidom.parse(str(self.d / 'files/intel_lpmd_config_F6_M204.xml'))
        value = lambda tag: conf.getElementsByTagName(tag)[0].firstChild.data
        self.assertEqual(value('Mode'), '1')               # cgroup v2 isolate: no systemd
        self.assertEqual(value('BalancedDef'), '0')
        self.assertEqual(conf.getElementsByTagName('lp_mode_cpus')[0].firstChild, None)  # auto
        self.assertTrue({'intel-lpmd', 'upower'} <= PACKAGES)

    def test_installer_enables_it(self):
        import importlib.util as u
        spec = u.spec_from_file_location('inst2', ROOT / 'installer/pustota-installer.py')
        inst = u.module_from_spec(spec); spec.loader.exec_module(inst)
        self.assertIn('intel_lpmd', inst.SERVICES_OPTIONAL)

    def test_sleepcheck_and_firefox(self):
        sc = (DESK / 'usr/bin/pustota-sleepcheck').read_text()
        self.assertIn('rtcwake -m mem', sc)
        self.assertIn('low_power_idle_system_residency_us', sc)
        import json
        pol = json.loads((DESK / 'usr/lib/firefox/distribution/policies.json').read_text())
        self.assertIn('uBlock0@raymondhill.net', pol['policies']['ExtensionSettings'])
        menu = (DESK / 'usr/bin/pustota-menu').read_text()
        for opt in ('--touchscreen-enable false', '--kblight 0', '--click-force'):
            self.assertIn(opt, menu)


class Apps(unittest.TestCase):
    def test_webcord_freetube_steam(self):
        for name, digest in (('webcord', 'e4e96656b3b0f5a6954022c47bbd4af48f49f0838f37ac290ff80ae4f76123ea'),
                             ('freetube', 'e3a671357ac32edcd872c6ea3218c8921bd0fda7318706d8570ece44d2c1fcbf')):
            t = (ROOT / 'srcpkgs' / name / 'template').read_text()
            self.assertIn(f'checksum={digest}', t)
            self.assertIn('noverifyrdeps=yes', t)          # Electron brings its own libraries
            self.assertIn(name, PACKAGES)
        self.assertTrue({'steam', 'void-repo-multilib', 'void-repo-multilib-nonfree'} <= PACKAGES)
        self.assertIn('nofile    524288', (DESK / 'etc/security/limits.d/90-pustota-steam.conf').read_text())
        opener = (DESK / 'usr/bin/pustota-open').read_text()
        self.assertIn('have webcord && exec webcord', opener)


class ProtonVpn(unittest.TestCase):
    PKGS = ('python3-proton-core', 'python3-proton-keyring-linux', 'python3-sentry-sdk',
            'python3-proton-vpn-api-core', 'proton-vpn-gtk-app')

    def test_adopted_recipes_are_credited_and_pinned(self):
        for name in self.PKGS:
            t = (ROOT / 'srcpkgs' / name / 'template').read_text()
            self.assertIn('d4d093dd57df41f8a3f72f8c89c8417d8b23c21f', t, name)
            self.assertIn('Tommy Alderson, MIT', t, name)
            self.assertIn('make_check=no', t, name)
        api = (ROOT / 'srcpkgs/python3-proton-vpn-api-core/template').read_text()
        self.assertIn('--features "python,core,local_agent,protun,telemetry"', api)
        self.assertIn('skip_extraction="v${_protun_version}.tar.gz"', api)
        self.assertIn('proton-vpn-gtk-app', PACKAGES)

    def test_desktop_wiring(self):
        self.assertIn('gnome-keyring-daemon --start --components=secrets',
                      (DESK / 'usr/bin/pustota-session').read_text())
        self.assertIn('have protonvpn-app && exec protonvpn-app', (DESK / 'usr/bin/pustota-open').read_text())

