#!/usr/bin/env sh
# Print a working Chrome or Chromium path, or explain what to install.
#
#   CHROME=$(tools/find-chrome.sh) || exit 1
#
# This exists because the path used to be hardcoded to one Playwright build
# number. A routine upgrade moved that directory and the entire toolchain
# stopped working with "No such file or directory", which gives no hint that
# Chrome is the missing piece. Resolve it at run time instead.
#
# Order: an explicit $CHROME, then any Playwright build newest first, then the
# usual system locations on macOS, Linux and Git Bash on Windows.
set -u

try () { [ -n "${1:-}" ] && [ -x "$1" ] && { echo "$1"; exit 0; }; }

# 1. explicit override always wins
try "${CHROME:-}"

# 2. Playwright caches. Full Chromium before the headless shell, because the
#    layout extractor drives the DevTools protocol and the full build is the
#    one that is guaranteed to carry it. Newest build number first within each
#    kind: ls -v sorts numerically, tac puts the highest on top.
for base in "$HOME/.cache/ms-playwright" \
            "$HOME/Library/Caches/ms-playwright" \
            "${LOCALAPPDATA:-}/ms-playwright"; do
  [ -d "$base" ] || continue
  for dir in $(ls -1v "$base" 2>/dev/null | grep -E '^chromium-[0-9]+$' | tac); do
    try "$base/$dir/chrome-linux64/chrome"
    try "$base/$dir/chrome-linux/chrome"
    try "$base/$dir/chrome-mac/Chromium.app/Contents/MacOS/Chromium"
    try "$base/$dir/chrome-win/chrome.exe"
  done
done
for base in "$HOME/.cache/ms-playwright" \
            "$HOME/Library/Caches/ms-playwright" \
            "${LOCALAPPDATA:-}/ms-playwright"; do
  [ -d "$base" ] || continue
  for dir in $(ls -1v "$base" 2>/dev/null | grep -E '^chromium_headless_shell-[0-9]+$' | tac); do
    try "$base/$dir/chrome-headless-shell-linux64/chrome-headless-shell"
    try "$base/$dir/chrome-headless-shell-mac/chrome-headless-shell"
    try "$base/$dir/chrome-headless-shell-win64/chrome-headless-shell.exe"
  done
done

# 3. system installs
try "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
try "/Applications/Chromium.app/Contents/MacOS/Chromium"
try "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
try "/c/Program Files/Google/Chrome/Application/chrome.exe"
try "/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
for c in google-chrome-stable google-chrome chromium chromium-browser microsoft-edge; do
  p=$(command -v "$c" 2>/dev/null) && try "$p"
done

cat >&2 <<'MSG'
No Chrome or Chromium found.

The export needs one to render the PDF. Pick whichever is easiest:

  macOS     brew install --cask google-chrome
  Debian    sudo apt install chromium
  anywhere  npx playwright install chromium

Already have one somewhere unusual? Point at it directly:

  CHROME=/path/to/chrome ./build.sh
MSG
exit 1
