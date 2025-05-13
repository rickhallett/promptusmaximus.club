#!/bin/bash

# Script to stage only modified files, commit with a conventional message (provided as argument), and push.

# Check if commit message argument is provided
if [ -z "$1" ]; then
  echo "Error: Commit message is required."
  echo "Usage: ./git_commit_modified.sh \"<your conventional commit message>\""
  exit 1
fi

COMMIT_MESSAGE="$1" # Use the first argument as the commit message

# Identify modified files
# Using git diff --name-only --cached to see what's staged, and git diff --name-only for unstaged modifications
# More robustly, let's check status first
MODIFIED_FILES=$(git status --porcelain | grep '^ M' | awk '{print $2}')

if [ -z "$MODIFIED_FILES" ]; then
  echo "No modified files to commit."
  exit 0
fi

echo "Staging modified files:"
# Loop through modified files and add them
OLD_IFS="$IFS"
IFS=$'\n'
for FILE in $MODIFIED_FILES; do
  echo "  Adding $FILE"
  git add "$FILE"
done
IFS="$OLD_IFS"

# Commit the changes using the provided message
echo "Committing with message: $COMMIT_MESSAGE"
git commit -m "$COMMIT_MESSAGE"

# Check if commit was successful
if [ $? -ne 0 ]; then
  echo "Git commit failed. Aborting push."
  exit 1
fi

# Push the changes
echo "Pushing to remote..."
git push

if [ $? -ne 0 ]; then
  echo "Git push failed."
  exit 1
fi

echo "Successfully staged modified files, committed, and pushed."
exit 0 