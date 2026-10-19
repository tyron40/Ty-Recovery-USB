#!/bin/sh
# Run with sh Start-Recovery.sh; no executable bit or root access required.
set -eu
cd -- "$(dirname -- "$0")"
if command -v python3 >/dev/null 2>&1; then
    exec python3 ./recovery.py "$@"
fi
printf '%s\n' 'Python 3 is unavailable. Open Recovery-Guide.html and select your system manually.'
case "$(uname -s)" in
    Darwin) exec open ./Recovery-Guide.html ;;
    Linux) if command -v xdg-open >/dev/null 2>&1; then exec xdg-open ./Recovery-Guide.html; fi ;;
esac
