# Russian, A1 to B2

From Constellation (and Kirin before it). `krest-russian path` lays out the route; everything runs offline once downloaded. Ctrl+Super+r opens these as a menu.

| Command | |
| --- | --- |
| `krest-russian path` | what to study at each level, with your word progress |
| `krest-russian words [--level A1..B2] [--new N] [--reverse] [--say] [--stats]` | 10,000 words banded A1-B2, spaced repetition (Leitner boxes); progress in `~/.local/share/krest/russian-words.json` |
| `krest-russian tutor [TEXT] [--level A1..C2]` | the AI tutor, Qwen3.6 35B-A3B through llama.cpp on this computer; corrections explained in British English; `/say`, `/level`, `/quit` |
| `krest-russian say TEXT [--voice irina\|denis\|dmitri\|ruslan]` | Piper speech |
| `krest-russian listen [--level A2\|B1\|B2] [--play N \| --pick]` | 29 LibriVox audiobooks |
| `krest-russian read mezhdunami\|wikisource\|wikipedia\|wiktionary-ru\|wiktionary` | the textbook (in Firefox) and Kiwix (kiwix-serve on 127.0.0.1, in Firefox) |
| `krest-russian library [--open]` | the FSI, DLI and Peace Corps courses |

## Downloads: `sudo krest-content`

| Pack | Size | From | Checked against |
| --- | --- | --- | --- |
| `ru-voices` | 0.25 GB | content mirror, else Hugging Face | mirror checksums, else hashes pinned on first download |
| `ai-tutor` | 22.4 GB | the GGUF model (unsloth/Qwen3.6-35B-A3B-GGUF, UD-Q4_K_XL) from Hugging Face | the SHA-256 Hugging Face publishes for it |
| `ru-course` | 1.2 GB | content mirror, else the original sites; Между нами from mezhdunami.org | mirror checksums, else pinned hashes |
| `ru-dictionaries` | ~9 GB | Kiwix | Kiwix's SHA-256 |
| `ru-reading` | ~6 GB | Kiwix | Kiwix's SHA-256 |
| `ru-audiobooks` | ~5 GB | content mirror, else the Internet Archive | mirror checksums, else the Archive's MD5 and SHA-1 |

Downloads go to `/var/lib/krest/russian`, the model to `/var/lib/krest/russian/tutor`. llama.cpp's server runs it as the service `/etc/rc.d/krest-tutor` (as `nobody`, listening on 127.0.0.1 only, log in `/var/log/krest-tutor.log`); it starts once the model is downloaded and at every boot after (it is in `SERVICES` in `/etc/rc.conf`), and `sudo krest-content remove ai-tutor` stops it and deletes the model. Interrupted downloads resume.

*Между нами* (University of Kansas) is CC BY-NC-ND: it is copied for your personal use on your own computer and never mirrored. The course library is US government work (public domain), the audiobooks are LibriVox (public domain), the voices are MIT, and the word list is CC BY-SA 4.0 (`VOCAB-SOURCES.md`).

The content mirror is the GitHub release `content-v1` on factionparadox/Kirin. To move it here, download the packs on a Krest machine and run `build/publish-content.sh`, then commit the new `russian/mirror.json`.

Reaching B2 takes roughly 900-1,200 hours for an English speaker. Krest covers courses, words, listening, reading and practice with an AI; real conversation (a class, a language exchange) is the part it cannot give you.
