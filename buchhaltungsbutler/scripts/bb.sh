#!/usr/bin/env bash
# bb.sh — call the BuchhaltungsButler API v1 with credentials pulled from Bitwarden.
#
#   bb.sh <endpoint> [json-body|-]        POST https://webapp.buchhaltungsbutler.de/api/v1/<endpoint>  ('-' = body from stdin)
#                                         by-id endpoints take the id in the path: receipts/get/123, receipts/delete/123,
#                                         receipts/restore/123, transactions/get/123  (spec writes them as .../id_by_customer; verified live)
#   bb.sh --all <endpoint> [json-body]    read endpoint: follow limit/offset paging, merge all .data rows
#   bb.sh --upload <file> <type> [json]   receipts/upload with the file base64-encoded (type: 'invoice inbound', ...)
#   bb.sh --check                         verify credentials + connectivity (accounts/get)
#   bb.sh --list-endpoints                print the 54 endpoints with their safety class
#
# Flags:  --write        required for any endpoint that is not read-only
#         --destructive  required for receipts/delete/*, cost-locations/delete, postings/cancel (implies --write)
#         --raw          print the response body unformatted
#         --item NAME    Bitwarden item to read (default: "BuchhaltungsButler API", or $BB_BW_ITEM)
#
# Credentials (in this order):
#   1. env BB_API_CLIENT / BB_API_SECRET / BB_API_KEY  (all three; for CI or one-off use)
#   2. Bitwarden item (login: username = API client, password = API secret, custom field api_key)
#      needs an unlocked vault:  export BW_SESSION="$(bw unlock --raw)"   in the shell that starts the agent.
# The script never prints credentials. Exit codes: 0 success, 1 API/usage error, 2 credentials unavailable.

set -euo pipefail

BASE_URL="${BB_BASE_URL:-https://webapp.buchhaltungsbutler.de/api/v1}"
ITEM="${BB_BW_ITEM:-BuchhaltungsButler API}"
WRITE=0 DESTRUCTIVE=0 RAW=0 MODE='call'
ENDPOINT='' BODY='{}' UPLOAD_FILE='' UPLOAD_TYPE=''

READ_ENDPOINTS=(accounts/get cost-locations/get postings/get receipts/get receipts/get/id_by_customer
  receipts/assigned-transactions/get transactions/get transactions/get/id_by_customer transactions/assigned-receipts/get
  settings/get/debtors settings/get/creditors settings/get/postingaccounts reports/get/bwa reports/get/sums reports/get/sums/ledger)
DESTRUCTIVE_ENDPOINTS=(receipts/delete/id_by_customer cost-locations/delete postings/cancel)
ALL_ENDPOINTS=(receipts/get receipts/get/id_by_customer receipts/add receipts/addBatch receipts/upload
  receipts/delete/id_by_customer receipts/restore/id_by_customer receipts/assigned-transactions/get
  transactions/get transactions/get/id_by_customer transactions/add transactions/addBatch transactions/assign/receipt
  transactions/unassign/receipt transactions/assign-batch/receipt transactions/assigned-receipts/get
  invoices/create invoices/create/e-invoice invoices/create/draft
  postings/get postings/add/receipt postings/add-batch/receipts postings/add/transaction postings/add-batch/transactions
  postings/add/free postings/add-batch/free postings/unconfirm/transaction postings/unconfirm/receipt postings/unconfirm/free
  postings/assign/receipt-to-free-posting postings/cancel
  settings/add/debtor settings/add-batch/debtors settings/add/creditor settings/add-batch/creditors settings/add/postingaccount
  settings/get/debtors settings/get/creditors settings/get/postingaccounts
  settings/update/debtor settings/update/creditor settings/update/postingaccount
  accounts/get accounts/add comments/add
  cost-locations/get cost-locations/add cost-locations/update cost-locations/delete
  reports/create/bwa reports/create/sums reports/get/bwa reports/get/sums reports/get/sums/ledger)

die() { printf 'bb.sh: %s\n' "$*" >&2; exit 1; }
need() { command -v "$1" >/dev/null 2>&1 || die "missing dependency: $1"; }
need curl; need jq

