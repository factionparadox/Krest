#!/usr/bin/env python3
"""Pustota installer: Void glibc on one whole disk, automatically.

Asks for: the disk, a computer name, your username and password, the timezone, and whether to
log in automatically. Then, after ONE Yes/No confirmation, it does the chroot install from
Void's handbook by itself (the same steps a manual install takes, in the same order):

  1. GPT: 1 GiB EFI system partition, swap the size of the RAM (so the laptop can hibernate),
     XFS root on the rest.  mkfs.vfat / mkswap / mkfs.xfs, mounted at /mnt/target.
  2. Void's signing keys, then  xbps-install -r /mnt/target base-system  plus Pustota's three
     packages, from Void's repository (base) and the ISO (Pustota). Void's default kernel is
     held back (ignorepkg=linux): linux-mainline, the 7.x series, is the one for Panther Lake.
  3. xgenfstab -U for /etc/fstab; hostname; en_GB and ru_RU locales; timezone; keyboard.
  4. Your user (wheel, audio, video, input, network, bluetooth), sudo for wheel.
  5. runit services linked into /etc/runit/runsvdir/default.
  6. xbps-reconfigure -fa (locales, initramfs with resume), GRUB for UEFI, grub-mkconfig.

UEFI only (the Framework 13 Pro boots UEFI; turn Secure Boot off). Whole-disk installs only.
Everything it runs is logged to /tmp/pustota-install.log, copied to /var/log on the new system.
"""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess as sp
import sys
import time
import urllib.error
import urllib.request

TITLE = "Пустота / Pustota installer"
TARGET = Path("/mnt/target")
REPO = Path("/usr/lib/pustota/repo")
# Void's mirrors (https://xmirror.voidlinux.org): the first that answers is used, and written
# into the new system if it is not the default.
MIRRORS = ["https://repo-default.voidlinux.org", "https://repo-de.voidlinux.org",
           "https://repo-fi.voidlinux.org", "https://repo-fastly.voidlinux.org",
           "https://mirrors.dotsrc.org/voidlinux", "https://ftp.lysator.liu.se/pub/voidlinux",
           "https://mirrors.summithq.com/voidlinux"]
MIRROR = MIRRORS[0] + "/current"
LOGFILE = Path("/tmp/pustota-install.log")
TRUSTED_KEYS = Path("/var/db/xbps/keys")
MOUNTS = []
SWAPS = []
GiB = 1024 ** 3
EFI_GIB = 1
MIN_ROOT_GIB = 20
USERNAME = re.compile(r"^[a-z_][a-z0-9_-]{0,30}$")
HOSTNAME = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9-]{0,62}$")
PACKAGES = ["base-system", "pustota-desktop", "pustota-learn", "pustota-russian"]
GROUPS = ["wheel", "audio", "video", "input", "network", "bluetooth", "storage", "users"]
# runit services. The first three are required for a working desktop; the rest are logged
# if missing rather than stopping the install.
SERVICES_REQUIRED = ["dbus", "elogind", "NetworkManager"]
SERVICES_OPTIONAL = ["bluetoothd", "tlp", "thermald", "chronyd", "socklog-unix", "nologd",
                     "zramen", "earlyoom", "ufw"]
