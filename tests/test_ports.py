"""Krest's CRUX ports: every Pkgfile is complete, every source has a checksum line, local
files exist, and build/krest-ports makes the collection."""
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PORTS = ROOT / 'ports'
OWN = {'krest', 'krest-desktop', 'krest-learn', 'krest-russian'}
HEX = re.compile(r'^[0-9a-f]{64}$')


def sources(port):
    out = subprocess.run(['bash', '-c', '. ./Pkgfile; for s in "${source[@]}"; do echo "$s"; done'],
                         cwd=PORTS / port, capture_output=True, text=True, check=True).stdout
    return out.split()


class Pkgfiles(unittest.TestCase):
    def test_every_port_is_complete(self):
        for port in sorted(p.name for p in PORTS.iterdir()):
            text = (PORTS / port / 'Pkgfile').read_text()
            for line in ('# Description:', '# Maintainer:', f'name={port}\n', 'version=', 'release=', 'build()'):
                self.assertIn(line, text, f'{port}: {line}')
            r = subprocess.run(['bash', '-n', 'Pkgfile'], cwd=PORTS / port, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, f'{port}: {r.stderr}')

    def test_every_source_is_checked(self):
        for port in sorted(p.name for p in PORTS.iterdir() if p.name not in OWN):
            listed = {}
            for line in (PORTS / port / 'sha256').read_text().splitlines():
                want, name = line.split()
                self.assertTrue(want == '-' or HEX.match(want), f'{port}: {line}')
                listed[name] = want
            names = [s.rsplit('/', 1)[-1] for s in sources(port)]
            self.assertEqual(sorted(names), sorted(listed), port)
            # files shipped in the port itself are pinned, never trusted on first use
            for src in sources(port):
                if '://' not in src:
                    self.assertTrue((PORTS / port / src).is_file(), f'{port}: {src}')
                    self.assertNotEqual(listed[src], '-', f'{port}: {src}')
                    import hashlib
                    got = hashlib.sha256((PORTS / port / src).read_bytes()).hexdigest()
                    self.assertEqual(listed[src], got, f'{port}: {src} changed; update its sha256 line')

    def test_the_whole_system_depends_on_krests_own_ports(self):
        deps = re.search(r'^# Depends on:(.*)$', (PORTS / 'krest/Pkgfile').read_text(), re.M).group(1).split()
        for port in ('linux', 'ly', 'krest-desktop', 'krest-learn', 'krest-russian', 'webcord',
                     'freetube', 'proton-vpn-gtk-app', 'steam', 'firefox', 'networkmanager'):
            self.assertIn(port, deps)

    def test_kernel_config_changes_apply(self):
        frag = (PORTS / 'linux/krest.config').read_text()
        self.assertIn('CONFIG_XFS_FS=y', frag)
        self.assertIn('CONFIG_BLK_DEV_NVME=y', frag)
        self.assertIn('# CONFIG_DEBUG_INFO_BTF is not set', frag)