usage() { awk 'NR>1 && !/^#/{exit} NR>1{sub(/^# ?/,""); print}' "$0"; exit "${1:-1}"; }

in_list() { local needle="$1" x; shift; for x in "$@"; do [[ "$x" == "$needle" ]] && return 0; done; return 1; }

# ---------- argument parsing ----------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --write) WRITE=1 ;;
    --destructive) DESTRUCTIVE=1; WRITE=1 ;;
    --raw) RAW=1 ;;
    --item) shift; ITEM="${1:?--item needs a name}" ;;
    --check) MODE='check' ;;
    --all) MODE='all' ;;
    --list-endpoints) MODE='list' ;;
    --upload) MODE='upload'; shift; UPLOAD_FILE="${1:?--upload needs a file}"; shift; UPLOAD_TYPE="${1:?--upload needs a type}" ;;
    -h|--help) usage 0 ;;
    -) BODY='-' ;;
    -*) die "unknown flag $1" ;;
    \{*) BODY="$1" ;;                                   # anything that looks like JSON is the body, wherever it stands
    *) if [[ "$MODE" == 'upload' ]]; then die "unexpected argument '$1' with --upload (the optional body must be JSON)"
       elif [[ -z "$ENDPOINT" ]]; then ENDPOINT="$1"; else BODY="$1"; fi ;;
  esac
  shift
done

if [[ "$MODE" == 'list' ]]; then
  for e in "${ALL_ENDPOINTS[@]}"; do
    cls='write'
    in_list "$e" "${READ_ENDPOINTS[@]}" && cls='read'
    in_list "$e" "${DESTRUCTIVE_ENDPOINTS[@]}" && cls='destructive'
    printf '%-12s %s\n' "$cls" "$e"
  done
  exit 0
fi

[[ "$MODE" == 'check' ]] && { ENDPOINT='accounts/get'; BODY='{}'; }
if [[ "$MODE" == 'upload' ]]; then
  [[ -z "$ENDPOINT" ]] || die "unexpected argument '$ENDPOINT' with --upload (usage: --upload <file> <type> [json])"
  ENDPOINT='receipts/upload'
fi
[[ -n "$ENDPOINT" ]] || usage 1

if [[ "$BODY" == '-' ]]; then BODY="$(cat)"; fi
BODY="$(jq -c -s 'if length == 1 and (.[0] | type) == "object" then .[0] else error("not one object") end' <<<"$BODY" 2>/dev/null)" \
  || die "body must be a single JSON object"
if jq -e 'has("api_key")' <<<"$BODY" >/dev/null; then die "do not pass api_key in the body; it is injected from the credential store"; fi

ENDPOINT="${ENDPOINT#/}"; ENDPOINT="${ENDPOINT#api/v1/}"
# The spec names four endpoints ".../id_by_customer"; the real URL carries the record id there: receipts/get/123.
CANON="$ENDPOINT"
if [[ "$ENDPOINT" =~ ^(receipts/get|receipts/delete|receipts/restore|transactions/get)/([0-9]+)$ ]]; then
  CANON="${BASH_REMATCH[1]}/id_by_customer"
elif [[ "$ENDPOINT" == */id_by_customer ]]; then
  # The literal spec path is not a real URL (it answers with an HTML page); the id must be the last path segment.
  die "'$ENDPOINT' needs the record id in the path, e.g. '${ENDPOINT%/id_by_customer}/123'"
fi
in_list "$CANON" "${ALL_ENDPOINTS[@]}" || die "unknown endpoint '$ENDPOINT' (see --list-endpoints)"

# ---------- safety gate ----------
if ! in_list "$CANON" "${READ_ENDPOINTS[@]}"; then
  if in_list "$CANON" "${DESTRUCTIVE_ENDPOINTS[@]}"; then
    [[ "$DESTRUCTIVE" == 1 ]] || die "'$ENDPOINT' deletes or cancels data. Confirm with the user, then re-run with --destructive."
  else
    [[ "$WRITE" == 1 ]] || die "'$ENDPOINT' writes to the books. Confirm with the user, then re-run with --write."
  fi
  [[ "$MODE" == 'all' ]] && die "--all is only for read endpoints"
