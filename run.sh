#!/bin/bash

SHORT_FAILURE_LINES=6

expand_home() {
  printf '%s' "${1/#\~/$HOME}"
}

dir=$(expand_home "${decks_dir:-~/decks}")
bin=$(expand_home "${decks_bin:-~/.local/bin/decks}")

json_escape() {
  local s
  s=$(printf '%s' "$1" | tr -d '\000-\010\013-\037')
  s=${s//\\/\\\\}
  s=${s//\"/\\\"}
  s=${s//$'\t'/\\t}
  s=${s//$'\n'/\\n}
  printf '%s' "$s"
}

show() {
  printf '{"alfredworkflow":{"arg":"%s","variables":{"show":"%s"}}}\n' "$(json_escape "$2")" "$1"
  exit 0
}

show_as_code() {
  show view '```'$'\n'"$1"$'\n''```'
}

line_count() {
  printf '%s\n' "$1" | wc -l | tr -d ' '
}

last_line() {
  printf '%s\n' "$1" | awk 'NF { line = $0 } END { print line }'
}

require_decks() {
  [[ -x "$bin" ]] || show large "decks not found at $bin. Set its path in the workflow configuration."
}

announce() {
  osascript -e "display notification \"$1\" with title \"Decks\"" >/dev/null 2>&1
}

run_decks() {
  require_decks
  output=$("$bin" "$@" 2>&1)
  status=$?
}

show_failure() {
  if (($(line_count "$output") <= SHORT_FAILURE_LINES)); then
    show large "$output"
  fi
  show_as_code "$output"
}

show_summary() {
  ((status == 0)) || show_failure
  show notify "$(last_line "$output")"
}

long_running() {
  announce "$1 started"
  shift
  run_decks "$@" --dir "$dir"
  show_summary
}

show_status() {
  run_decks status --dir "$dir"
  ((status == 0)) || show_failure
  show_as_code "$output"
}

add_card() {
  [[ -n "${card//[[:space:]]/}" ]] || show large "Nothing to add."
  run_decks add --dir "$dir" -- "$card"
  ((status == 0)) && show notify "$(last_line "$output")"
  printf '%s' "$card" | pbcopy
  show large "$output"$'\n\n'"Nothing was added. Your text is on the clipboard."
}

open_log() {
  local log="$dir/toanki/decks.log"
  [[ -f "$log" ]] || show large "No log yet at $log"
  open "$log"
  show none ""
}

open_folder() {
  open "$dir"
  show none ""
}

case "$action" in
  sync) long_running "Sync" sync ;;
  build) long_running "Build" build ;;
  rebuild) long_running "Rebuild" rebuild ;;
  force) long_running "Forced sync" sync --force ;;
  status) show_status ;;
  add) add_card ;;
  log) open_log ;;
  folder) open_folder ;;
  *) show large "Unknown action: $action" ;;
esac
