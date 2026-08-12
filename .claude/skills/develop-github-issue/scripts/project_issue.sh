#!/usr/bin/env bash

set -euo pipefail

readonly PROJECT_OWNER="${GITHUB_PROJECT_OWNER:-alexandervivas}"
readonly PROJECT_NUMBER="${GITHUB_PROJECT_NUMBER:-1}"

usage() {
  printf 'Usage:\n'
  printf '  %s inspect <issue-url-or-number>\n' "$0"
  printf '  %s set-status <issue-url-or-number> <Todo|In Progress|Done> [--dry-run]\n' "$0"
}

fail() {
  printf 'Error: %s\n' "$1" >&2
  exit 1
}

resolve_issue() {
  local issue_ref="$1"

  if [[ "$issue_ref" =~ ^https://github.com/([^/]+)/([^/]+)/issues/([0-9]+)/?$ ]]; then
    ISSUE_REPOSITORY="${BASH_REMATCH[1]}/${BASH_REMATCH[2]}"
    ISSUE_NUMBER="${BASH_REMATCH[3]}"
  elif [[ "$issue_ref" =~ ^#?([0-9]+)$ ]]; then
    ISSUE_REPOSITORY="$(gh repo view --json nameWithOwner --jq '.nameWithOwner')"
    ISSUE_NUMBER="${BASH_REMATCH[1]}"
  else
    fail "issue must be a GitHub issue URL or numeric issue number"
  fi

  ISSUE_JSON="$(gh issue view "$ISSUE_NUMBER" \
    --repo "$ISSUE_REPOSITORY" \
    --json number,title,url,state,body,assignees,labels)"
  ISSUE_URL="$(jq -r '.url' <<<"$ISSUE_JSON")"
}

load_project_item() {
  local project_items

  project_items="$(gh project item-list "$PROJECT_NUMBER" \
    --owner "$PROJECT_OWNER" \
    --limit 1000 \
    --format json)"
  PROJECT_ITEM_JSON="$(jq -c --arg url "$ISSUE_URL" \
    '.items[] | select(.content.url == $url)' <<<"$project_items")"

  [[ -n "$PROJECT_ITEM_JSON" ]] || fail "issue is not present in GitHub Project ${PROJECT_OWNER}/${PROJECT_NUMBER}"
}

inspect_issue() {
  local project_summary

  project_summary="$(jq -c '{
    id,
    status,
    refinement,
    release,
    deliverySlice: .["delivery Slice"],
    priority,
    area,
    size,
    type,
    productIteration: .["product Iteration"],
    corridor
  }' <<<"$PROJECT_ITEM_JSON")"

  jq -n \
    --arg projectOwner "$PROJECT_OWNER" \
    --argjson projectNumber "$PROJECT_NUMBER" \
    --argjson issue "$ISSUE_JSON" \
    --argjson projectItem "$project_summary" \
    '{project: {owner: $projectOwner, number: $projectNumber}, issue: $issue, projectItem: $projectItem}'
}

set_project_status() {
  local requested_status="$1"
  local dry_run="${2:-}"
  local project_id
  local fields_json
  local status_field_id
  local status_option_id
  local project_item_id

  case "$requested_status" in
    "Todo" | "In Progress" | "Done") ;;
    *) fail "status must be Todo, In Progress, or Done" ;;
  esac

  project_id="$(gh project view "$PROJECT_NUMBER" --owner "$PROJECT_OWNER" --format json --jq '.id')"
  fields_json="$(gh project field-list "$PROJECT_NUMBER" --owner "$PROJECT_OWNER" --format json)"
  status_field_id="$(jq -r '.fields[] | select(.name == "Status") | .id' <<<"$fields_json")"
  status_option_id="$(jq -r --arg status "$requested_status" \
    '.fields[] | select(.name == "Status") | .options[] | select(.name == $status) | .id' <<<"$fields_json")"
  project_item_id="$(jq -r '.id' <<<"$PROJECT_ITEM_JSON")"

  [[ -n "$status_field_id" && "$status_field_id" != "null" ]] || fail "project Status field was not found"
  [[ -n "$status_option_id" && "$status_option_id" != "null" ]] || fail "project status option was not found"

  if [[ "$dry_run" == "--dry-run" ]]; then
    printf 'Would set %s to %s in GitHub Project %s/%s\n' \
      "$ISSUE_URL" "$requested_status" "$PROJECT_OWNER" "$PROJECT_NUMBER"
    return
  fi

  [[ -z "$dry_run" ]] || fail "unknown option: $dry_run"

  gh project item-edit \
    --id "$project_item_id" \
    --project-id "$project_id" \
    --field-id "$status_field_id" \
    --single-select-option-id "$status_option_id" >/dev/null

  printf 'Set %s to %s in GitHub Project %s/%s\n' \
    "$ISSUE_URL" "$requested_status" "$PROJECT_OWNER" "$PROJECT_NUMBER"
}

[[ $# -ge 2 ]] || {
  usage >&2
  exit 2
}

readonly COMMAND="$1"
readonly ISSUE_REFERENCE="$2"

resolve_issue "$ISSUE_REFERENCE"
load_project_item

case "$COMMAND" in
  inspect)
    [[ $# -eq 2 ]] || fail "inspect accepts exactly one issue reference"
    inspect_issue
    ;;
  set-status)
    [[ $# -ge 3 && $# -le 4 ]] || fail "set-status requires an issue, a status, and optional --dry-run"
    set_project_status "$3" "${4:-}"
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac
