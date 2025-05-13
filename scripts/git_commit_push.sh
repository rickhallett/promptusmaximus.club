#!/bin/bash

# Script to stage all changes, commit with a conventional message (provided as argument), and push.

# Check if commit message argument is provided
if [ -z "$1" ]; then
  echo "Error: Commit message is required."
  echo "Usage: ./scripts/git_commit_push.sh \"<your conventional commit message>\""
  exit 1
fi

COMMIT_MESSAGE="$1" # Use the first argument as the commit message

echo "Staging all changes..."
git add -A # Stages all changes (new, modified, deleted)

# Check if there's anything to commit
if git diff-index --quiet HEAD --; then
  echo "No changes to commit."
  exit 0
fi

echo "Committing with message: $COMMIT_MESSAGE"
git commit -m "$COMMIT_MESSAGE"

# Check if commit was successful
if [ $? -ne 0 ]; then
  echo "Git commit failed. Aborting push."
  # Attempt to unstage if commit failed, though 'git add -A' makes this tricky
  # For simplicity, we'll leave files staged. Manual intervention might be needed.
  exit 1
fi

echo "Pushing to remote..."
git push

if [ $? -ne 0 ]; then
  echo "Git push failed."
  exit 1
fi

echo "Successfully staged, committed, and pushed all changes."
exit 0 