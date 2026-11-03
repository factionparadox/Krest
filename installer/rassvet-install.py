#!/usr/bin/env python3
"""Рассвет / Rassvet installer: Guix System with Rassvet's desktop, on one whole disk.

Asks for the disk, a computer name, your username and password, the timezone and whether to
log in automatically. After ONE Yes/No it does the manual Guix install by itself, offline:

  1. GPT: 1 GiB EFI, swap the size of the RAM (hibernation), XFS root.  mkfs, mount /mnt.
  2. herd start cow-store /mnt   (the store writes go to the new disk, not to RAM)
  3. guix archive --import       every package of the system, from this USB stick
  4. /mnt/etc/config.scm         a few lines: your disk's UUIDs, your name, your choices
  5. guix system init            builds what is personal (a few small files) and GRUB

Everything it runs, with its output, shows on screen as it happens and is kept in
/tmp/rassvet-install.log (copied to /var/log on the new system).
"""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess as sp
import sys
import time

TITLE = "Рассвет / Rassvet installer"
TARGET = Path("/mnt")
LOGFILE = Path("/tmp/rassvet-install.log")
# The system's packages: an archive on the stick (build/build-iso.sh appends it to the ISO).
ARCHIVES = [Path("/rassvet/system.nar.zst"), Path("/run/rassvet/system.nar.zst")]
# Rassvet's channel and Nonguix, exactly as the system was built from them
CHANNELS = Path(os.environ.get("RASSVET_CHANNELS", "/run/current-system/profile/share/rassvet-installer"))
GiB = 1024 ** 3
EFI_GIB = 1
MIN_ROOT_GIB = 40
USERNAME = re.compile(r"^[a-z_][a-z0-9_-]{0,30}$")
HOSTNAME = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9-]{0,62}$")
MOUNTS, SWAPS = [], []
TIMEZONES = [
    ("Europe/London", "United Kingdom"),
    ("Europe/Moscow", "Moscow"),
    ("Europe/Dublin", "Ireland"),
    ("Europe/Berlin", "Central Europe"),
    ("America/New_York", "Eastern United States"),
    ("UTC", "Coordinated Universal Time"),
]


# ------------------------------------------------------------------ pure helpers (tested)
def partition_path(disk, number):
    """NVMe and eMMC disks name partitions with a p (nvme0n1p1); SATA and VirtIO do not."""
    return f"{disk}{'p' if disk[-1].isdigit() else ''}{number}"


