"""pustota-content against a fake installed system, a stub Ollama and a local web server."""
import functools
import hashlib
import http.server
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import unittest

PKG = Path(__file__).resolve().parents[1] / 'russian'
TOOL = PKG / 'pustota-content'


def stage(root: Path) -> None:
    """Lay the package out as its PKGBUILD's package() does."""
    lib, share = root / 'usr/lib/pustota/content', root / 'usr/share/pustota/russian'
    lib.mkdir(parents=True); share.mkdir(parents=True)
    for f in PKG.glob('fetch-*.py'):
        shutil.copy(f, lib)
    shutil.copy(PKG / 'mirror.json', lib)
    for f in ('vocab.tsv', 'library.tsv', 'audiobooks.tsv', 'voices.tsv'):
        shutil.copy(PKG / f, share)
    (root / 'var/lib/pustota/russian').mkdir(parents=True)


class ContentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.root = base / 'root'
        stage(self.root)
        self.data = self.root / 'var/lib/pustota/russian'
        (self.data / 'russian.json').write_text(json.dumps({'model': 'tutor'}))
        self.site = base / 'site'; self.site.mkdir()
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(self.site))
        handler.log_message = lambda *a: None
        httpd = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        self.addCleanup(httpd.server_close); self.addCleanup(httpd.shutdown)
        self.url = f'http://127.0.0.1:{httpd.server_port}'
        # Stub Ollama: remembers pulled tags in a file.
        self.ollama = base / 'ollama'
        self.ollama.write_text('#!/bin/sh\nS="$(dirname "$0")/pulled"\ncase "$1" in\n'
                               '  list) echo "NAME ID SIZE"; [ ! -f "$S" ] || sed "s/$/ x 1GB/" "$S" ;;\n'
                               '  pull) echo "$2" >> "$S" ;;\n  rm) grep -vx "$2" "$S" > "$S.n"; mv "$S.n" "$S" ;;\nesac\n')
        self.ollama.chmod(0o755)

    def publish_zim(self, directory, name, data=b'zim'):
        d = self.site / 'zim' / directory; d.mkdir(parents=True, exist_ok=True)
        (d / name).write_bytes(data)
        (d / f'{name}.sha256').write_text(f'{hashlib.sha256(data).hexdigest()}  {name}\n')
        listing = d / 'index.html'
        listing.write_text((listing.read_text() if listing.exists() else '') + f'<a href="{name}">{name}</a>\n')

    def run_tool(self, *args, input='', env=None):
        env = {**os.environ, 'PUSTOTA_CONTENT_ROOT': str(self.root),
               'PUSTOTA_CONTENT_OLLAMA': str(self.ollama),
               'PUSTOTA_CONTENT_KIWIX': self.url + '/zim', 'PUSTOTA_CONTENT_ARCHIVE': self.url + '/archive/',
               'PUSTOTA_CONTENT_MEZHDUNAMI': self.url + '/mn/index.shtml',
               'PUSTOTA_CONTENT_YTDLP': 'no-such-ytdlp',
               'PUSTOTA_CONTENT_MIRROR': self.url + '/no-mirror/', **(env or {})}
        return subprocess.run([sys_python(), str(TOOL), *args], capture_output=True, text=True, env=env, input=input)

    def config(self):
        return json.loads((self.data / 'russian.json').read_text())

    def test_tutor_model_goes_through_ollama(self):
        r = self.run_tool('install', 'ai-tutor')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('qwen3.6:35b-a3b', (self.ollama.parent / 'pulled').read_text())
        self.assertRegex(self.run_tool('list').stdout, r'ai-tutor\s+installed')
        self.run_tool('remove', 'ai-tutor')
        self.assertNotIn('qwen3', (self.ollama.parent / 'pulled').read_text())

    def test_dictionaries_are_verified_and_configured(self):
        self.publish_zim('wiktionary', 'wiktionary_en_all_nopic_2026-09.zim')
        self.publish_zim('wiktionary', 'wiktionary_ru_all_nopic_2026-08.zim')
        r = self.run_tool('install', 'ru-dictionaries')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        cfg = self.config()
        self.assertEqual(cfg['kiwix']['wiktionary'],
                         '/var/lib/pustota/russian/dictionary/wiktionary_en_all_nopic_2026-09.zim')
        self.assertEqual(cfg['kiwix']['wiktionary-ru'],
                         '/var/lib/pustota/russian/dictionary/wiktionary_ru_all_nopic_2026-08.zim')
        self.assertEqual(cfg['model'], 'tutor')                        # existing settings kept
        self.assertRegex(self.run_tool('list').stdout, r'ru-dictionaries\s+installed')
        self.run_tool('remove', 'ru-dictionaries')
        self.assertEqual(self.config()['kiwix'], {})

    def test_tampered_zim_refused(self):
        self.publish_zim('wikisource', 'wikisource_ru_all_nopic_2019-08.zim')
        self.publish_zim('wikipedia', 'wikipedia_ru_all_mini_2026-10.zim')
        (self.site / 'zim/wikipedia/wikipedia_ru_all_mini_2026-10.zim').write_bytes(b'tampered')
        r = self.run_tool('install', 'ru-reading')
        self.assertEqual(r.returncode, 1)
        self.assertIn('FAILED', r.stdout)
        self.assertNotIn('wikipedia', self.config()['kiwix'])
        self.assertIn('wikisource', self.config()['kiwix'])

    def test_interactive_choice_and_unknown_pack(self):
        r = self.run_tool(input='2\n')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('qwen3', (self.ollama.parent / 'pulled').read_text())
        self.assertEqual(self.run_tool('install', 'nonsense').returncode, 2)

    def test_packaged_files_exist(self):
        """build-packages.sh puts every kit file in the pustota-russian package."""
        build = (PKG.parent / 'build/build-packages.sh').read_text()
        for name in ('fetch-files.py', 'fetch-kiwix.py', 'fetch-archive.py', 'fetch-mezhdunami.py', 'fetch-mirror.py',
                     'library.tsv', 'audiobooks.tsv', 'voices.tsv', 'vocab.tsv', 'mirror.json', 'sv/ollama/run'):
            self.assertTrue((PKG / name).is_file(), name)
        for pattern in ('fetch-*.py', 'mirror.json', '{vocab,library,audiobooks,voices}.tsv', 'russian/sv',
                        'pustota-russian', 'pustota-content'):
            self.assertIn(pattern, build, pattern)

    @unittest.skipUnless(shutil.which('zstd'), 'needs zstd (Void and the builder have it)')
    def test_ollama_itself_is_downloaded_checked_and_given_a_service(self):
        """Void has no ollama package: the tutor pack fetches the pinned release first."""
        import tarfile, io
        stub = (b'#!/bin/sh\nS="$(dirname "$0")/pulled"\ncase "$1" in list) echo NAME; [ ! -f "$S" ] || cat "$S";;'
                b' pull) echo "$2" >> "$S";; esac\n')
        raw = io.BytesIO()
        with tarfile.open(fileobj=raw, mode='w') as tar:
            info = tarfile.TarInfo('bin/ollama'); info.size = len(stub); info.mode = 0o755
            tar.addfile(info, io.BytesIO(stub))
        archive = self.site / 'ollama-linux-amd64.tar.zst'
        archive.write_bytes(subprocess.run(['zstd', '-q', '-c'], input=raw.getvalue(), capture_output=True,
                                           check=True).stdout)
        shutil.copytree(PKG / 'sv', self.root / 'usr/lib/pustota/sv')
        binary = self.root / 'opt/ollama/bin/ollama'
        env = {'PUSTOTA_CONTENT_OLLAMA': str(binary),
               'PUSTOTA_CONTENT_OLLAMA_URL': self.url + '/ollama-linux-amd64.tar.zst'}
        # a wrong checksum is refused and nothing is unpacked
        bad = self.run_tool('install', 'ai-tutor', env={**env, 'PUSTOTA_CONTENT_OLLAMA_SHA256': '0' * 64})
        self.assertNotEqual(bad.returncode, 0)
        self.assertFalse(binary.exists())
        good = self.run_tool('install', 'ai-tutor', env={**env, 'PUSTOTA_CONTENT_OLLAMA_SHA256':
                                                       hashlib.sha256(archive.read_bytes()).hexdigest()})
        self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
        self.assertTrue(binary.is_file())
        self.assertIn('qwen3.6:35b-a3b', (binary.parent / 'pulled').read_text())
        self.assertTrue((self.root / 'etc/sv/ollama/run').is_file())
        self.assertEqual(os.readlink(self.root / 'var/service/ollama'), '/etc/sv/ollama')


def sys_python():
    import sys
    return sys.executable


if __name__ == '__main__':
    unittest.main()
