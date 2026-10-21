#!/usr/bin/env sh
# Render <name>.render.html -> <name>.png at 2x using headless Chrome in Docker, then crop
# to the exact diagram size (Chrome's viewport is shorter than --window-size, so we render
# with padding and trim). Everything runs in containers; nothing is installed on the host.
#
#   render.sh <out_dir> <name> <width> <height>
#   e.g. render.sh ./out architecture 2280 1720   -> out/architecture.png (4560x3440)
set -eu
OUT=$(cd "$1" && pwd); NAME=$2; W=$3; H=$4
PAD_H=$((H + 200))
CHROME=zenika/alpine-chrome:124
PY=python:3.12-slim

docker run --rm -v "$OUT":/work -w /work "$CHROME" \
  --headless=new --no-sandbox --disable-gpu --disable-dev-shm-usage --hide-scrollbars \
  --force-device-scale-factor=2 --window-size="$W,$PAD_H" --timeout=20000 \
  --screenshot=/work/"$NAME".raw.png "file:///work/$NAME.render.html"

docker run --rm -v "$OUT":/work -w /work "$PY" sh -c \
  "pip install -q pillow >/dev/null && python - <<PYEOF
from PIL import Image
im = Image.open('$NAME.raw.png')
im.crop((0, 0, $W * 2, $H * 2)).save('$NAME.png', optimize=True)
print('$NAME.png', $W * 2, 'x', $H * 2)
PYEOF"
rm -f "$OUT/$NAME.raw.png"
