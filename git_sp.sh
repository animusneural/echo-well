#!/usr/bin/env bash
# git_sp.sh – stage, commit, and push in one go

if [ $# -gt 0 ]; then
  MSG="$*"
else
  read -p "Commit message: " MSG
fi

git add .
git commit -m "$MSG"
git push -u origin main
