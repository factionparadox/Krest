#!/usr/bin/env bash
# Publish Pustota's package repository (after a build) as the GitHub release "repo-x86_64":
# every .xbps, its .sig2 signature and the signed index. Installed systems read it from
#   https://github.com/factionparadox/Pustota/releases/download/repo-x86_64
# (/usr/share/xbps.d/20-pustota-repository.conf), so  sudo xbps-install -Su  updates Pustota's
# packages along with Void's. Needs the GitHub CLI, signed in:  gh auth login
set -Eeuo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
repo=$root/build/work/repo
tag=repo-x86_64
die() { printf 'publish-repo: %s\n' "$*" >&2; exit 2; }
command -v gh >/dev/null || die 'the GitHub CLI is not installed (Arch: sudo pacman -S github-cli; Void: sudo xbps-install github-cli)'
[[ -s $repo/x86_64-repodata ]] || die "build first: bash build/build-iso.sh"
ls "$repo"/*.sig2 >/dev/null 2>&1 || die "the repository is not signed (build/sign-repo.sh)"
cd "$root"
if ! gh release view "$tag" >/dev/null 2>&1; then
  gh release create "$tag" --title "Pustota package repository (x86_64)" --notes \
"XBPS repository for Pustota: its own packages (pustota-*) and packages Void does not have
(ani-cli, ollama-bin), built with xbps-src from srcpkgs/ and signed.
Installed systems use it automatically. Do not download these by hand."
fi
gh release upload "$tag" "$repo"/x86_64-repodata "$repo"/*.xbps "$repo"/*.sig2 --clobber
echo "published: https://github.com/factionparadox/Pustota/releases/tag/$tag"
