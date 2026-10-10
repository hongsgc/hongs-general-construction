#!/bin/zsh
# Render signature.html to PNG at 1x (Gmail upload) and 2x (sharp on high-res screens).
cd "${0:A:h}"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
for s in 1 2; do
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --allow-file-access-from-files \
    --force-device-scale-factor=$s --window-size=480,160 --virtual-time-budget=3000 \
    --screenshot="$PWD/hongs-signature@${s}x.png" "file://$PWD/signature.html" 2>/dev/null
done
ls -la hongs-signature@*.png
