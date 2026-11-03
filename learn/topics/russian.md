# Russian, A1 to B2

The Russian kit (rassvet-russian, from Constellation) runs on this laptop, offline once the
material is downloaded. Ctrl+Super+r opens its menu.

    rassvet-russian path         what to study at each level, with your word progress
    rassvet-russian words        ten minutes of spaced repetition (10,000 words, A1-B2)
    rassvet-russian tutor        the AI tutor, corrections explained in British English
    rassvet-russian say ТЕКСТ    Piper reads Russian aloud (voices: irina, denis, dmitri, ruslan)
    rassvet-russian listen       LibriVox audiobooks, A2-B2
    rassvet-russian read mezhdunami | wiktionary | wikisource | wikipedia
    rassvet-russian library      FSI, DLI and Peace Corps courses

## Downloading the material
    sudo rassvet-content         choose packs: voices, the tutor, courses, dictionaries,
                                 reading, audiobooks (each checked against its checksum)
Everything goes to /var/lib/rassvet/russian. Interrupted downloads resume.

## The tutor
The engine is llama.cpp's llama-server (Rassvet's llama-cpp port, built here for this
processor), run by /etc/rc.d/rassvet-tutor, a service in /etc/rc.conf: as the user nobody,
listening on 127.0.0.1:11434 only, logging to /var/log/rassvet-tutor.log. At boot it starts
only once the model is on disk.
    sudo rassvet-content install ai-tutor
downloads the model from Hugging Face, Qwen3.6 35B-A3B (about 24 GB, a GGUF file), checks it
against the SHA-256 Hugging Face publishes, and starts the service. It is a mixture-of-experts
model: 35 billion parameters, of which only about 3 billion work on each word, so it answers
quickly on the CPU. While the service runs the model stays in memory; stop it when you need
the memory back.
    sudo /etc/rc.d/rassvet-tutor status ; sudo /etc/rc.d/rassvet-tutor stop ; ... start

## The keyboard
Alt+Shift switches to Russian phonetic, where letters sit on their Latin look-alikes and
sound-alikes: я on q, в on w, е on e, ж on v. See the whole layout with:  setxkbmap -print -layout ru -variant phonetic

Dictionaries open through kiwix-serve (the kiwix-tools port), a small web server on this computer only
(127.0.0.1), in Firefox.
