#!/usr/bin/env bash
# Sign Pustota's package repository (build/work/repo) and export its public key as a trusted
# XBPS key, ready for the live image (and from there, every installed system).
#   sign-repo.sh REPO PRIVATE-KEY.pem OUT-KEYS-DIR
# XBPS insists on signatures for any repository fetched over the network, which is how
# installed systems will update Pustota's packages (from the GitHub release, publish-repo.sh).
set -Eeuo pipefail
repo=$1 key=$2 out=$3
die() { printf 'sign-repo: %s\n' "$*" >&2; exit 2; }
[[ -s $repo/x86_64-repodata ]] || die "no repository index in $repo"
[[ -s $key ]] || die "no private key at $key"
xbps-rindex --sign --signedby "Pustota <pustota@localhost>" --privkey "$key" "$repo"
xbps-rindex --sign-pkg --privkey "$key" "$repo"/*.xbps

# The trusted-key file (/var/db/xbps/keys/FINGERPRINT.plist) is XBPS's own format: let XBPS
# write it, by importing the key from the repository served on this computer for a moment.
tmp=$(mktemp -d)
port=$(( 20000 + RANDOM % 20000 ))
python3 -m http.server --bind 127.0.0.1 --directory "$repo" "$port" >/dev/null 2>&1 &
server=$!
trap 'kill $server 2>/dev/null; rm -rf "$tmp"' EXIT
for _ in $(seq 50); do python3 -c "import socket; socket.create_connection(('127.0.0.1', $port), 0.2)" 2>/dev/null && break; sleep 0.1; done
printf 'y\ny\n' | xbps-install -r "$tmp" -S --repository="http://127.0.0.1:$port" >/dev/null 2>&1 || true
mkdir -p "$out"
found=0
for plist in "$tmp"/var/db/xbps/keys/*.plist; do
  [[ -e $plist ]] || continue
  cp "$plist" "$out/"; found=1
  echo "    trusted key: $(basename "$plist")"
done
[[ $found == 1 ]] || die "XBPS did not import the repository key"
