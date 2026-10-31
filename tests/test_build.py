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
                 *ROOT.glob('russian/sv/**/run')]:
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
                     ROOT / 'russian/sv/ollama/run', ROOT / 'installer/pustota-installer']:
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
             'source'}

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
                    'networkmanager_dmenu', 'dmenu_run'}
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
                          ('xsetroot', 'xsetroot'), ('xset', 'xset')):
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
        for key, bind in (('Super+Space', 's-space'), ('Super+d', 's-d'), ('Super+a', 's-a'),
                          ('Super+q', 's-q'), ('Super+s', 's-s'), ('Super+Shift+s', 's-S-s'),
                          ('Super+l', 's-l'), ('Super+o', 's-o'), ('Super+x', 's-x')):
            self.assertIn(key, sheet)
            self.assertIn(f'definekey top {bind} ', self.rc)

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