fi

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
chmod 700 "$TMP"

# ---------- credentials ----------
bw_run() {   # BW_SESSION travels in the environment (bw reads it), never on the command line.
  if command -v bw >/dev/null 2>&1; then bw "$@"
  elif command -v nix-shell >/dev/null 2>&1; then
    local q=() a; for a in "$@"; do q+=("$(printf '%q' "$a")"); done
    nix-shell -p bitwarden-cli --run "bw ${q[*]}"
  else die "Bitwarden CLI 'bw' not found (install it, or install nix so it can be fetched with nix-shell)"; fi
}

API_CLIENT="${BB_API_CLIENT:-}" API_SECRET="${BB_API_SECRET:-}" API_KEY="${BB_API_KEY:-}"
if [[ -z "$API_CLIENT" || -z "$API_SECRET" || -z "$API_KEY" ]]; then
  if [[ -z "${BW_SESSION:-}" ]]; then
    cat >&2 <<'MSG'
bb.sh: NOT_UNLOCKED — the Bitwarden vault is not unlocked in this shell.
Ask the user to run, in the terminal that starts the agent:
  export BW_SESSION="$(bw unlock --raw)"        # first time: bw config server <url>; bw login
then retry. (Or export BB_API_CLIENT, BB_API_SECRET, BB_API_KEY instead.)
MSG
    exit 2
  fi
  export BW_SESSION
  bw_list() {   # exact-name matches as a JSON array; a bw failure (locked, logged out, offline) is reported, not hidden
    local out
    if ! out="$(bw_run list items --search "$ITEM" 2>"$TMP/bw_err")"; then
      printf 'bb.sh: BW_ERROR — bw failed: %s\n' "$(tr -d '\n' <"$TMP/bw_err" | head -c 200)" >&2
      # shellcheck disable=SC2016  # the $(...) is meant literally: it is an instruction for the user
      printf 'If the vault is locked or logged out, ask the user to run: export BW_SESSION="$(bw unlock --raw)"  (or: bw login)\n' >&2
      exit 2
    fi
    ITEM="$ITEM" jq -c '[.[] | select(.name == $ENV.ITEM)]' <<<"$out"
  }
  matches="$(bw_list)"
  if [[ "$(jq 'length' <<<"$matches")" == 0 ]]; then
    bw_run sync >/dev/null 2>&1 || true
    matches="$(bw_list)"
  fi
  case "$(jq 'length' <<<"$matches")" in
    1) item_json="$(jq -c '.[0]' <<<"$matches")" ;;
    0) printf 'bb.sh: NO_ITEM — no Bitwarden item named "%s". Ask the user to run scripts/bb-setup.sh once (interactive) to create it, or pass --item <name>.\n' "$ITEM" >&2; exit 2 ;;
    *) printf 'bb.sh: AMBIGUOUS_ITEM — several Bitwarden items are named "%s"; ask the user to rename one, or pass --item.\n' "$ITEM" >&2; exit 2 ;;
  esac
  unset matches
  API_CLIENT="$(jq -r '(.login.username // empty), (.fields[]? | select(.name=="api_client") | .value) | select(type=="string" and . != "")' <<<"$item_json" | head -n1)"
  API_SECRET="$(jq -r '(.login.password // empty), (.fields[]? | select(.name=="api_secret") | .value) | select(type=="string" and . != "")' <<<"$item_json" | head -n1)"
  API_KEY="$(jq -r '.fields[]? | select(.name=="api_key") | .value | select(type=="string" and . != "")' <<<"$item_json" | head -n1)"
  unset item_json
  [[ -n "$API_CLIENT" && -n "$API_SECRET" && -n "$API_KEY" ]] || {
    printf 'bb.sh: BAD_ITEM — item "%s" must have username (API client), password (API secret) and a non-empty custom field api_key.\n' "$ITEM" >&2; exit 2; }
fi

# ---------- request ----------
REPLY_CODE='000'

