#!/bin/sh
# Builds the zip haxofi.com/verificadas/ offers (and the Chrome Web Store takes): the manifest, the script, the icons.
set -e
cd "$(dirname "$0")"
out=../docs/verificadas/haxofi-salas-verificadas.zip
rm -f "$out"
bsdtar -a -cf "$out" manifest.json verified.js icons/16.png icons/48.png icons/128.png
echo "$out"
