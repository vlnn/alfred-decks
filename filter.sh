#!/bin/bash

query="$1"
verb="${query%% *}"
text=""
[[ "$query" == *" "* ]] && text="${query#* }"
items=""

json_escape() {
  local s=$1
  s=${s//\\/\\\\}
  s=${s//\"/\\\"}
  s=${s//$'\t'/\\t}
  printf '%s' "$s"
}

append() {
  items="${items:+$items,}$1"
}

item() {
  local action=$1 title=$2 subtitle=$3 valid=${4:-true} card=${5:-} complete=$1
  [[ "$action" == edit ]] && complete="add "
  printf '{"title":"%s","subtitle":"%s","arg":"%s","valid":%s,"autocomplete":"%s","variables":{"action":"%s","card":"%s"}' \
    "$title" "$(json_escape "$subtitle")" "$action" "$valid" "$complete" "$action" "$(json_escape "$card")"
}

plain_item() {
  append "$(item "$@")}"
}

guarded_item() {
  local action=$1 title=$2 subtitle=$3
  append "$(item "$action" "$title" "Hold ⌘ and press ↩: $subtitle" false),\"mods\":{\"cmd\":{\"valid\":true,\"subtitle\":\"$subtitle\"}}}"
}

typed() {
  [[ "$1" == "$verb"* ]]
}

add_item() {
  if [[ -z "$text" ]]; then
    append "$(item edit "Add card" "Open the editor: a cloze, or Q: and A: lines")}"
  elif [[ "$text" == *"{{c"*"::"*"}}"* ]]; then
    plain_item add "Add cloze card" "$text" true "$text"
  else
    plain_item add "Add card" "A one-liner needs a cloze like {{c1::gap}}; use plain 'decks add' for the editor" false "$text"
  fi
}

typed sync && plain_item sync "Sync decks" "Build if needed, import into Anki, remove orphans, sync AnkiWeb"
typed build && plain_item build "Build decks" "Build changed decks and new inbox packages into toanki"
typed status && plain_item status "Status" "Show what a sync would do"
typed add && add_item
typed rebuild && guarded_item rebuild "Rebuild everything" "Rebuild every deck from scratch and regenerate all audio"
typed force && guarded_item force "Sync with force" "Sync and allow large deletions"
typed log && plain_item log "Open log" "Open the last run's full output"
typed folder && plain_item folder "Open decks folder" "Show the decks directory in Finder"

printf '{"items":[%s]}\n' "$items"