# Base live images start these; NetworkManager and elogind do their jobs on Pustota.
SERVICES_OFF = ["dhcpcd", "wpa_supplicant", "acpid"]
LOCALES = ["en_GB.UTF-8 UTF-8", "ru_RU.UTF-8 UTF-8", "en_US.UTF-8 UTF-8"]
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
    swap = -(-ram_bytes // GiB)          # RAM rounded up to whole GiB
    if disk_gib - EFI_GIB - swap < MIN_ROOT_GIB:
        swap = 0
    root = disk_gib - EFI_GIB - swap
    if root < MIN_ROOT_GIB:
        raise ValueError(f"disk too small: {disk_gib} GiB (Pustota needs {MIN_ROOT_GIB + EFI_GIB})")
    return EFI_GIB, swap, root


def enable_locales(text, wanted=LOCALES):
    """Uncomment the wanted lines in /etc/default/libc-locales (what you would do by hand)."""
    out = []
    for line in text.splitlines():
        bare = line.lstrip("#").strip()
        out.append(bare if bare in wanted else line)
    have = {line.strip() for line in out}
    out += [w for w in wanted if w not in have]
    return "\n".join(out) + "\n"


def with_resume(grub_default, swap_uuid):
    """Add resume=UUID=... to GRUB_CMDLINE_LINUX_DEFAULT (hibernation), once."""
    if not swap_uuid or "resume=" in grub_default:
        return grub_default
    pattern = re.compile(r'^(GRUB_CMDLINE_LINUX_DEFAULT=")', re.M)
    if pattern.search(grub_default):
        return pattern.sub(r'\1resume=UUID=' + swap_uuid + ' ', grub_default, count=1)
    return grub_default + f'\nGRUB_CMDLINE_LINUX_DEFAULT="resume=UUID={swap_uuid} loglevel=4"\n'


def firewall_on(conf):
    """ufw.conf with ENABLED=yes: the ufw service then loads the rules at boot. ufw's defaults
    (/etc/default/ufw) already drop everything coming in and allow everything going out."""
    lines = [l for l in conf.splitlines() if not l.strip().startswith("ENABLED=")]
    return "\n".join(lines + ["ENABLED=yes"]) + "\n"


def with_fingerprint(pam):
    """/etc/pam.d/sudo trying the fingerprint reader first; with no finger enrolled (or no
    reader) pam_fprintd steps aside and the password is asked as usual."""
    line = "auth      sufficient pam_fprintd.so"
    if "pam_fprintd.so" in pam:
        return pam
    out, done = [], False
    for l in pam.splitlines():
        if not done and l.split()[:1] == ["auth"]:
            out.append(line)
            done = True
        out.append(l)
    if not done:
        out.insert(1 if out and out[0].startswith("#%PAM") else 0, line)
    return "\n".join(out) + "\n"


def autologin_conf(conf, username):
    """agetty on tty1 logs USERNAME in (then ~/.bash_profile runs startx)."""
    args = f'GETTY_ARGS="--noclear --autologin {username}"'
    if re.search(r"^GETTY_ARGS=", conf, re.M):
        return re.sub(r"^GETTY_ARGS=.*$", args, conf, flags=re.M)
    return conf.rstrip("\n") + "\n" + args + "\n"


def fstab_ok(fstab):
    """xgenfstab must have produced /, /boot/efi (and the swap, when there is one)."""
    mounts = {fields[1] for fields in (l.split() for l in fstab.splitlines())
              if len(fields) >= 3 and not fields[0].startswith("#")}
    return "/" in mounts and "/boot/efi" in mounts


# ------------------------------------------------------------------ dialog
def dialog(*args, output=False):
    command = ["dialog", "--clear", "--stdout", "--backtitle", TITLE, "--title", "Pustota",
               *map(str, args)]
    result = sp.run(command, text=True, stdout=sp.PIPE)
    return (result.returncode, result.stdout.strip()) if output else result.returncode


def notice(text):
    dialog("--msgbox", text, 14, 78)


def input_field(label, preset="", password=False):
    while True:
        args = ["--insecure", "--passwordbox", label, 11, 76] if password else ["--inputbox", label, 11, 76, preset]
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


def stage(message):
    dialog("--infobox", message + "\n\nEverything is logged to " + str(LOGFILE)
           + " (Alt+F2 for a shell to read it).", 9, 78)


# ------------------------------------------------------------------ system
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
        if not re.fullmatch(r"/dev/[A-Za-z0-9_./+-]+", dev.get("path", "")):
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


def run(*cmd, input_text=None, capture=False):
    with LOGFILE.open("a", encoding="utf-8") as log:
        log.write("+ " + " ".join(map(str, cmd)) + "\n")
        log.flush()
        if capture:
            result = sp.run(list(map(str, cmd)), input=input_text, text=True,
                            stdout=sp.PIPE, stderr=log, check=True)
            log.write(result.stdout)
            return result.stdout
        sp.run(list(map(str, cmd)), input=input_text, text=True,
               stdout=log, stderr=sp.STDOUT, check=True)
    return None


def log(message):
    with LOGFILE.open("a", encoding="utf-8") as fh:
        fh.write(message + "\n")


def mount(device, path, *, bind=False):
    Path(path).mkdir(parents=True, exist_ok=True)
    if bind:
        run("mount", "--rbind", device, path)
        run("mount", "--make-rslave", path)
    else:
        run("mount", device, path)
    MOUNTS.append(str(path))


def cleanup():
    for path in reversed(MOUNTS):
        sp.run(["umount", "-R", path], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    MOUNTS.clear()
    for dev in SWAPS:
        sp.run(["swapoff", dev], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    SWAPS.clear()


def chroot(*args, input_text=None):
    run("chroot", TARGET, *args, input_text=input_text)


def uuid_of(device):
    value = sp.check_output(["blkid", "-s", "UUID", "-o", "value", device], text=True).strip()
    if not value:
        raise RuntimeError(f"no filesystem UUID on {device}")
    return value


def check_repository():
    """Choose the first Void mirror that answers (sets MIRROR); fail before touching a disk."""
    global MIRROR
    errors = []
    for base in MIRRORS:
        try:
            with urllib.request.urlopen(base + "/current/x86_64-repodata", timeout=12) as response:
                response.read(1)
            MIRROR = base + "/current"
            return base
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            errors.append(f"{base}: {error}")
    raise RuntimeError("No Void mirror answered. Connect Wi-Fi (nmtui) or Ethernet first; no disk "
                       "has been touched.\n\n" + "\n".join(errors[:3]))


def failure_dialog(error):
    details = ""
    if LOGFILE.is_file():
        lines = LOGFILE.read_text(encoding="utf-8", errors="replace").splitlines()
        hits = [l for l in lines[-150:] if re.search(r"error|failed|not found|unable|cannot", l, re.I)]
        details = "\n".join((hits or lines)[-10:])
    dialog("--msgbox", f"The installation stopped: {error}\n\nFrom the log:\n{details or '(empty)'}"
           f"\n\nWhole log: {LOGFILE}  (Alt+F2, then: less {LOGFILE})\n"
           "Do not boot the half-installed disk; run the installer again.", 24, 92)


# ------------------------------------------------------------------ the install
def install(disk, hostname, username, password, timezone, autologin):
    efi_gib, swap_gib, root_gib = plan(int(sp.check_output(
        ["lsblk", "-b", "-d", "-n", "-o", "SIZE", disk], text=True)), ram_bytes())
    log(f"Void mirror: {MIRROR}")
    efi, swap = partition_path(disk, 1), partition_path(disk, 2)
    root = partition_path(disk, 3 if swap_gib else 2)

    stage(f"1/6  Partitioning {disk}: {efi_gib} GiB EFI, "
          f"{swap_gib or 'no'} GiB swap, {root_gib} GiB XFS")
    run("wipefs", "-a", disk)
    run("sgdisk", "--zap-all", disk)
    run("sgdisk", "-n", f"1:1MiB:+{efi_gib}GiB", "-t", "1:ef00", "-c", "1:EFI", disk)
    if swap_gib:
        run("sgdisk", "-n", f"2:0:+{swap_gib}GiB", "-t", "2:8200", "-c", "2:swap", disk)
    n = 3 if swap_gib else 2
    run("sgdisk", "-n", f"{n}:0:0", "-t", f"{n}:8300", "-c", f"{n}:Pustota", disk)
    run("partprobe", disk)
    run("udevadm", "settle")
    for _ in range(15):
        if all(Path(p).exists() for p in (efi, root) + ((swap,) if swap_gib else ())):
            break
        time.sleep(1)
    else:
        raise RuntimeError("the new partitions did not appear")
    run("mkfs.vfat", "-F", "32", "-n", "EFI", efi)
    run("mkfs.xfs", "-f", "-L", "Pustota", root)
    if swap_gib:
        run("mkswap", "-L", "swap", swap)
        run("swapon", swap)
        SWAPS.append(swap)
    mount(root, TARGET)
    mount(efi, TARGET / "boot/efi")

    stage("2/6  Installing Void (base-system, linux-mainline) and Pustota.\n"
          "This downloads about 1.5 GB; on Wi-Fi it takes a while.")
    # A new XBPS root trusts nothing: copy Void's keys from this (verified) live system first,
    # or XBPS stops to ask about the signing key even with -y.
    keys = sorted(p for p in TRUSTED_KEYS.glob("*.plist") if p.is_file())
    if not keys:
        raise RuntimeError("no Void signing keys in /var/db/xbps/keys")
    (TARGET / "var/db/xbps/keys").mkdir(parents=True, exist_ok=True)
    for key in keys:
        shutil.copy2(key, TARGET / "var/db/xbps/keys" / key.name)
    # Keep Void's default kernel (6.x) out: linux-mainline (7.x) is the one this laptop needs.
    xbpsd = TARGET / "etc/xbps.d"
    xbpsd.mkdir(parents=True, exist_ok=True)
    if not MIRROR.startswith(MIRRORS[0]):
        # the default mirror did not answer: the new system uses the one that did
        (xbpsd / "00-repository-main.conf").write_text(
            "# chosen by the Pustota installer (the default mirror did not answer)\n"
            f"repository={MIRROR}\n")
        (xbpsd / "10-repository-nonfree.conf").write_text(
            "# chosen by the Pustota installer (the default mirror did not answer)\n"
            f"repository={MIRROR}/nonfree\n")
    (xbpsd / "10-pustota-kernel.conf").write_text(
        "# Pustota: the Framework 13 Pro needs Linux 7.x; Void's default 'linux' is older.\n"
        "# linux-mainline follows Void's newest kernel series instead.\n"
        "ignorepkg=linux\nignorepkg=linux-headers\n")
    run("xbps-install", "-r", TARGET, "-C", "etc/xbps.d", "-S", "-y",
        "-R", REPO, "-R", MIRROR, "-R", MIRROR + "/nonfree", *PACKAGES)
    for pkg in PACKAGES + ["linux-mainline"]:
        run("xbps-query", "-r", TARGET, "-p", "pkgver", pkg)

    stage("3/6  fstab, name, languages, time and keyboard")
    fstab = run("xgenfstab", "-U", TARGET, capture=True)
    if not fstab_ok(fstab):
        raise RuntimeError("xgenfstab did not list / and /boot/efi")
    (TARGET / "etc/fstab").write_text(fstab)
    (TARGET / "etc/hostname").write_text(hostname + "\n")
    hosts = TARGET / "etc/hosts"
    if hosts.exists() and hostname not in hosts.read_text():
        hosts.write_text(hosts.read_text() + f"127.0.1.1\t{hostname}\n")
    locales = TARGET / "etc/default/libc-locales"
    locales.write_text(enable_locales(locales.read_text() if locales.exists() else ""))
    (TARGET / "etc/locale.conf").write_text("LANG=en_GB.UTF-8\nLC_COLLATE=C\n")
    rc = TARGET / "etc/rc.conf"
    text = rc.read_text() if rc.exists() else ""
    text = re.sub(r"(?m)^\s*(KEYMAP|HARDWARECLOCK|FONT)=.*$\n?", "", text)
    rc.write_text(text.rstrip("\n") + '\nKEYMAP="uk"\nHARDWARECLOCK="UTC"\nFONT="ter-v24n"\n')
    zone = TARGET / "usr/share/zoneinfo" / timezone
    if not zone.is_file():
        raise RuntimeError("timezone not found: " + timezone)
    (TARGET / "etc/localtime").unlink(missing_ok=True)
    (TARGET / "etc/localtime").symlink_to("/usr/share/zoneinfo/" + timezone)

    for d in ("dev", "proc", "sys", "run"):
        mount("/" + d, TARGET / d, bind=True)

    stage("4/6  Your account")
    existing = {line.split(":")[0] for line in (TARGET / "etc/group").read_text().splitlines()}
    groups = ",".join(g for g in GROUPS if g in existing)
    chroot("useradd", "-m", "-G", groups, "-s", "/bin/bash", username)
    chroot("chpasswd", input_text=f"{username}:{password}\n")       # on stdin, never on a command line
    chroot("chpasswd", input_text=f"root:{password}\n")
    sudoers = TARGET / "etc/sudoers.d/10-pustota-wheel"
    sudoers.parent.mkdir(parents=True, exist_ok=True)
    sudoers.write_text("%wheel ALL=(ALL:ALL) ALL\n")
    sudoers.chmod(0o440)

    stage("5/6  Services (runit)")
    enabled = TARGET / "etc/runit/runsvdir/default"
    enabled.mkdir(parents=True, exist_ok=True)
    for svc in SERVICES_REQUIRED + SERVICES_OPTIONAL:
        if (TARGET / "etc/sv" / svc).is_dir():
            link = enabled / svc
            link.unlink(missing_ok=True)
            link.symlink_to(f"/etc/sv/{svc}")
            log(f"service enabled: {svc}")
        elif svc in SERVICES_REQUIRED:
            raise RuntimeError(f"runit service missing: /etc/sv/{svc}")
        else:
            log(f"service not available, skipped: {svc}")
    for svc in SERVICES_OFF:
        (enabled / svc).unlink(missing_ok=True)
    ufw = TARGET / "etc/ufw/ufw.conf"
    if ufw.exists():
        ufw.write_text(firewall_on(ufw.read_text()))
        log("firewall: ufw on (incoming dropped, outgoing allowed)")
    pam_sudo = TARGET / "etc/pam.d/sudo"
    if pam_sudo.exists() and (TARGET / "usr/lib/security/pam_fprintd.so").exists():
        pam_sudo.write_text(with_fingerprint(pam_sudo.read_text()))
        log("sudo: fingerprint first, then password")
    if autologin:
        conf = TARGET / "etc/sv/agetty-tty1/conf"
        conf.write_text(autologin_conf(conf.read_text() if conf.exists() else "", username))

    stage("6/6  Locales, initramfs and GRUB (xbps-reconfigure -fa, grub-install)")
    grub = TARGET / "etc/default/grub"
    if swap_gib and grub.exists():
        grub.write_text(with_resume(grub.read_text(), uuid_of(swap)))
    if swap_gib:
        # Lid closed: suspend, and after two hours asleep, hibernate (no battery drain at all).
        for rel, text in (("etc/elogind/logind.conf.d/60-pustota-hibernate.conf",
                           "[Login]\nHandleLidSwitch=suspend-then-hibernate\n"),
                          ("etc/elogind/sleep.conf.d/60-pustota-hibernate.conf",
                           "[Sleep]\nHibernateDelaySec=2h\n")):
            (TARGET / rel).parent.mkdir(parents=True, exist_ok=True)
            (TARGET / rel).write_text("# written by the Pustota installer (swap = RAM)\n" + text)
    chroot("xbps-reconfigure", "-fa")
    chroot("grub-install", "--target=x86_64-efi", "--efi-directory=/boot/efi",
           "--bootloader-id=Pustota", "--recheck")
    # also the removable path, which firmware boots even if its boot list was reset
    chroot("grub-install", "--target=x86_64-efi", "--efi-directory=/boot/efi",
           "--removable", "--no-nvram", "--recheck")
    chroot("grub-mkconfig", "-o", "/boot/grub/grub.cfg")

    cfg = (TARGET / "boot/grub/grub.cfg").read_text()
    kernels = sorted((TARGET / "boot").glob("vmlinuz-7.*"))
    if not kernels:
        raise RuntimeError("no 7.x kernel in /boot")
    version = kernels[-1].name[len("vmlinuz-"):]
    if not (TARGET / f"boot/initramfs-{version}.img").is_file():
        raise RuntimeError(f"no initramfs for {version}")
    if f"vmlinuz-{version}" not in cfg:
        raise RuntimeError(f"GRUB menu does not list {version}")
    if not (TARGET / "boot/efi/EFI/BOOT/BOOTX64.EFI").is_file():
        raise RuntimeError("EFI fallback loader missing")
    log(f"installed: kernel {version}, swap {swap_gib} GiB, user {username}")
    return version


def main():
    if os.geteuid() != 0:
        raise SystemExit("run it with sudo: sudo pustota-installer")
    if not Path("/sys/firmware/efi").is_dir():
        notice("This computer started the installer in legacy BIOS mode.\n\n"
               "Pustota installs for UEFI only: restart, choose the USB stick's UEFI entry "
               "in the boot menu, and keep Secure Boot off.")
        return 2
    if not (REPO / "x86_64-repodata").is_file():
        raise SystemExit("Pustota's packages are missing from the ISO")
    if sp.run(["mountpoint", "-q", str(TARGET)]).returncode == 0:
        raise SystemExit("/mnt/target is already mounted: reboot and start again")

    available = disks()
    if not available:
        notice(f"No unmounted disk of at least {MIN_ROOT_GIB + EFI_GIB} GiB was found.")
        return 2
    notice("Пустота / Pustota\n\nVoid Linux, runit, XFS, ratpoison and Plan 9 tools: light, "
           "quick and kind to the battery.\n\nThe installer asks five questions, then one "
           "Yes/No. Choosing Yes erases the whole disk you picked.")
    options = [(d["path"], f"{int(d['size']) / GiB:.0f} GiB  {(d.get('model') or 'disk').strip()[:40]}")
               for d in available]
    disk = choice("Install Pustota on which disk?", options)
    hostname = input_field("Computer name:", "pustota")
    if not HOSTNAME.fullmatch(hostname) or hostname.endswith("-"):
        notice("Use letters, digits and hyphens for the computer name.")
        return 2
    username = input_field("Your username (lower case):")
    if not USERNAME.fullmatch(username) or username == "root":
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

    stage("Checking Void's package repository...")
    try:
        check_repository()
    except RuntimeError as error:
        notice(str(error))
        return 2
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
              f"{root_gib} GiB XFS\n  GRUB (UEFI)   computer: {hostname}   user: {username}\n"
              f"  {'automatic login' if autologin else 'password at login'}   {timezone}", 15, 80) != 0:
        notice("Cancelled. Nothing has been changed.")
        return 1
    if disk not in {d["path"] for d in disks()}:
        notice("The disk changed. Nothing has been changed.")
        return 2

    LOGFILE.write_text("Pustota installation\n")
    try:
        version = install(disk, hostname, username, password, timezone, autologin)
    except (sp.CalledProcessError, RuntimeError, OSError, ValueError) as error:
        failure_dialog(error)
        cleanup()
        return 1
    finally:
        password = ""
    shutil.copy2(LOGFILE, TARGET / "var/log/pustota-install.log")
    cleanup()
    notice(f"Pustota is installed (Linux {version}).\n\nRemove the USB stick and reboot:  "
           "sudo reboot\n\nAfter logging in, press Super+? for the keys, or run  pustota-learn")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (KeyboardInterrupt, InterruptedError):
        print("\nInstaller cancelled. Nothing more was changed.", file=sys.stderr)
        sys.exit(1)
