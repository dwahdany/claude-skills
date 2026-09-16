#!/bin/sh
# Mux an SRT into a copy of an MKV as an additional subtitle track, verify by round-trip extraction.
# Usage: mux.sh ORIG.mkv NEW.srt LANG TITLE OUT.mkv [--default]
#   LANG   ISO 639-2 code (rus, deu, ...); TITLE  track title shown in players
#   --default  make the new track the default subtitle and clear the flag on the others
# Never touches ORIG. Refuses to overwrite an existing OUT. Requires ffmpeg/ffprobe (nix-shell -p ffmpeg) and uv.
set -e
ORIG="$1"; SRT="$2"; LANG="$3"; TITLE="$4"; OUT="$5"; DEFAULT="$6"
[ -e "$OUT" ] && { echo "refusing to overwrite existing $OUT"; exit 1; }
NSUB=$(ffprobe -v error -select_streams s -show_entries stream=index -of csv=p=0 "$ORIG" | grep -c .)
DISP=""
if [ "$DEFAULT" = "--default" ]; then
  k=0; while [ $k -lt "$NSUB" ]; do DISP="$DISP -disposition:s:$k 0"; k=$((k+1)); done
  DISP="$DISP -disposition:s:$NSUB default"
else
  DISP="-disposition:s:$NSUB 0"
fi
ffmpeg -v error -i "$ORIG" -i "$SRT" -map 0 -map 1:0 -c copy \
  -metadata:s:s:$NSUB language="$LANG" -metadata:s:s:$NSUB title="$TITLE" $DISP "$OUT"
NEWIDX=$(ffprobe -v error -select_streams s -show_entries stream=index -of csv=p=0 "$OUT" | tail -1)
TMP=$(mktemp -t roundtrip).srt
ffmpeg -v error -y -i "$OUT" -map 0:"$NEWIDX" -c:s srt "$TMP"
uv run --quiet --with srt python -c "
import srt, sys
a = list(srt.parse(open('$SRT', encoding='utf-8').read())); b = list(srt.parse(open('$TMP', encoding='utf-8').read()))
ok = len(a) == len(b) and all(x.start == y.start and x.end == y.end and x.content.strip() == y.content.strip() for x, y in zip(a, b))
print('roundtrip', len(a), len(b), 'OK' if ok else 'MISMATCH'); sys.exit(0 if ok else 1)"
rm -f "$TMP"
ffprobe -v error -show_entries stream=index,codec_type,codec_name:stream_tags=language,title:stream_disposition=default -of compact "$OUT" | grep subtitle
ls -la "$OUT"
