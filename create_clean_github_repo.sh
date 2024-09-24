#!/bin/bash

# Define the destination directory in ~/Public
PUBLIC_DIR=~/Public
DIR_NAME=$(basename "$PWD")
DEST_DIR="$PUBLIC_DIR/$DIR_NAME-public"
YOUR_GITHUB_USERNAME="will-abb"
USER_NAME="Will Bosch-Bello"
USER_EMAIL="williamsbosch@gmail.com"
SSH_KEY_PATH="~/.ssh/id_rsa_per"

# Check if gh CLI is installed
if ! command -v gh &>/dev/null; then
    echo "GitHub CLI (gh) could not be found. Please install it and authenticate with 'gh auth login'."
    exit 1
fi

# Ensure the correct SSH key is used for Git operations
export GIT_SSH_COMMAND="ssh -i $SSH_KEY_PATH"

# Create the ~/Public directory if it doesn't exist
if [ ! -d "$PUBLIC_DIR" ]; then
    echo "Creating ~/Public directory..."
    mkdir -p "$PUBLIC_DIR"
fi

# Copy the repository to the ~/Public directory with -public suffix
echo "Copying repository to $DEST_DIR..."
cp -r "$PWD" "$DEST_DIR"

# Navigate to the new destination directory
cd "$DEST_DIR" || {
    echo "Failed to change directory to $DEST_DIR"
    exit 1
}

# Remove the .git directory (if it exists)
if [ -d ".git" ]; then
    echo "Removing existing .git directory..."
    rm -rf .git
fi

# Initialize a new git repository
echo "Initializing a new Git repository in $DEST_DIR..."
git init

# Configure Git user information (if not already configured globally)
git config user.email "$USER_EMAIL"
git config user.name "$USER_NAME"

# Add all files and commit with a descriptive message
echo "Adding files to the new repository..."
git add .

COMMIT_MESSAGE="Deleted all git history to remove all private information. The purpose of this repository is to display my projects and work."
echo "Making initial commit: '$COMMIT_MESSAGE'"
git commit -m "$COMMIT_MESSAGE"

# Check if the repository already exists
REPO_EXISTS=$(gh repo view "$YOUR_GITHUB_USERNAME/$DIR_NAME-public" &>/dev/null && echo "yes" || echo "no")

if [ "$REPO_EXISTS" == "no" ]; then
    # Create a new public GitHub repository if it doesn't exist
    echo "Creating new public GitHub repository: $DIR_NAME-public"
    gh repo create "$DIR_NAME-public" --public --confirm
else
    echo "Repository $DIR_NAME-public already exists on GitHub. Skipping creation."
fi

# Add the new GitHub repository as the remote (using SSH instead of HTTPS)
echo "Adding GitHub remote (using SSH)..."
git remote add origin "git@github.com:$YOUR_GITHUB_USERNAME/$DIR_NAME-public.git"

# Push the changes to the new repository (using 'main' branch)
echo "Pushing changes to GitHub..."
git branch -M main
git push -u origin main

echo "Repository creation and push completed successfully."
