#!/usr/bin/env bash
# bb-setup.sh — one-time: store the BuchhaltungsButler API credentials in Bitwarden and verify them.
# Run this yourself in a terminal (it prompts interactively). Nothing is written to disk.
#
#   scripts/bb-setup.sh [--item "BuchhaltungsButler API"]
#
# Creates (or updates) a Bitwarden login item:
#   username      = API Client
#   password      = API Secret
#   field api_key = API Key   (hidden custom field)
# The values are shown in BuchhaltungsButler under Einstellungen → Schnittstellen und API-Zugang.
# BW_SESSION reaches bw through the environment only, never as a command-line argument.
set -euo pipefail

ITEM="${BB_BW_ITEM:-BuchhaltungsButler API}"
[[ "${1:-}" == "--item" ]] && ITEM="${2:?--item needs a name}"
HERE="$(cd "$(dirname "$0")" && pwd)"

die() { printf 'bb-setup: %s\n' "$*" >&2; exit 1; }
command -v jq >/dev/null || die "jq is required"
[[ -t 0 ]] || die "needs an interactive terminal: run scripts/bb-setup.sh yourself, not from the agent"

bw_run() {
  if command -v bw >/dev/null 2>&1; then bw "$@"
  elif command -v nix-shell >/dev/null 2>&1; then
    local q=() a; for a in "$@"; do q+=("$(printf '%q' "$a")"); done
    nix-shell -p bitwarden-cli --run "bw ${q[*]}"
  else die "Bitwarden CLI 'bw' not found. Install it (brew install bitwarden-cli / npm i -g @bitwarden/cli) or install nix."; fi
}

status="$(bw_run status | jq -r .status)"
case "$status" in
  unauthenticated)
    cat >&2 <<'MSG'
Bitwarden CLI is not logged in. Log in first, then re-run this script:
  bw config server https://YOUR-SERVER      # only for a self-hosted vault; skip for bitwarden.com
  bw login                                  # or: bw login --apikey  (BW_CLIENTID/BW_CLIENTSECRET)
MSG
    exit 1 ;;
  locked)
    [[ -n "${BW_SESSION:-}" ]] && echo "BW_SESSION is set but the vault reports locked (stale key) — unlocking again."
    echo "Vault is locked — unlocking (this only affects the current run)."
    BW_SESSION="$(bw_run unlock --raw)"; export BW_SESSION ;;
  unlocked) export BW_SESSION ;;
  *) die "unexpected bw status: $status" ;;
esac
[[ -n "${BW_SESSION:-}" ]] || die "no BW_SESSION; run: export BW_SESSION=\"\$(bw unlock --raw)\""

bw_run sync >/dev/null

echo "Enter the three values from BuchhaltungsButler → Einstellungen → Schnittstellen und API-Zugang."
read -r -p "API Client: " api_client
read -r -s -p "API Secret (hidden): " api_secret; echo
read -r -s -p "API Key (hidden): " api_key; echo
[[ -n "$api_client" && -n "$api_secret" && -n "$api_key" ]] || die "all three values are required"

# Secrets go to jq through the environment ($ENV.*), never as command-line arguments.
export BBS_CLIENT="$api_client" BBS_SECRET="$api_secret" BBS_KEY="$api_key" BBS_ITEM="$ITEM"
unset api_client api_secret api_key
matches="$(bw_run list items --search "$ITEM" | jq -c '[.[] | select(.name == $ENV.BBS_ITEM)]')"
case "$(jq 'length' <<<"$matches")" in
  0)
    echo "Creating item \"$ITEM\"."
    bw_run get template item \
      | jq '.type = 1 | .name = $ENV.BBS_ITEM
            | .notes = "BuchhaltungsButler API v1 credentials. Used by the buchhaltungsbutler Claude Code skill (scripts/bb.sh)."
            | .login = {username: $ENV.BBS_CLIENT, password: $ENV.BBS_SECRET, uris: [{match: null, uri: "https://app.buchhaltungsbutler.de/"}]}
            | .fields = [{name: "api_key", value: $ENV.BBS_KEY, type: 1}]' \
      | bw_run encode | bw_run create item >/dev/null ;;
  1)
    echo "Item \"$ITEM\" exists — updating it."
    id="$(jq -r '.[0].id' <<<"$matches")"
    jq '.[0] | .login.username = $ENV.BBS_CLIENT | .login.password = $ENV.BBS_SECRET
        | .fields = ([.fields[]? | select(.name != "api_key")] + [{name: "api_key", value: $ENV.BBS_KEY, type: 1}])' <<<"$matches" \
      | bw_run encode | bw_run edit item "$id" >/dev/null ;;
  *) die "several Bitwarden items are named \"$ITEM\" — rename them or pass --item <unique name>" ;;
esac
unset BBS_CLIENT BBS_SECRET BBS_KEY BBS_ITEM matches

echo "Stored. Verifying against the API..."
env -u BB_API_CLIENT -u BB_API_SECRET -u BB_API_KEY BB_BW_ITEM="$ITEM" "$HERE/bb.sh" --check
cat <<'MSG'

Done. For the skill to use these credentials, the agent's shell needs an unlocked vault:
  export BW_SESSION="$(bw unlock --raw)"     # then start claude from that shell
MSG