class Sync(unittest.TestCase):
    def test_sync_makes_the_collection(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / 'krest'
            r = subprocess.run(['sh', str(ROOT / 'build/krest-ports'), 'sync', str(ROOT), str(dest)],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            version = (ROOT / 'VERSION').read_text().strip()
            for port in ('krest-desktop', 'krest-learn', 'krest-russian'):
                tarball = dest / port / f'{port}-{version}.tar.gz'
                self.assertTrue(tarball.is_file(), port)
                pkgfile = (dest / port / 'Pkgfile').read_text()
                self.assertIn(f'version={version}', pkgfile)
                self.assertRegex(pkgfile, r'release=\d+')
                self.assertIn(tarball.name, (dest / port / 'sha256').read_text())
            listing = subprocess.run(['tar', 'tzf', str(dest / 'krest-desktop' / f'krest-desktop-{version}.tar.gz')],
                                     capture_output=True, text=True).stdout
            self.assertIn('root/usr/bin/krest-session', listing)
            # the same input makes the same tarball (so its checksum means something)
            first = (dest / 'krest-learn/sha256').read_text()
            subprocess.run(['sh', str(ROOT / 'build/krest-ports'), 'sync', str(ROOT), str(dest)],
                           capture_output=True, check=True)
            self.assertEqual(first, (dest / 'krest-learn/sha256').read_text())


class Installer(unittest.TestCase):
    def test_scripts_parse(self):
        for script in ('installer/krest-install', 'build/build-iso.sh'):
            r = subprocess.run(['bash', '-n', str(ROOT / script)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, f'{script}: {r.stderr}')
        for script in ('build/krest-ports', 'installer/iso-binaries'):
            r = subprocess.run(['sh', '-n', str(ROOT / script)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, f'{script}: {r.stderr}')

    def test_partition_names(self):
        fn = re.search(r'^part\(\) \{.*\}', (ROOT / 'installer/krest-install').read_text(), re.M).group(0)
        for disk, n, want in (('/dev/nvme0n1', 1, '/dev/nvme0n1p1'), ('/dev/sda', 3, '/dev/sda3'),
                              ('/dev/mmcblk0', 2, '/dev/mmcblk0p2')):
            out = subprocess.run(['bash', '-c', f'{fn}; part {disk} {n}'], capture_output=True, text=True).stdout.strip()
            self.assertEqual(out, want)

    def test_services_have_rc_scripts(self):
        """every service the installer switches on comes from a port Krest installs."""
        text = (ROOT / 'installer/krest-install').read_text()
        services = re.search(r'^SERVICES="(.*)"', text, re.M).group(1).split()
        own = {p.name for p in (ROOT / 'desktop/root/etc/rc.d').iterdir()}
        ported = {'acpid', 'tlp', 'thermald'}
        crux = {'lo', 'crond', 'dbus', 'networkmanager', 'bluetoothd', 'chronyd'}
        for s in services:
            self.assertIn(s, own | ported | crux, s)
        for s in ported:
            self.assertIn(f'$PKG/etc/rc.d/{s}', (PORTS / s / 'Pkgfile').read_text())


if __name__ == '__main__':
    unittest.main()


class Verify(unittest.TestCase):
    """krest-ports verify, with a stand-in pkgmk (the sources are already in the port)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.bin = base / 'bin'; self.bin.mkdir()
        (self.bin / 'pkgmk').write_text('#!/bin/sh\n[ "$1" = -um ] && echo md5 > .md5sum\nexit 0\n')
        (self.bin / 'pkgmk').chmod(0o755)
        self.dest = base / 'ports'
        port = self.dest / 'demo'; port.mkdir(parents=True)
        (port / 'Pkgfile').write_text('name=demo\nversion=1\nrelease=1\nsource=(a.txt b.tar.gz)\nbuild() { :; }\n')
        (port / 'a.txt').write_text('pinned')
        (port / 'b.tar.gz').write_text('first')
        import hashlib
        pinned = hashlib.sha256(b'pinned').hexdigest()
        (port / 'sha256').write_text(f'{pinned}  a.txt\n-  b.tar.gz\n')
        self.port, self.lock = port, base / 'lock'

    def verify(self):
        import os
        env = {**os.environ, 'PATH': f'{self.bin}:{os.environ["PATH"]}', 'KREST_SOURCES_LOCK': str(self.lock)}
        return subprocess.run(['sh', str(ROOT / 'build/krest-ports'), 'verify', str(self.dest)],
                              capture_output=True, text=True, env=env)

    def test_pinned_and_first_use(self):
        r = self.verify()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('demo/b.tar.gz', self.lock.read_text())         # recorded on first use
        self.assertTrue((self.port / '.md5sum').exists())
        self.assertEqual(self.verify().returncode, 0)                   # same file again: fine

    def test_changed_sources_refused(self):
        self.assertEqual(self.verify().returncode, 0)
        (self.port / 'b.tar.gz').write_text('changed upstream')       # differs from the record
        r = self.verify()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('DOES NOT MATCH', r.stderr)
        (self.port / 'b.tar.gz').write_text('first')
        (self.port / 'a.txt').write_text('tampered')                    # differs from the pin
        self.assertNotEqual(self.verify().returncode, 0)
