#!/bin/bash

# Print a message indicating the start of the script
echo "Starting Git update process..."

# Step 1: Show the Git status
echo "Getting Git status..."
git status
echo "-----------------------------"

# Step 2: Get the current branch name
current_branch=$(git rev-parse --abbrev-ref HEAD)
echo "Current branch is: $current_branch"
echo "-----------------------------"

# Step 3: Add all changes to staging area
echo "Adding all changes to staging area..."
git add .
if [ $? -eq 0 ]; then
    echo "Successfully added changes."
else
    echo "Failed to add changes."
    exit 1
fi
echo "-----------------------------"

# Step 4: Commit the changes with a message
commit_message="Update changes on branch $current_branch"
echo "Committing changes with message: $commit_message"
git commit -m "$commit_message"
if [ $? -eq 0 ]; then
    echo "Changes committed successfully."
else
    echo "Commit failed."
    exit 1
fi
echo "-----------------------------"

# Step 5: Push changes to the remote repository
echo "Pushing changes to remote repository..."
git push origin "$current_branch"
if [ $? -eq 0 ]; then
    echo "Changes pushed successfully to $current_branch."
else
    echo "Push failed."
    exit 1
fi

# End of script
echo "Git update process completed."