def plan(disk_bytes, ram_bytes):
    """Partition sizes in GiB: (efi, swap, root). Swap matches RAM so hibernation fits; on a
    disk too small for that, no swap partition (zram still swaps, but no hibernation)."""
    disk_gib = disk_bytes // GiB
    swap = -(-ram_bytes // GiB)
    if disk_gib - EFI_GIB - swap < MIN_ROOT_GIB:
        swap = 0
    root = disk_gib - EFI_GIB - swap
    if root < MIN_ROOT_GIB:
        raise ValueError(f"disk too small: {disk_gib} GiB (Rassvet needs {MIN_ROOT_GIB + EFI_GIB})")
    return EFI_GIB, swap, root


def scheme_string(text):
    """A Scheme string literal for TEXT."""
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def config_scm(hostname, username, full_name, timezone, autologin, efi_uuid, root_uuid, swap_uuid):
    """/etc/config.scm: Rassvet's whole system, for this laptop."""
    swap = scheme_string(swap_uuid) if swap_uuid else "#f"
    return f""";; Рассвет / Rassvet: this computer's system. The rest is in Rassvet's channel,
;; (rassvet system): guix/rassvet/system.scm in https://github.com/factionparadox/Pustota
;; After changing this file:  sudo guix system reconfigure /etc/config.scm
;; Back to the previous generation:  sudo guix system roll-back  (or pick it in GRUB)
(use-modules (rassvet system))

(rassvet-operating-system
  #:host-name {scheme_string(hostname)}
  #:user {scheme_string(username)}
  #:full-name {scheme_string(full_name)}
  #:timezone {scheme_string(timezone)}
  #:autologin? {"#t" if autologin else "#f"}
  #:efi-uuid {scheme_string(efi_uuid)}
  #:root-uuid {scheme_string(root_uuid)}
  #:swap-uuid {swap})
"""


def shadow_lines(entries):
    """/etc/shadow lines for (name, hash) pairs. Guix keeps these passwords when it creates
    the accounts at first boot, so nobody starts with an empty password."""
    days = int(time.time() // 86400)
    return "".join(f"{name}:{hashed}:{days}:0:99999:7:::\n" for name, hashed in entries)


# ------------------------------------------------------------------ dialog
def dialog(*args, output=False):
    clear = [] if "--infobox" in map(str, args) else ["--clear"]
    command = ["dialog", *clear, "--stdout", "--backtitle", TITLE, "--title", "Rassvet",
               *map(str, args)]
    result = sp.run(command, text=True, stdout=sp.PIPE)
    return (result.returncode, result.stdout.strip()) if output else result.returncode


def notice(text):
    dialog("--msgbox", text, 14, 78)


def input_field(label, preset="", password=False):
    while True:
        args = (["--insecure", "--passwordbox", label, 11, 76] if password
                else ["--inputbox", label, 11, 76, preset])
        code, value = dialog(*args, output=True)
        if code != 0:
            raise InterruptedError("cancelled")
        if value:
            return value
        notice("This cannot be empty.")


def choice(label, options, default=None):
    extra = ["--default-item", default] if default else []
    code, selected = dialog(*extra, "--menu", label, 19, 78, 10,
                            *[item for row in options for item in row], output=True)
    if code != 0:
        raise InterruptedError("cancelled")
    return selected


# ------------------------------------------------------------------ progress
# Plain text on the screen while it works: each step's heading, every command as it starts
# and its output as it comes. Nothing can leave the screen blank.
def stage(number, total, text):
    if sys.stdout.isatty():
        sys.stdout.write("\033[H\033[2J")
    rule = "=" * 60
    sys.stdout.write(f"{rule}\n Installing Rassvet: step {number} of {total}\n{rule}\n{text}\n\n"
                     f"Each command and its output appear below as they happen; all of it is kept\n"
                     f"in {LOGFILE} (Alt+F3 opens a shell).\n\n")
    sys.stdout.flush()


def say(text):
    sys.stdout.write(text[:200] + "\n")
    sys.stdout.flush()


def log(message):
    with LOGFILE.open("a", encoding="utf-8") as fh:
        fh.write(message + "\n")


def run(*cmd, input_text=None, capture=False, quiet=False):
    with LOGFILE.open("a", encoding="utf-8") as logf:
        logf.write("+ " + " ".join(map(str, cmd)) + "\n")
        logf.flush()
        if capture:
            result = sp.run(list(map(str, cmd)), input=input_text, text=True,
                            stdout=sp.PIPE, stderr=logf, check=True)
            logf.write(result.stdout)
            return result.stdout
        say("$ " + " ".join(map(str, cmd)))
        proc = sp.Popen(list(map(str, cmd)), stdin=sp.PIPE if input_text else sp.DEVNULL,
                        stdout=sp.PIPE, stderr=sp.STDOUT)
        if input_text:
            proc.stdin.write(input_text.encode())
            proc.stdin.close()
        pending = b""
        for chunk in iter(lambda: proc.stdout.read1(4096), b""):
            logf.write(chunk.decode(errors="replace"))
            logf.flush()
            pending += chunk
            *lines, pending = re.split(rb"[\r\n]", pending)
            for raw in lines:
                text = raw.decode(errors="replace").strip()
                if text and not quiet:
                    say("  " + text)
        if pending.strip() and not quiet:
            say("  " + pending.decode(errors="replace").strip())
        if proc.wait():
            raise sp.CalledProcessError(proc.returncode, list(map(str, cmd)))
    return None


def import_archive(archive):
    """zstd -dc ARCHIVE | guix archive --import, with a percentage as it goes."""
    size = archive.stat().st_size
    say(f"$ zstd -dc {archive} | guix archive --import    ({size / GiB:.1f} GiB, compressed)")
    log(f"+ zstd -dc {archive} | guix archive --import")
    with LOGFILE.open("a", encoding="utf-8") as logf:
        unzstd = sp.Popen(["zstd", "-dc"], stdin=sp.PIPE, stdout=sp.PIPE, stderr=logf)
        guix = sp.Popen(["guix", "archive", "--import"], stdin=unzstd.stdout,
                        stdout=logf, stderr=logf)
        unzstd.stdout.close()
        done, shown = 0, -1
        with archive.open("rb") as src:
            for block in iter(lambda: src.read(8 << 20), b""):
                unzstd.stdin.write(block)
                done += len(block)
                percent = done * 100 // size
                if percent != shown:
                    shown = percent
                    sys.stdout.write(f"\r  [{percent:3d}%] {done / GiB:5.1f} of {size / GiB:.1f} GiB copied into the store")
                    sys.stdout.flush()
        unzstd.stdin.close()
        if unzstd.wait() or guix.wait():
            raise RuntimeError("the system archive did not import (see the log)")
    say("")


def mount(device, path):
    Path(path).mkdir(parents=True, exist_ok=True)
    run("mount", device, path)
    MOUNTS.append(str(path))


def cleanup():
    for path in reversed(MOUNTS):
        sp.run(["umount", "-R", path], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    MOUNTS.clear()
    for dev in SWAPS:
        sp.run(["swapoff", dev], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    SWAPS.clear()


def uuid_of(device):
    value = sp.check_output(["blkid", "-s", "UUID", "-o", "value", device], text=True).strip()
    if not value:
        raise RuntimeError(f"no filesystem UUID on {device}")
    return value


def password_hash(password):
    return sp.run(["openssl", "passwd", "-6", "-stdin"], input=password, text=True,
                  stdout=sp.PIPE, check=True).stdout.strip()


def descendants(device):
    yield device
    for child in device.get("children") or ():
        yield from descendants(child)


def disks():
    """Whole, writable, unmounted disks of a usable size: never the stick we booted from."""
    data = json.loads(sp.check_output(
        ["lsblk", "-J", "-b", "-o", "NAME,PATH,TYPE,SIZE,MODEL,RO,MOUNTPOINTS"], text=True))
    found = []
    for dev in data["blockdevices"]:
        if dev.get("type") != "disk" or str(dev.get("ro", "0")) not in ("0", "false", "False"):
            continue
        if int(dev.get("size") or 0) < (MIN_ROOT_GIB + EFI_GIB) * GiB:
            continue
        if any(any(mp for mp in (n.get("mountpoints") or [])) for n in descendants(dev)):
            continue
        found.append(dev)
    return found


def ram_bytes():
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemTotal:"):
            return int(line.split()[1]) * 1024
    raise RuntimeError("cannot read /proc/meminfo")


def failure_dialog(error):
    details = ""
    if LOGFILE.is_file():
        lines = LOGFILE.read_text(encoding="utf-8", errors="replace").splitlines()
        hits = [l for l in lines[-200:] if re.search(r"error|failed|not found|unable|cannot", l, re.I)]
        details = "\n".join((hits or lines)[-10:])
    dialog("--msgbox", f"The installation stopped: {error}\n\nFrom the log:\n{details or '(empty)'}"
           f"\n\nWhole log: {LOGFILE}  (Alt+F3, then: less {LOGFILE})\n"
           "Nothing on the disk is usable yet; run the installer again.", 24, 92)


# ------------------------------------------------------------------ the install
def install(disk, hostname, username, password, timezone, autologin, archive):
    size = int(sp.check_output(["lsblk", "-b", "-d", "-n", "-o", "SIZE", disk], text=True))
    efi_gib, swap_gib, root_gib = plan(size, ram_bytes())
    efi, swap = partition_path(disk, 1), partition_path(disk, 2)
    root = partition_path(disk, 3 if swap_gib else 2)
    total = 5

    stage(1, total, f"Partitioning {disk}: {efi_gib} GiB EFI, {swap_gib or 'no'} GiB swap, "
                    f"{root_gib} GiB XFS")
    run("wipefs", "-a", disk)
    run("sgdisk", "--zap-all", disk)
    run("sgdisk", "-n", f"1:1MiB:+{efi_gib}GiB", "-t", "1:ef00", "-c", "1:EFI", disk)
    if swap_gib:
        run("sgdisk", "-n", f"2:0:+{swap_gib}GiB", "-t", "2:8200", "-c", "2:swap", disk)
    n = 3 if swap_gib else 2
    run("sgdisk", "-n", f"{n}:0:0", "-t", f"{n}:8300", "-c", f"{n}:Rassvet", disk)
    run("partprobe", disk)
    for _ in range(20):
        if all(Path(p).exists() for p in (efi, root) + ((swap,) if swap_gib else ())):
            break
        time.sleep(1)
    else:
        raise RuntimeError("the new partitions did not appear")
    run("mkfs.vfat", "-F", "32", "-n", "EFI", efi)
    run("mkfs.xfs", "-f", "-L", "Rassvet", root)
    if swap_gib:
        run("mkswap", "-L", "swap", swap)
        run("swapon", swap)
        SWAPS.append(swap)
    mount(root, TARGET)
    mount(efi, TARGET / "boot/efi")

    stage(2, total, "The store on the new disk (herd start cow-store /mnt): from now on, what\n"
                    "Guix copies goes onto the disk, not into this stick's memory.")
    run("herd", "start", "cow-store", TARGET)

    stage(3, total, "Copying the whole system from the USB stick into the store.\n"
                    "No network is needed. This is the long step.")
    import_archive(archive)

    stage(4, total, "Your settings: /etc/config.scm (UUIDs, name, timezone) and passwords")
    swap_uuid = uuid_of(swap) if swap_gib else None
    (TARGET / "etc").mkdir(parents=True, exist_ok=True)
    config = config_scm(hostname, username, "", timezone, autologin,
                        uuid_of(efi), uuid_of(root), swap_uuid)
    (TARGET / "etc/config.scm").write_text(config)
    for line in config.splitlines():
        say("  " + line)
    hashed = password_hash(password)
    shadow = TARGET / "etc/shadow"
    shadow.write_text(shadow_lines([("root", hashed), (username, hashed)]))
    shadow.chmod(0o600)
    log("passwords: root and the user, written to /etc/shadow (hashed)")

    stage(5, total, "guix system init: the personal parts (accounts, GRUB menu, initrd) and\n"
                    "GRUB itself. Everything else is already on the disk.")
    run("guix", "system", "init", "--no-substitutes", "--no-grafts",
        "-L", CHANNELS / "nonguix", "-L", CHANNELS / "rassvet/guix",
        TARGET / "etc/config.scm", TARGET)
    if not (TARGET / "boot/efi/EFI").is_dir():
        raise RuntimeError("GRUB was not installed in the EFI partition")
    log(f"installed: user {username}, swap {swap_gib} GiB")


def find_archive():
    for path in ARCHIVES:
        if path.is_file():
            return path
    return None


def main():
    if os.geteuid() != 0:
        raise SystemExit("run it as root")
    if not Path("/sys/firmware/efi").is_dir():
        notice("This computer started the installer in legacy BIOS mode.\n\n"
               "Rassvet installs for UEFI only: restart, choose the USB stick's UEFI entry "
               "in the boot menu.")
        return 2
    archive = find_archive()
    if archive is None:
        notice("The system archive (rassvet/system.nar.zst) is not on this stick.\n\n"
               "Build the ISO again with build/build-iso.sh.")
        return 2
    if sp.run(["mountpoint", "-q", str(TARGET)]).returncode == 0:
        notice("/mnt is already mounted: restart and run the installer again.")
        return 2
    available = disks()
    if not available:
        notice(f"No unmounted disk of at least {MIN_ROOT_GIB + EFI_GIB} GiB was found.")
        return 2
    notice("Рассвет / Rassvet\n\nGuix System (Shepherd, no systemd), ratpoison and Plan 9's "
           "tools. Every change makes a new generation you can go back to from the boot "
           "menu.\n\nFive questions, then one Yes/No. Choosing Yes erases the whole disk you "
           "picked.")
    options = [(d["path"], f"{int(d['size']) / GiB:.0f} GiB  {(d.get('model') or 'disk').strip()[:40]}")
               for d in available]
    disk = choice("Install Rassvet on which disk?", options)
    hostname = input_field("Computer name:", "rassvet")
    if not HOSTNAME.fullmatch(hostname) or hostname.endswith("-"):
        notice("Use letters, digits and hyphens for the computer name.")
        return 2
    username = input_field("Your username (lower case):")
    if not USERNAME.fullmatch(username) or username in ("root", "rassvet"):
        notice("Use lower-case letters, digits, _ or - for the username.")
        return 2
    password = input_field("Password (also the root password, for recovery):", password=True)
    if input_field("The same password again:", password=True) != password:
        notice("The passwords were different. Nothing has been changed.")
        return 2
    timezone = choice("Timezone:", TIMEZONES, default="Europe/London")
    autologin = dialog("--yes-label", "Log in automatically", "--no-label", "Ask for my password",
                       "--yesno", "Start straight into the desktop when the laptop boots?\n\n"
                       "The screen still locks with your password when the lid closes or it "
                       "sleeps.", 10, 76) == 0
    current = {d["path"]: d for d in disks()}
    if disk not in current:
        notice("That disk changed or is now mounted. Nothing has been changed.")
        return 2
    try:
        efi_gib, swap_gib, root_gib = plan(int(current[disk]["size"]), ram_bytes())
    except ValueError as error:
        notice(str(error))
        return 2
    model = (current[disk].get("model") or "disk").strip()
    if dialog("--defaultno", "--yes-label", "Erase and install", "--no-label", "Cancel", "--yesno",
              f"Erase EVERYTHING on this disk?\n\n  {disk}  {model}  "
              f"{int(current[disk]['size']) / GiB:.0f} GiB\n\n"
              f"  {efi_gib} GiB EFI   {swap_gib or 'no'} GiB swap (hibernation)   "
              f"{root_gib} GiB XFS\n  computer: {hostname}   user: {username}\n"
              f"  {'automatic login' if autologin else 'password at login'}   {timezone}", 15, 80) != 0:
        notice("Cancelled. Nothing has been changed.")
        return 1

    LOGFILE.write_text("Rassvet installation\n")
    try:
        install(disk, hostname, username, password, timezone, autologin, archive)
    except (sp.CalledProcessError, RuntimeError, OSError, ValueError) as error:
        failure_dialog(error)
        cleanup()
        return 1
    finally:
        password = ""
    (TARGET / "var/log").mkdir(parents=True, exist_ok=True)
    shutil.copy2(LOGFILE, TARGET / "var/log/rassvet-install.log")
    cleanup()
    notice("Rassvet is installed.\n\nRemove the USB stick and restart: reboot\n\n"
           "After logging in, Super+? shows the keys; rassvet-learn explains the system.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (KeyboardInterrupt, InterruptedError):
        print("\nInstaller cancelled. Nothing more was changed.", file=sys.stderr)
        sys.exit(1)
