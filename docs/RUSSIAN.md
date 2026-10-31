# Russian, A1 to B2

From Constellation (and Kirin before it). `pustota-russian path` lays out the route; everything runs offline once downloaded. Super+r opens these as a menu.

| Command | |
| --- | --- |
| `pustota-russian path` | what to study at each level, with your word progress |
| `pustota-russian words [--level A1..B2] [--new N] [--reverse] [--say] [--stats]` | 10,000 words banded A1-B2, spaced repetition (Leitner boxes); progress in `~/.local/share/pustota/russian-words.json` |
| `pustota-russian tutor [TEXT] [--level A1..C2]` | the AI tutor, Qwen3.6 35B-A3B through Ollama on this computer; corrections explained in British English; `/say`, `/level`, `/quit` |
| `pustota-russian say TEXT [--voice irina\|denis\|dmitri\|ruslan]` | Piper speech |
| `pustota-russian listen [--level A2\|B1\|B2] [--play N \| --pick]` | 29 LibriVox audiobooks |
| `pustota-russian read mezhdunami\|wikisource\|wikipedia\|wiktionary-ru\|wiktionary` | the textbook (in Firefox) and Kiwix (kiwix-serve on 127.0.0.1, in Firefox) |
| `pustota-russian library [--open]` | the FSI, DLI and Peace Corps courses |

## Downloads: `sudo pustota-content`

| Pack | Size | From | Checked against |
| --- | --- | --- | --- |
| `ru-voices` | 0.25 GB | content mirror, else Hugging Face | mirror checksums, else hashes pinned on first download |
| `ai-tutor` | about 24 GB | Ollama v0.40.13 from GitHub, then the model from the Ollama registry | the release's pinned SHA-256, then Ollama's blob digests |
| `ru-course` | 1.2 GB | content mirror, else the original sites; Между нами from mezhdunami.org | mirror checksums, else pinned hashes |
| `ru-dictionaries` | ~9 GB | Kiwix | Kiwix's SHA-256 |
| `ru-reading` | ~6 GB | Kiwix | Kiwix's SHA-256 |
| `ru-audiobooks` | ~5 GB | content mirror, else the Internet Archive | mirror checksums, else the Archive's MD5 and SHA-1 |

Downloads go to `/var/lib/pustota/russian`, Ollama to `/opt/ollama` and the model to `/var/lib/ollama` (Ollama runs as the `ollama` user under runit: `/etc/sv/ollama`, unloading the model a minute after its last answer). Interrupted downloads resume.

*Между нами* (University of Kansas) is CC BY-NC-ND: it is copied for your personal use on your own computer and never mirrored. The course library is US government work (public domain), the audiobooks are LibriVox (public domain), the voices are MIT, and the word list is CC BY-SA 4.0 (`VOCAB-SOURCES.md`).

The content mirror is the GitHub release `content-v1` on factionparadox/Kirin. To move it here, download the packs on a Pustota machine and run `build/publish-content.sh`, then commit the new `russian/mirror.json`.

Reaching B2 takes roughly 900-1,200 hours for an English speaker. Pustota covers courses, words, listening, reading and practice with an AI; real conversation (a class, a language exchange) is the part it cannot give you.