esc() { printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g'; }

request() { # $1 endpoint, $2 body-json (without api_key). Writes $TMP/resp, sets REPLY_CODE. Credentials never hit argv.
  local ep="$1" body="$2"
  API_KEY="$API_KEY" jq -c '. + {api_key: $ENV.API_KEY}' <<<"$body" > "$TMP/body.json"   # env, not argv: keeps the key out of `ps`
  printf 'user = "%s:%s"\n' "$(esc "$API_CLIENT")" "$(esc "$API_SECRET")" > "$TMP/curl.cfg"
  : > "$TMP/resp"
  # -q first: ignore ~/.curlrc, so a stray -v/--trace there cannot log the Authorization header or the body.
  REPLY_CODE="$(curl -q -sS -K "$TMP/curl.cfg" -X POST "$BASE_URL/$ep" \
      -H 'Content-Type: application/json' -H 'Accept: application/json' \
      --data-binary @"$TMP/body.json" -o "$TMP/resp" -w '%{http_code}' --max-time 120)" || REPLY_CODE='000'
  rm -f "$TMP/body.json" "$TMP/curl.cfg"
}

emit() { # $1 file with response body
  [[ -s "$1" ]] || return 0
  if [[ "$RAW" == 1 ]]; then cat "$1"; echo
  elif jq -e . "$1" >/dev/null 2>&1; then jq . "$1"
  else cat "$1"; echo; fi
}

ok_response() { jq -e '.success == true' "$1" >/dev/null 2>&1; }

if [[ "$MODE" == 'upload' ]]; then
  [[ -f "$UPLOAD_FILE" ]] || die "file not found: $UPLOAD_FILE"
  base64 < "$UPLOAD_FILE" | tr -d '\n' > "$TMP/b64"
  BODY="$(jq -c --rawfile b64 "$TMP/b64" --arg name "$(basename "$UPLOAD_FILE")" --arg type "$UPLOAD_TYPE" \
          '. + {file: $b64, file_name: (.file_name // $name), type: $type}' <<<"$BODY")"
  rm -f "$TMP/b64"
fi

if [[ "$MODE" == 'all' ]]; then
  limit=500 offset=0 total=0
  case "$CANON" in postings/get|cost-locations/get) limit=1000 ;; esac   # these two allow 1000 per page
  : > "$TMP/all.jsonl"
  while :; do
    page="$(jq -c --argjson l "$limit" --argjson o "$offset" '. + {limit: $l, offset: $o}' <<<"$BODY")"
    request "$ENDPOINT" "$page"
    if ! ok_response "$TMP/resp"; then printf 'bb.sh: HTTP %s at offset %s\n' "$REPLY_CODE" "$offset" >&2; emit "$TMP/resp" >&2; exit 1; fi
    n="$(jq '.data | length' "$TMP/resp")"
    jq -c '.data[]?' "$TMP/resp" >> "$TMP/all.jsonl"
    total=$((total + n))
    # Documented page caps: stop on a short page. Undocumented caps (creditors/debtors/postingaccounts): stop on an empty page.
    case "$CANON" in
      receipts/get|transactions/get|postings/get|cost-locations/get) (( n < limit )) && break ;;
      *) (( n == 0 )) && break ;;
    esac
    offset=$((offset + n)); sleep 0.7   # advance by rows actually returned; stay under 100 requests/minute
  done
  jq -s --argjson rows "$total" '{success: true, rows: $rows, data: .}' "$TMP/all.jsonl" > "$TMP/resp"
  emit "$TMP/resp"; exit 0
fi

request "$ENDPOINT" "$BODY"
if [[ "$MODE" == 'check' ]]; then
  if ok_response "$TMP/resp"; then
    printf 'OK — authenticated; %s payment account(s) visible.\n' "$(jq '.data | length' "$TMP/resp")"
    jq -r '.data[]? | "  \(.postingaccount_number // "?")  \(.name // "")"' "$TMP/resp" 2>/dev/null || true
    exit 0
  fi
  printf 'FAILED — HTTP %s\n' "$REPLY_CODE" >&2; emit "$TMP/resp" >&2; exit 1
fi

emit "$TMP/resp"
ok_response "$TMP/resp" || { printf 'bb.sh: request failed (HTTP %s)\n' "$REPLY_CODE" >&2; exit 1; }
