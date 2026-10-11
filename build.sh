#!/usr/bin/env bash
# Build every deliverable from the HTML sources.
#
#   ./build.sh            everything
#   ./build.sh slides     the deck and the chart gallery
#   ./build.sh paper      the paper
#   ./build.sh docs       the README screenshots and mockups
#
# Needs: a Chromium build, poppler (pdftoppm, pdfinfo), Node 22+,
#        and a Python with python-pptx (see tools/requirements.txt).
set -euo pipefail
cd "$(dirname "$0")"

CHROME=$(tools/find-chrome.sh) || exit 1
PY="${PY:-python3}"
WORK="${WORK:-.build}"
WHAT="${1:-all}"
mkdir -p "$WORK"

pdf () {  # pdf <html> <out.pdf>
  "$CHROME" --headless --disable-gpu --no-sandbox \
    --print-to-pdf="$2" --no-pdf-header-footer \
    --virtual-time-budget=12000 "file://$PWD/$1" 2>/dev/null
  echo "   $2  $(pdfinfo "$2" | awk '/Pages/{print $2}') pages"
}

echo "== self-containment =="
"$PY" tools/inline_assets.py --check || exit 1

echo "== shared components =="
"$PY" tools/sync_components.py --check || exit 1

if [ "$WHAT" = all ] || [ "$WHAT" = slides ]; then
  echo "== slides =="
  pdf slides/slides.html slides/slides.pdf
  pdf slides/gallery.html slides/gallery.pdf
  node tools/extract_layout.mjs slides/slides.html "$WORK/slides.json" | sed 's/^/   /'
  "$PY" tools/make_pptx_native.py "$WORK/slides.json" slides/slides.pptx | sed 's/^/   /'
  "$PY" tools/make_pptx.py slides/slides.pdf | sed 's/^/   /'
fi

if [ "$WHAT" = all ] || [ "$WHAT" = paper ]; then
  echo "== paper =="
  pdf paper/paper.html paper/paper.pdf
  pdf paper/onepager.html paper/onepager.pdf
  # One page is the whole format. Nothing else enforces it.
  op=$(pdfinfo paper/onepager.pdf | awk '/Pages/{print $2}')
  if [ "$op" != 1 ]; then
    echo "   FAIL: the one-pager is $op pages. Cut until it is one." >&2
    exit 1
  fi
fi

if [ "$WHAT" = all ] || [ "$WHAT" = docs ]; then
  echo "== README images =="
  "$PY" tools/mockups.py
fi
