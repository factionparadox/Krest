"""The installer's decisions, tested without a disk: partition sizes, partition names, locales,
the kernel line, autologin and the fstab check."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('installer', ROOT / 'installer/pustota-installer.py')
inst = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inst)
GiB = inst.GiB


class Plan(unittest.TestCase):
    def test_framework_with_32_gb_and_a_1_tb_disk(self):
        efi, swap, root = inst.plan(1000 * 10**9, 32 * GiB - 300 * 2**20)   # MemTotal is a bit under 32
        self.assertEqual((efi, swap), (1, 32))
        self.assertEqual(root, 1000 * 10**9 // GiB - 33)

    def test_small_disk_drops_swap_rather_than_root(self):
        self.assertEqual(inst.plan(40 * GiB, 32 * GiB), (1, 0, 39))

    def test_too_small_disk_is_refused(self):
        with self.assertRaises(ValueError):
            inst.plan(16 * GiB, 8 * GiB)

    def test_partition_names(self):
        self.assertEqual(inst.partition_path('/dev/nvme0n1', 3), '/dev/nvme0n1p3')
        self.assertEqual(inst.partition_path('/dev/sda', 1), '/dev/sda1')
        self.assertEqual(inst.partition_path('/dev/mmcblk0', 2), '/dev/mmcblk0p2')


class Files(unittest.TestCase):
    def test_locales_are_uncommented_not_duplicated(self):
        text = '#en_GB.UTF-8 UTF-8\n#en_US.UTF-8 UTF-8\n#ru_RU.UTF-8 UTF-8\n#de_DE.UTF-8 UTF-8\n'
        out = inst.enable_locales(text)
        self.assertIn('\nen_US.UTF-8 UTF-8\n', '\n' + out)
        for line in ('en_GB.UTF-8 UTF-8', 'ru_RU.UTF-8 UTF-8'):
            self.assertEqual(out.splitlines().count(line), 1)
        self.assertIn('#de_DE.UTF-8 UTF-8', out)
        self.assertEqual(inst.enable_locales(out), out)            # running twice changes nothing

    def test_locales_missing_from_the_file_are_added(self):
        self.assertIn('ru_RU.UTF-8 UTF-8', inst.enable_locales('#C.UTF-8 UTF-8\n'))

    def test_resume_goes_on_the_kernel_line_once(self):
        grub = 'GRUB_DEFAULT=0\nGRUB_CMDLINE_LINUX_DEFAULT="loglevel=4"\n'
        once = inst.with_resume(grub, 'abcd-1234')
        self.assertIn('GRUB_CMDLINE_LINUX_DEFAULT="resume=UUID=abcd-1234 loglevel=4"', once)
        self.assertEqual(inst.with_resume(once, 'abcd-1234'), once)
        self.assertEqual(inst.with_resume(grub, ''), grub)          # no swap, no resume

    def test_kernel_options(self):
        grub = 'GRUB_DEFAULT=0\nGRUB_CMDLINE_LINUX_DEFAULT="loglevel=4"\n'
        once = inst.with_kernel_options(grub)
        self.assertIn('GRUB_CMDLINE_LINUX_DEFAULT="loglevel=4 nvme.noacpi=1"', once)
        self.assertEqual(inst.with_kernel_options(once), once)
        both = inst.with_resume(once, 'abcd')
        self.assertIn('"resume=UUID=abcd loglevel=4 nvme.noacpi=1"', both)
        self.assertIn('GRUB_CMDLINE_LINUX_DEFAULT="nvme.noacpi=1"', inst.with_kernel_options('X=1\n'))
        self.assertIn('resume=UUID=x', inst.with_resume('GRUB_DEFAULT=0\n', 'x'))

    def test_autologin(self):
        void = 'if [ -x /sbin/agetty -o -x /bin/agetty ]; then\n\tGETTY_ARGS="--noclear"\nfi\nBAUD_RATE=38400\n'
        out = inst.autologin_conf(void, 'stephen')
        # the last assignment wins in sh, so the appended line takes effect
        self.assertTrue(out.rstrip().endswith('GETTY_ARGS="--noclear --autologin stephen"'))
        self.assertEqual(inst.autologin_conf('GETTY_ARGS="--noclear"\n', 'a'),
                         'GETTY_ARGS="--noclear --autologin a"\n')

    def test_fstab_check(self):
        good = ('# /dev/nvme0n1p3\nUUID=1 / xfs rw,relatime 0 1\nUUID=2 /boot/efi vfat rw 0 2\n'
                'UUID=3 none swap defaults 0 0\n')
        self.assertTrue(inst.fstab_ok(good))
        self.assertFalse(inst.fstab_ok('UUID=1 / xfs rw 0 1\n'))


class Plan_of_record(unittest.TestCase):
    """The choices the README promises are what the installer does."""
    src = (ROOT / 'installer/pustota-installer.py').read_text()

    def test_xfs_root_efi_and_mainline_kernel(self):
        for needle in ('"mkfs.xfs"', '"mkfs.vfat", "-F", "32"', 'ignorepkg=linux\\n',
                       '"xgenfstab", "-U"', '"xbps-reconfigure", "-fa"', '--target=x86_64-efi',
                       '"--removable"', '"pustota-desktop"', '"base-system"'):
            self.assertIn(needle, self.src, needle)

    def test_password_never_on_a_command_line(self):
        self.assertIn('chroot("chpasswd", input_text=f"{username}:{password}\\n")', self.src)
        self.assertNotIn('password)', self.src.replace('input_field(', ''))

    def test_required_services(self):
        self.assertEqual(inst.SERVICES_REQUIRED, ['dbus', 'elogind', 'NetworkManager'])
        self.assertIn('dhcpcd', inst.SERVICES_OFF)


if __name__ == '__main__':
    unittest.main()


class Mirrors(unittest.TestCase):
    def test_first_mirror_that_answers_is_used(self):
        import urllib.error
        from unittest import mock
        tried = []
        class Answer:
            def __enter__(self): return self
            def __exit__(self, *a): return False
            def read(self, n): return b'x'
        def fake(url, timeout):
            tried.append(url)
            if 'repo-default' in url or 'repo-de.' in url:
                raise urllib.error.URLError('connection refused')
            return Answer()
        saved = inst.MIRROR
        try:
            with mock.patch.object(inst.urllib.request, 'urlopen', fake):
                self.assertEqual(inst.check_repository(), 'https://repo-fi.voidlinux.org')
            self.assertEqual(inst.MIRROR, 'https://repo-fi.voidlinux.org/current')
            self.assertEqual(len(tried), 3)
            with mock.patch.object(inst.urllib.request, 'urlopen',
                                   lambda url, timeout: (_ for _ in ()).throw(urllib.error.URLError('down'))):
                with self.assertRaisesRegex(RuntimeError, 'No Void mirror answered'):
                    inst.check_repository()
        finally:
            inst.MIRROR = saved


class WholeInstall(unittest.TestCase):
    """install() from start to finish against a temporary folder, with every command faked.
    Checks the order of the steps and the files the installed system ends up with."""

    def setUp(self):
        import tempfile, types
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(__import__('shutil').rmtree, self.tmp)
        self.target = self.tmp / 'target'
        self.disk = str(self.tmp / 'nvme0n1')
        self.ran = []
        keys = self.tmp / 'keys'; keys.mkdir(); (keys / 'void.plist').write_text('key')
        self.saved = {n: getattr(inst, n) for n in
                      ('TARGET', 'TRUSTED_KEYS', 'LOGFILE', 'run', 'mount', 'uuid_of', 'ram_bytes', 'sp')}
        inst.TARGET, inst.TRUSTED_KEYS, inst.LOGFILE = self.target, keys, self.tmp / 'log'
        inst.run, inst.mount = self.fake_run, lambda dev, path, bind=False: Path(path).mkdir(parents=True, exist_ok=True)
        inst.uuid_of = lambda dev: 'SWAP-UUID'
        inst.ram_bytes = lambda: 32 * GiB
        inst.sp = types.SimpleNamespace(check_output=lambda *a, **k: str(512 * GiB), run=inst.sp.run,
                                        CalledProcessError=inst.sp.CalledProcessError)

    def tearDown(self):
        for name, value in self.saved.items():
            setattr(inst, name, value)

    fail_pkg = None

    def fake_run(self, *cmd, input_text=None, capture=False):
        cmd = [str(c) for c in cmd]
        self.ran.append(cmd)
        t = self.target
        if cmd[0] == 'partprobe':
            for n in (1, 2, 3):
                Path(inst.partition_path(self.disk, n)).write_text('')
        if cmd[0] == 'xbps-install' and self.fail_pkg and cmd[-1] == self.fail_pkg:
            raise inst.sp.CalledProcessError(2, cmd)
        if cmd[0] == 'xbps-install' and 'base-system' in cmd:   # a minimal Void system appears
            for svc in inst.SERVICES_REQUIRED + inst.SERVICES_OPTIONAL + ['dhcpcd', 'agetty-tty1']:
                (t / 'etc/sv' / svc).mkdir(parents=True, exist_ok=True)
            (t / 'etc/sv/agetty-tty1/conf').write_text('GETTY_ARGS="--noclear"\n')
            (t / 'etc/runit/runsvdir/default').mkdir(parents=True, exist_ok=True)
            (t / 'etc/runit/runsvdir/default/dhcpcd').symlink_to('/etc/sv/dhcpcd')
            (t / 'etc/group').write_text('root:x:0:\nwheel:x:1:\naudio:x:2:\nvideo:x:3:\n')
            (t / 'etc/default').mkdir(parents=True, exist_ok=True)
            (t / 'etc/default/grub').write_text('GRUB_CMDLINE_LINUX_DEFAULT="loglevel=4"\n')
            (t / 'etc/default/libc-locales').write_text('#en_GB.UTF-8 UTF-8\n#ru_RU.UTF-8 UTF-8\n')
            (t / 'usr/share/zoneinfo/Europe').mkdir(parents=True, exist_ok=True)
            (t / 'usr/share/zoneinfo/Europe/London').write_text('tz')
            (t / 'var/log').mkdir(parents=True, exist_ok=True)
            (t / 'etc/ufw').mkdir(parents=True, exist_ok=True)
            (t / 'etc/ufw/ufw.conf').write_text('# /etc/ufw/ufw.conf\nENABLED=no\nLOGLEVEL=low\n')
            (t / 'etc/pam.d').mkdir(parents=True, exist_ok=True)
            (t / 'etc/pam.d/sudo').write_text('#%PAM-1.0\nauth      include   system-auth\n'
                                              'account   include   system-auth\n')
            (t / 'usr/lib/security').mkdir(parents=True, exist_ok=True)
            (t / 'usr/lib/security/pam_fprintd.so').write_text('')
        if cmd[0] == 'xgenfstab':
            return 'UUID=r / xfs rw 0 1\nUUID=e /boot/efi vfat rw 0 2\nUUID=s none swap sw 0 0\n'
        if cmd[:2] == ['chroot', str(t)] and cmd[2] == 'xbps-reconfigure':
            (t / 'boot').mkdir(exist_ok=True)
            (t / 'boot/vmlinuz-7.3.1_1').write_text('k')
            (t / 'boot/initramfs-7.3.1_1.img').write_text('i')
        if cmd[:2] == ['chroot', str(t)] and cmd[2] == 'grub-install':
            (t / 'boot/efi/EFI/BOOT').mkdir(parents=True, exist_ok=True)
            (t / 'boot/efi/EFI/BOOT/BOOTX64.EFI').write_text('efi')
        if cmd[:2] == ['chroot', str(t)] and cmd[2] == 'grub-mkconfig':
            (t / 'boot/grub').mkdir(parents=True, exist_ok=True)
            (t / 'boot/grub/grub.cfg').write_text('linux /boot/vmlinuz-7.3.1_1 resume=UUID=SWAP-UUID\n')
        return '' if capture else None

    def test_install(self):
        inst.dialog = lambda *a, **k: 0
        version = inst.install(self.disk, 'pustota', 'stephen', 'secret', 'Europe/London', autologin=True)
        t = self.target
        self.assertEqual(version, '7.3.1_1')
        names = [c[0] if c[0] != 'chroot' else c[2] for c in self.ran]
        order = ['wipefs', 'sgdisk', 'mkfs.vfat', 'mkfs.xfs', 'mkswap', 'swapon', 'xbps-install',
                 'xgenfstab', 'useradd', 'chpasswd', 'xbps-reconfigure', 'grub-install', 'grub-mkconfig']
        positions = [names.index(step) for step in order]
        self.assertEqual(positions, sorted(positions), names)
        sgdisk = [c for c in self.ran if c[0] == 'sgdisk']
        self.assertIn(['sgdisk', '-n', '1:1MiB:+1GiB', '-t', '1:ef00', '-c', '1:EFI', self.disk], sgdisk)
        self.assertIn(['sgdisk', '-n', '2:0:+32GiB', '-t', '2:8200', '-c', '2:swap', self.disk], sgdisk)
        xbps = next(c for c in self.ran if c[0] == 'xbps-install')
        self.assertEqual(xbps[-4:], ['base-system', 'pustota-desktop', 'pustota-learn', 'pustota-russian'])
        self.assertIn('ignorepkg=linux', (t / 'etc/xbps.d/10-pustota-kernel.conf').read_text())
        self.assertFalse((t / 'etc/xbps.d/00-repository-main.conf').exists())   # default mirror worked
        self.assertEqual((t / 'var/db/xbps/keys/void.plist').read_text(), 'key')
        self.assertIn('/boot/efi', (t / 'etc/fstab').read_text())
        self.assertIn('\nru_RU.UTF-8 UTF-8', '\n' + (t / 'etc/default/libc-locales').read_text())
        self.assertIn('LANG=en_GB.UTF-8', (t / 'etc/locale.conf').read_text())
        self.assertIn('KEYMAP="uk"', (t / 'etc/rc.conf').read_text())
        ufw = (t / 'etc/ufw/ufw.conf').read_text()
        self.assertIn('ENABLED=yes', ufw)
        self.assertNotIn('ENABLED=no', ufw)
        self.assertTrue((t / 'etc/runit/runsvdir/default/ufw').is_symlink())
        pam = (t / 'etc/pam.d/sudo').read_text().splitlines()
        self.assertEqual(pam[1], 'auth      sufficient pam_fprintd.so')     # before the password
        self.assertEqual(pam[2], 'auth      include   system-auth')
        self.assertEqual(Path((t / 'etc/localtime').readlink()).as_posix(), '/usr/share/zoneinfo/Europe/London')
        enabled = t / 'etc/runit/runsvdir/default'
        self.assertEqual(sorted(p.name for p in enabled.iterdir()),
                         sorted(inst.SERVICES_REQUIRED + inst.SERVICES_OPTIONAL))      # dhcpcd gone
        self.assertIn('--autologin stephen', (t / 'etc/sv/agetty-tty1/conf').read_text())
        self.assertIn('resume=UUID=SWAP-UUID', (t / 'etc/default/grub').read_text())
        self.assertIn('nvme.noacpi=1', (t / 'etc/default/grub').read_text())
        self.assertTrue((t / 'etc/runit/runsvdir/default/snooze-weekly').is_symlink())   # weekly TRIM
        self.assertIn('suspend-then-hibernate',
                      (t / 'etc/elogind/logind.conf.d/60-pustota-hibernate.conf').read_text())
        useradd = next(c for c in self.ran if 'useradd' in c)
        self.assertIn('wheel,audio,video', useradd)              # only groups that exist
        self.assertNotIn('secret', ' '.join(' '.join(c) for c in self.ran))   # password only on stdin
        self.assertEqual((t / 'etc/sudoers.d/10-pustota-wheel').stat().st_mode & 0o777, 0o440)

    def test_another_mirror_is_written_into_the_new_system(self):
        inst.dialog = lambda *a, **k: 0
        saved = inst.MIRROR
        inst.MIRROR = 'https://repo-fi.voidlinux.org/current'
        try:
            inst.install(self.disk, 'pustota', 'u', 'pw', 'Europe/London', autologin=False)
        finally:
            inst.MIRROR = saved
        conf = (self.target / 'etc/xbps.d/00-repository-main.conf').read_text()
        self.assertIn('repository=https://repo-fi.voidlinux.org/current', conf)
        xbps = next(c for c in self.ran if c[0] == 'xbps-install')
        self.assertIn('https://repo-fi.voidlinux.org/current', xbps)
        self.assertIn('https://repo-fi.voidlinux.org/current/nonfree', xbps)   # intel-ucode
        self.assertIn('repository=https://repo-fi.voidlinux.org/current/nonfree',
                      (self.target / 'etc/xbps.d/10-repository-nonfree.conf').read_text())

    def test_missing_kernel_stops_the_install(self):
        original = self.fake_run
        def no_kernel(*cmd, **kw):
            result = original(*cmd, **kw)
            for f in (self.target / 'boot').glob('vmlinuz-*'):
                f.unlink()
            return result
        inst.run = no_kernel
        with self.assertRaisesRegex(RuntimeError, 'no 7.x kernel'):
            inst.install(self.disk, 'p', 'u', 'pw', 'Europe/London', autologin=False)


class Helpers(unittest.TestCase):
    def test_fingerprint_line_is_added_once(self):
        once = inst.with_fingerprint('#%PAM-1.0\nauth include system-auth\n')
        self.assertEqual(inst.with_fingerprint(once), once)
        self.assertEqual(once.count('pam_fprintd.so'), 1)

    def test_firewall_on(self):
        self.assertEqual(inst.firewall_on('ENABLED=no\nLOGLEVEL=low\n'), 'LOGLEVEL=low\nENABLED=yes\n')


class PersonalMusic(WholeInstall):
    """A personal ISO's music goes to the user's Music folder (Constellation's way)."""
    def test_music_is_copied_and_owned(self):
        music = self.target.parent / 'music'
        (music / 'Кино').mkdir(parents=True)
        (music / 'Кино' / 'Группа крови.flac').write_text('flac')
        saved = inst.MUSIC
        inst.MUSIC = music
        try:
            inst.dialog = lambda *a, **k: 0
            inst.install(self.disk, 'pustota', 'stephen', 'pw', 'Europe/London', autologin=False)
        finally:
            inst.MUSIC = saved
        self.assertIn(['cp', '-a', f'{music}/.', str(self.target / 'home/stephen/Music')], self.ran)
        self.assertIn(['chroot', str(self.target), 'chown', '-R', 'stephen:stephen', '/home/stephen/Music'],
                      self.ran)

    def test_no_music_no_copy(self):
        inst.dialog = lambda *a, **k: 0
        saved = inst.MUSIC
        inst.MUSIC = self.target.parent / 'nothing-here'
        try:
            inst.install(self.disk, 'pustota', 'stephen', 'pw', 'Europe/London', autologin=False)
        finally:
            inst.MUSIC = saved
        self.assertFalse(any('Music' in ' '.join(c) for c in self.ran))


class Steam32bit(WholeInstall):
    def test_each_32bit_library_is_tried_and_a_missing_one_is_skipped(self):
        self.fail_pkg = 'mesa-vulkan-intel-32bit'
        inst.dialog = lambda *a, **k: 0
        inst.install(self.disk, 'pustota', 'stephen', 'pw', 'Europe/London', autologin=False)
        tried = [c[-1] for c in self.ran if c[0] == 'xbps-install' and 'base-system' not in c]
        self.assertEqual(tried, inst.STEAM_32BIT)
        one = next(c for c in self.ran if c[0] == 'xbps-install' and c[-1] == 'libgcc-32bit')
        self.assertIn(inst.MIRROR + '/multilib', one)
        self.assertIn(inst.MIRROR + '/multilib/nonfree', one)
        log = inst.LOGFILE.read_text() if inst.LOGFILE.exists() else ''
        self.assertIn('mesa-vulkan-intel-32bit: not available, skipped', log)


class Progress(unittest.TestCase):
    """The installer streams each command's output (and an XBPS package count) to the screen."""
    def setUp(self):
        import tempfile
        self.tmp = Path(tempfile.mkdtemp())
        self.saved = inst.LOGFILE, inst.PROGRESS
        inst.LOGFILE = self.tmp / 'log'
        # a stand-in for dialog --progressbox: cat copies what it is shown into a file
        self.shown = self.tmp / 'shown'
        inst.PROGRESS = inst.sp.Popen(['sh', '-c', f'cat > {self.shown}'], stdin=inst.sp.PIPE,
                                      text=True, bufsize=1)

    def tearDown(self):
        inst.progress_close()
        inst.LOGFILE, inst.PROGRESS = self.saved

    def test_output_is_shown_live_and_logged(self):
        inst.run('sh', '-c', "printf '2 packages will be installed:\\na-1_1: unpacking ...\\r"
                             "b-2_1: unpacking ...\\nno newline at the end'")
        inst.progress_close()
        shown = self.shown.read_text()
        self.assertIn('$ sh -c', shown)                              # the command itself
        self.assertIn('[1 of 2 unpacked] a-1_1: unpacking ...', shown)
        self.assertIn('[2 of 2 unpacked] b-2_1: unpacking ...', shown)   # \r splits lines too
        self.assertIn('no newline at the end', shown)
        self.assertIn('b-2_1: unpacking', inst.LOGFILE.read_text())

    def test_input_is_passed_not_shown_and_failures_raise(self):
        inst.run('sh', '-c', 'read -r x; test -n "$x"', input_text='pw-hidden\n')
        with self.assertRaises(inst.sp.CalledProcessError):
            inst.run('sh', '-c', 'exit 3')
        inst.progress_close()
        self.assertNotIn('pw-hidden', self.shown.read_text())
        self.assertNotIn('pw-hidden', inst.LOGFILE.read_text())

    def test_steps_get_a_title(self):
        self.assertEqual(inst.STEP.match('2/6  Installing').group(1, 2), ('2', '6'))


class NoBlankScreen(unittest.TestCase):
    def test_infobox_is_never_cleared(self):
        seen = []
        saved = inst.sp.run
        inst.sp.run = lambda cmd, **k: seen.append(cmd) or inst.sp.CompletedProcess(cmd, 0, '')
        try:
            inst.dialog('--infobox', 'working', 9, 78)
            inst.dialog('--msgbox', 'done', 9, 78)
        finally:
            inst.sp.run = saved
        self.assertNotIn('--clear', seen[0])
        self.assertIn('--clear', seen[1])

