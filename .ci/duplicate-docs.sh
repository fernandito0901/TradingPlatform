#!/bin/bash
set -e
# Fail if duplicate top-level README/CHANGELOG/NOTES exist
# Uses git ls-files to detect duplicates

dupes=$(git ls-files | sort | uniq -d | grep -E 'README|CHANGELOG|NOTES' || true)
if [ -n "$dupes" ]; then
  echo "❌ Duplicate docs:" >&2
  echo "$dupes" >&2
  exit 1
fi
