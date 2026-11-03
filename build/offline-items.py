#!/usr/bin/env python3
"""What the USB stick must carry so that guix system init works offline.

The installed system is the template system's packages plus a few small files personal to each
laptop (accounts, /etc, the initrd and GRUB menu with its UUIDs). guix system init also needs
GRUB itself and what it builds GRUB's menu with, which guix system build never touches. So the
build asks guix system init itself, as a dry run (guix system init -n), what it would build:

    offline-items.py drvs INIT-LOG
        the derivations a dry run would build (build-iso.sh builds them for the template, so
        that GRUB, its keymap and the bootloader installer are in the store)
    offline-items.py items TEMPLATE-SYSTEM TEMPLATE-INIT-LOG VARIANT-INIT-LOG
        the store items to export: the template system, the outputs of what its install
        built and what it downloaded, and the inputs of every derivation a second, differently answered install
        would still build (those are the laptop's personal files: built on the laptop,
        offline, from these inputs)

build/build-iso.sh exports the closure of `items` (guix gc -R) into rassvet/system.nar.zst.
"""
import re
import sys
from pathlib import Path

OUTPUT = re.compile(r'\("([^"]+)","(/gnu/store/[^"]+)","[^"]*","[^"]*"\)')
DRV_LINE = re.compile(r"^\s+(/\S+\.drv)\s*$")


def drvs_to_build(log):
    """The .drv paths a log lists: under "would be built" (a dry run), or "building X.drv..."."""
    found, listing = set(), False
    for line in log.splitlines():
        if "would be built:" in line or "will be built:" in line:
            listing = True
            continue
        match = DRV_LINE.match(line) if listing else None
        if match:
            found.add(match.group(1))
            continue
        listing = False
        found.update(re.findall(r"building (/gnu/store/[^ ]+\.drv)", line))
    return sorted(found)


def downloaded_items(log):
    """The store items a log lists under "would be downloaded:" (GRUB itself, efibootmgr ...:
    what installing the bootloader runs)."""
    found, listing = set(), False
    for line in log.splitlines():
        if re.search(r"(would|will) be downloaded:", line):
            listing = True
            continue
        match = re.match(r"^\s+(/gnu/store/\S+)\s*$", line) if listing else None
        if match:
            found.add(match.group(1))
        else:
            listing = False
    return sorted(found)


def downloads(log):
    """How many items a dry run says it would download (0 if it says nothing)."""
    match = re.search(r"(\d+) items? would be downloaded", log)
    if match:
        return int(match.group(1))
    if "would be downloaded:" in log:
        return 1
    return 0


def parse_drv(path):
    """(outputs, input drv paths, input sources) of a derivation file (ATerm)."""
    text = Path(path).read_text()
    head = text[len("Derive(["):]
    outputs_part = head[:head.index("]")]
    outputs = {m.group(1): m.group(2) for m in OUTPUT.finditer(outputs_part + ")")}
    rest = head[head.index("]") + 1:]
    # each input: ("/gnu/store/...drv",["out","lib"]): the derivation and the outputs used
    inputs = [(d, re.findall(r'"([^"]+)"', names))
              for d, names in re.findall(r'\("(/[^"]+\.drv)",\[([^\]]*)\]\)', rest)]
    sources_part = rest[rest.index("],[") + 3:]
    sources = re.findall(r'"(/gnu/store/[^"]+)"', sources_part[:sources_part.index("]")])
    return outputs, inputs, sources


def outputs_of(drv):
    return parse_drv(drv)[0]


def inputs_needed(build):
    """The sources, and the outputs of the inputs not themselves in BUILD, of BUILD's drvs."""
    items = set()
    for drv in build:
        _, inputs, sources = parse_drv(drv)
        items.update(sources)
        for dep, names in inputs:
            if dep not in build:
                outs = outputs_of(dep)
                items.update(outs[name] for name in names)
    return items


def main(argv):
    if len(argv) == 3 and argv[1] == "drvs":
        for drv in drvs_to_build(Path(argv[2]).read_text()):
            print(drv)
        return 0
    if len(argv) == 5 and argv[1] == "items":
        template = argv[2]
        template_log, variant_log = Path(argv[3]).read_text(), Path(argv[4]).read_text()
        variant = set(drvs_to_build(variant_log))
        if not variant:
            sys.exit("offline-items: the second install would build nothing (it should build "
                     "its accounts, /etc, initrd and GRUB menu)")
        if downloads(variant_log):
            sys.exit("offline-items: the second install would still download items; the "
                     "template's install was not fully built first")
        items = {template}
        for drv in drvs_to_build(template_log):
            items.update(outputs_of(drv).values())
        items.update(downloaded_items(template_log))
        items |= inputs_needed(variant)
        for item in sorted(items):
            print(item)
        return 0
    sys.exit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
