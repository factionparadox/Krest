"""The installer's pure helpers, and build/offline-items.py's reading of build logs and .drv files."""
import contextlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


inst = load('rassvet_install', ROOT / 'installer/rassvet-install.py')
items = load('offline_items', ROOT / 'build/offline-items.py')
GiB = 1024 ** 3


class InstallerHelpers(unittest.TestCase):
    def test_partition_names(self):
        self.assertEqual(inst.partition_path('/dev/nvme0n1', 1), '/dev/nvme0n1p1')
        self.assertEqual(inst.partition_path('/dev/mmcblk0', 2), '/dev/mmcblk0p2')
        self.assertEqual(inst.partition_path('/dev/sda', 3), '/dev/sda3')
        self.assertEqual(inst.partition_path('/dev/vda', 1), '/dev/vda1')

    def test_plan_swap_matches_ram(self):
        # the Framework: 1 TB disk, 32 GB RAM
        efi, swap, root = inst.plan(1000 * 10**9, 32 * GiB)
        self.assertEqual((efi, swap), (1, 32))
        self.assertEqual(efi + swap + root, 1000 * 10**9 // GiB)

    def test_plan_drops_swap_on_a_small_disk_and_refuses_a_tiny_one(self):
        self.assertEqual(inst.plan(48 * GiB, 32 * GiB), (1, 0, 47))
        self.assertEqual(inst.plan(48 * GiB, 4 * GiB), (1, 4, 43))     # the VM test
        with self.assertRaises(ValueError):
            inst.plan(30 * GiB, 4 * GiB)

    def test_scheme_strings_are_escaped(self):
        self.assertEqual(inst.scheme_string('plain'), '"plain"')
        self.assertEqual(inst.scheme_string('a"b\\c'), '"a\\"b\\\\c"')

    def test_config_scm(self):
        text = inst.config_scm('rassvet', 'stephen', '', 'Europe/London', True,
                               '1234-ABCD', '1111-2222', None)
        self.assertIn('(use-modules (rassvet system))', text)
        self.assertIn('#:user "stephen"', text)
        self.assertIn('#:autologin? #t', text)
        self.assertIn('#:swap-uuid #f', text)
        code = '\n'.join(line for line in text.splitlines() if not line.lstrip().startswith(';;'))
        self.assertEqual(code.count('('), code.count(')'))
        with_swap = inst.config_scm('h', 'u', '', 'UTC', False, 'e', 'r', 's-uuid')
        self.assertIn('#:swap-uuid "s-uuid"', with_swap)
        self.assertIn('#:autologin? #f', with_swap)

    def test_shadow_lines(self):
        lines = inst.shadow_lines([('root', '$6$x$y'), ('stephen', '$6$x$y')]).splitlines()
        self.assertEqual(len(lines), 2)
        fields = lines[1].split(':')
        self.assertEqual(fields[:2], ['stephen', '$6$x$y'])
        self.assertEqual(len(fields), 9)


DRV = ('Derive([("out","/gnu/store/aaa-grub.cfg","","")],'
       '[("/gnu/store/bbb-grub-2.14.drv",["out"]),("/gnu/store/ccc-glibc.drv",["out","static"])],'
       '["/gnu/store/ddd-builder.scm","/gnu/store/eee-module-import"],'
       '"x86_64-linux","/gnu/store/fff-guile/bin/guile",["--no-auto-compile"],[("out","/gnu/store/aaa-grub.cfg")])')
DEP = 'Derive([("out","/gnu/store/ggg-glibc","",""),("static","/gnu/store/hhh-glibc-static","","")],[],[],"x86_64-linux","b",[],[])'


class OfflineItems(unittest.TestCase):
    def test_reads_a_dry_run(self):
        log = ('The following derivations would be built:\n'
               '  /gnu/store/abc-grub.cfg.drv\n  /gnu/store/def-system.drv\n'
               '822 items would be downloaded\n')
        self.assertEqual(items.drvs_to_build(log), ['/gnu/store/abc-grub.cfg.drv', '/gnu/store/def-system.drv'])
        self.assertEqual(items.downloads(log), 822)
        self.assertEqual(items.downloads('The following derivations would be built:\n'), 0)

    def test_reads_a_build_log(self):
        log = ('building /gnu/store/abc-etc.drv...\nbuilding /gnu/store/abc-etc.drv...\n'
               'building profile with 66 packages...\n')
        self.assertEqual(items.drvs_to_build(log), ['/gnu/store/abc-etc.drv'])

    def test_items_need_the_inputs_of_what_the_laptop_builds(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp)
            cfg, grub, glibc = store / 'cfg.drv', store / 'grub.drv', store / 'glibc.drv'
            cfg.write_text(DRV.replace('/gnu/store/bbb-grub-2.14.drv', str(grub)).replace('/gnu/store/ccc-glibc.drv', str(glibc)))
            grub.write_text('Derive([("out","/gnu/store/iii-grub","","")],[],[],"x86_64-linux","b",[],[])')
            glibc.write_text(DEP)
            tlog, vlog = store / 't.log', store / 'v.log'
            tlog.write_text(f'The following derivations would be built:\n  {grub}\n'
                            '5.8 MB would be downloaded:\n  /gnu/store/jjj-grub-efi-2.14\n')
            vlog.write_text(f'The following derivations would be built:\n  {cfg}\n')
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                items.main(['x', 'items', '/gnu/store/sys-system', str(tlog), str(vlog)])
            got = set(out.getvalue().split())
        self.assertEqual(got, {'/gnu/store/sys-system', '/gnu/store/iii-grub', '/gnu/store/jjj-grub-efi-2.14',
                               '/gnu/store/ggg-glibc',
                               '/gnu/store/hhh-glibc-static', '/gnu/store/ddd-builder.scm',
                               '/gnu/store/eee-module-import'})

    def test_refuses_when_the_laptop_would_download(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / 'v.log'
            log.write_text('The following derivations would be built:\n  /gnu/store/x.drv\n3 items would be downloaded\n')
            with self.assertRaises(SystemExit):
                items.main(['x', 'items', 's', str(log), str(log)])

    def test_parses_a_derivation(self):
        with tempfile.TemporaryDirectory() as tmp:
            drv = Path(tmp) / 'x.drv'
            drv.write_text(DRV)
            outputs, inputs, sources = items.parse_drv(drv)
        self.assertEqual(outputs, {'out': '/gnu/store/aaa-grub.cfg'})
        self.assertEqual(inputs, [('/gnu/store/bbb-grub-2.14.drv', ['out']),
                                  ('/gnu/store/ccc-glibc.drv', ['out', 'static'])])
        self.assertEqual(sources, ['/gnu/store/ddd-builder.scm', '/gnu/store/eee-module-import'])

    def test_dependency_outputs_by_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            dep = Path(tmp) / 'dep.drv'
            dep.write_text(DEP)
            self.assertEqual(items.outputs_of(dep), {'out': '/gnu/store/ggg-glibc',
                                                     'static': '/gnu/store/hhh-glibc-static'})


if __name__ == '__main__':
    unittest.main()
