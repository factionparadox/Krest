"""rassvet-content against a fake installed system, a stub tutor service and a local web server
(standing in for Kiwix, the Internet Archive and Hugging Face)."""
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
TOOL = PKG / 'rassvet-content'


def stage(root: Path) -> None:
    """Lay the package out as guix/rassvet/packages.scm's install plan does."""
    lib, share = root / 'usr/lib/rassvet/content', root / 'usr/share/rassvet/russian'
    lib.mkdir(parents=True); share.mkdir(parents=True)
    for f in PKG.glob('fetch-*.py'):
        shutil.copy(f, lib)
    shutil.copy(PKG / 'mirror.json', lib)
    for f in ('vocab.tsv', 'library.tsv', 'audiobooks.tsv', 'voices.tsv'):
        shutil.copy(PKG / f, share)
    (root / 'var/lib/rassvet/russian').mkdir(parents=True)


class ContentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.root = base / 'root'
        stage(self.root)
        self.data = self.root / 'var/lib/rassvet/russian'
        (self.data / 'russian.json').write_text(json.dumps({'model': 'tutor'}))
        self.site = base / 'site'; self.site.mkdir()
        site = self.site

        class Handler(http.server.SimpleHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def end_headers(self):
                # Hugging Face's large files: their SHA-256 and size in the headers
                if self.path.startswith('/hf/'):
                    f = site / self.path.lstrip('/')
                    if f.is_file():
                        data = f.read_bytes()
                        self.send_header('X-Linked-Etag', f'"{hashlib.sha256(data).hexdigest()}"')
                        self.send_header('X-Linked-Size', str(len(data)))
                super().end_headers()
        handler = functools.partial(Handler, directory=str(self.site))
        httpd = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        self.addCleanup(httpd.server_close); self.addCleanup(httpd.shutdown)
        self.url = f'http://127.0.0.1:{httpd.server_port}'
        # Stub /etc/rc.d/rassvet-tutor: records what it was asked
        self.herd = base / 'herd'
        self.herd.write_text('#!/bin/sh\necho "$@" >> "$(dirname "$0")/herd-args"\n')
        self.herd.chmod(0o755)
        # the tutor's model on the stand-in Hugging Face
        model = self.site / 'hf/unsloth/Qwen3.6-35B-A3B-GGUF/resolve/main'
        model.mkdir(parents=True)
        (model / 'Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf').write_bytes(b'GGUF' + b'x' * 5000)

    def publish_zim(self, directory, name, data=b'zim'):
        d = self.site / 'zim' / directory; d.mkdir(parents=True, exist_ok=True)
        (d / name).write_bytes(data)
        (d / f'{name}.sha256').write_text(f'{hashlib.sha256(data).hexdigest()}  {name}\n')
        listing = d / 'index.html'
        listing.write_text((listing.read_text() if listing.exists() else '') + f'<a href="{name}">{name}</a>\n')

    def run_tool(self, *args, input='', env=None):
        env = {**os.environ, 'RASSVET_CONTENT_ROOT': str(self.root),
               'RASSVET_CONTENT_LIB': str(self.root / 'usr/lib/rassvet/content'),
               'RASSVET_CONTENT_SHARE': str(self.root / 'usr/share/rassvet/russian'),
               'RASSVET_CONTENT_TUTOR_RC': str(self.herd), 'RASSVET_CONTENT_FREE_GB': '500', 'RASSVET_CONTENT_HF': self.url + '/hf',
               'RASSVET_CONTENT_KIWIX': self.url + '/zim', 'RASSVET_CONTENT_ARCHIVE': self.url + '/archive/',
               'RASSVET_CONTENT_MEZHDUNAMI': self.url + '/mn/index.shtml',
               'RASSVET_CONTENT_YTDLP': 'no-such-ytdlp',
               'RASSVET_CONTENT_MIRROR': self.url + '/no-mirror/', **(env or {})}
        return subprocess.run([sys_python(), str(TOOL), *args], capture_output=True, text=True, env=env, input=input)

    def config(self):
        return json.loads((self.data / 'russian.json').read_text())

    def herd_args(self):
        f = self.herd.parent / 'herd-args'
        return f.read_text() if f.exists() else ''

    def test_tutor_model_is_verified_and_its_service_started(self):
        r = self.run_tool('install', 'ai-tutor')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        tutor = self.data / 'tutor'
        self.assertEqual(os.readlink(tutor / 'tutor.gguf'), 'Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf')
        self.assertTrue((tutor / 'tutor.gguf').read_bytes().startswith(b'GGUF'))
        self.assertIn('start', self.herd_args().split())
        self.assertRegex(self.run_tool('list').stdout, r'ai-tutor\s+installed')
        self.run_tool('remove', 'ai-tutor')
        self.assertEqual(list(tutor.iterdir()), [])
        self.assertIn('stop', self.herd_args().split())

    def test_tampered_model_refused(self):
        model = self.site / 'hf/unsloth/Qwen3.6-35B-A3B-GGUF/resolve/main/Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf'
        # the headers describe one file, a different one arrives
        site_bytes = model.read_bytes()
        r = self.run_tool('install', 'ai-tutor')                     # good copy first
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        (self.data / 'tutor/Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf').write_bytes(site_bytes[:-1] + b'!')
        r = self.run_tool('install', 'ai-tutor')                     # changed on disk: fetched again
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual((self.data / 'tutor/tutor.gguf').read_bytes(), site_bytes)

    def test_dictionaries_are_verified_and_configured(self):
        self.publish_zim('wiktionary', 'wiktionary_en_all_nopic_2026-09.zim')
        self.publish_zim('wiktionary', 'wiktionary_ru_all_nopic_2026-08.zim')
        r = self.run_tool('install', 'ru-dictionaries')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        cfg = self.config()
        self.assertEqual(cfg['kiwix']['wiktionary'],
                         '/var/lib/rassvet/russian/dictionary/wiktionary_en_all_nopic_2026-09.zim')
        self.assertEqual(cfg['kiwix']['wiktionary-ru'],
                         '/var/lib/rassvet/russian/dictionary/wiktionary_ru_all_nopic_2026-08.zim')
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
        self.assertTrue((self.data / 'tutor/tutor.gguf').is_file())
        self.assertEqual(self.run_tool('install', 'nonsense').returncode, 2)

    def test_packaged_files_exist(self):
        """ports/rassvet-russian/Pkgfile installs every kit file."""
        recipe = (PKG.parent / 'ports/rassvet-russian/Pkgfile').read_text()
        for name in ('fetch-files.py', 'fetch-kiwix.py', 'fetch-archive.py', 'fetch-mezhdunami.py',
                     'fetch-mirror.py', 'fetch-hf.py', 'library.tsv', 'audiobooks.tsv', 'voices.tsv',
                     'vocab.tsv', 'mirror.json'):
            self.assertTrue((PKG / name).is_file(), name)
        for pattern in ('rassvet-russian $PKG/usr/bin/', 'rassvet-content $PKG/usr/bin/',
                        'fetch-*.py mirror.json $PKG/usr/lib/rassvet/content/',
                        '*.tsv VOCAB-SOURCES.md $PKG/usr/share/rassvet/russian/'):
            self.assertIn(pattern, recipe, pattern)


def sys_python():
    import sys
    return sys.executable


if __name__ == '__main__':
    unittest.main()
