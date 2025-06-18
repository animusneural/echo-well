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

#./git_sp.sh RUN THIS FOR GIT COMMIT AND PUSH
# This script stages all changes, commits them with a message, and pushes to the main branch