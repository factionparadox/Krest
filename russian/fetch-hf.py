#!/usr/bin/env python3
"""Download one file from Hugging Face, checked against the SHA-256 Hugging Face publishes.

Hugging Face answers a HEAD request for a large (LFS) file with X-Linked-Etag (the file's
SHA-256) and X-Linked-Size. The download resumes from FILE.part after an interruption, shows
its progress, and is renamed into place only when the whole file matches the hash.

    fetch-hf.py --repo OWNER/NAME --file NAME.gguf --dest DIR [--base URL]
Exit: 0 done (or already there and verified), 1 the download or the check failed.
"""
from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import sys
import time
from urllib import error, request

CHUNK = 1 << 20
USER_AGENT = 'krest/1 (+https://github.com/factionparadox/Pustota)'


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def published(url: str) -> tuple[str, int]:
    """(sha256, size) from Hugging Face's headers for url."""
    opener = request.build_opener(NoRedirect)
    req = request.Request(url, method='HEAD', headers={'User-Agent': USER_AGENT})
    try:
        response = opener.open(req, timeout=60)
        headers = response.headers
    except error.HTTPError as exc:          # the 302 to the CDN carries the headers too
        if exc.code not in (301, 302, 303, 307, 308):
            raise
        headers = exc.headers
    sha = (headers.get('X-Linked-Etag') or headers.get('ETag') or '').strip().strip('"').lower()
    size = headers.get('X-Linked-Size') or headers.get('Content-Length') or ''
    if len(sha) != 64 or not all(c in '0123456789abcdef' for c in sha):
        raise OSError(f'Hugging Face gave no SHA-256 for {url}')
    if not size.isdigit():
        raise OSError(f'Hugging Face gave no size for {url}')
    return sha, int(size)


def sha256_file(path: Path) -> str:
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def show(done: int, total: int) -> None:
    sys.stdout.write(f'\r    [{done * 100 // max(total, 1):3d}%] {done / 2**30:6.1f} of {total / 2**30:.1f} GiB')
    sys.stdout.flush()


def download(url: str, part: Path, total: int, attempts: int = 5) -> None:
    for attempt in range(1, attempts + 1):
        have = part.stat().st_size if part.exists() else 0
        if have >= total:
            return
        headers = {'User-Agent': USER_AGENT, 'Range': f'bytes={have}-'}
        try:
            with request.urlopen(request.Request(url, headers=headers), timeout=60) as response:
                mode = 'ab' if response.status == 206 else 'wb'
                done = have if mode == 'ab' else 0
                last = 0.0
                with part.open(mode) as out:
                    while chunk := response.read(CHUNK):
                        out.write(chunk)
                        done += len(chunk)
                        if time.monotonic() - last > 1:
                            show(done, total)
                            last = time.monotonic()
                show(done, total)
                print()
            if part.stat().st_size >= total:
                return
        except OSError as exc:
            print(f'\n    interrupted ({exc}); resuming', file=sys.stderr)
        if attempt < attempts:
            time.sleep(3 * attempt)
    raise OSError('the download did not finish (run it again to resume)')


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--repo', required=True)
    ap.add_argument('--file', required=True)
    ap.add_argument('--dest', type=Path, required=True)
    ap.add_argument('--base', default='https://huggingface.co')
    args = ap.parse_args(argv)
    url = f'{args.base.rstrip("/")}/{args.repo}/resolve/main/{args.file}'
    target = args.dest / args.file.rsplit('/', 1)[-1]     # the file itself, without the repo's folders
    part = target.with_name(target.name + '.part')
    try:
        sha, size = published(url)
        print(f'    {args.repo}/{args.file}: {size / 2**30:.1f} GiB, SHA-256 {sha[:16]}…')
        if target.is_file() and target.stat().st_size == size and sha256_file(target) == sha:
            print('    already here and verified')
            return 0
        args.dest.mkdir(parents=True, exist_ok=True)
        download(url, part, size)
        print('    checking the SHA-256 …')
        if part.stat().st_size != size or sha256_file(part) != sha:
            part.unlink(missing_ok=True)
            print('    the file did not match Hugging Face\'s SHA-256: deleted; run it again', file=sys.stderr)
            return 1
        os.replace(part, target)
        print('    verified')
        return 0
    except OSError as exc:
        print(f'    FETCH FAILED: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
