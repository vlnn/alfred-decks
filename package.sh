#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
rm -f Decks.alfredworkflow
zip -q Decks.alfredworkflow info.plist filter.sh run.sh
echo "Decks.alfredworkflow"
