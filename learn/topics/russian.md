# Russian, A1 to B2

The Russian kit (pustota-russian, from Constellation) runs on this laptop, offline once the
material is downloaded. Super+r opens its menu.

    pustota-russian path         what to study at each level, with your word progress
    pustota-russian words        ten minutes of spaced repetition (10,000 words, A1-B2)
    pustota-russian tutor        the AI tutor, corrections explained in British English
    pustota-russian say ТЕКСТ    Piper reads Russian aloud (voices: irina, denis, dmitri, ruslan)
    pustota-russian listen       LibriVox audiobooks, A2-B2
    pustota-russian read mezhdunami | wiktionary | wikisource | wikipedia
    pustota-russian library      FSI, DLI and Peace Corps courses

## Downloading the material
    sudo pustota-content         choose packs: voices, the tutor, courses, dictionaries,
                                 reading, audiobooks (each checked against its checksum)
Everything goes to /var/lib/pustota/russian. Interrupted downloads resume.

## The tutor
Void does not package Ollama, so Pustota does: ollama-bin, its official release (pinned and
checked) built with xbps-src, with a "_ollama" user and a runit service (/etc/sv/ollama). The
tutor pack switches that service on and downloads the model: Qwen3.6 35B-A3B, about 24 GB. It is a
mixture-of-experts model: 35 billion parameters, of which only about 3 billion work on each
word, so it answers quickly on the CPU. The service lets the model go a minute after the last
answer, so it costs no memory or battery when you are not using it.
    sudo sv status ollama ; sudo sv down ollama

## The keyboard
Alt+Shift switches to Russian phonetic, where letters sit on their Latin look-alikes and
sound-alikes: я on q, в on w, е on e, ж on v. See the whole layout with:  setxkbmap -print -layout ru -variant phonetic

Dictionaries open through kiwix-serve, a small web server on this computer only, in Firefox.
