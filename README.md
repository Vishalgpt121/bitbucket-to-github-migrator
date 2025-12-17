# Bitbucket to GitHub Migration Tool 🚀

A set of automated scripts to bulk migrate all repositories from Bitbucket to GitHub (including commit history, branches, and tags). 

**Why this exists:** Bitbucket is deleting inactive free workspaces/repos starting **January 15, 2026**. This tool helps you evacuate your code to GitHub quickly.

## Features
- **Zero Cost:** Uses Bitbucket OAuth Consumer (Free tier compatible).
- **Automated:** Fetches all repos, creates them on GitHub, and pushes history.
- **Smart:** Automatically fixes the `GH002` error (ambiguous 40-char branch names) that often blocks migrations.
- **Remote Updater:** Includes a script to update your local working directories to point to the new GitHub location.

## Prerequisites
- Python 3 (`pip install requests`)
- Git installed

## Setup

### 1. Get GitHub Credentials
1. Go to **Settings > Developer settings > Personal access tokens > Tokens (classic)**.
2. Generate a new token with `repo` scope.

### 2. Get Bitbucket Credentials (Free Method)
1. Go to Bitbucket **Workspace settings** (NOT personal settings).
2. Navigate to **Apps and features > OAuth consumers**.
3. Click **Add consumer**:
   - **Name:** `MigrationBot`
   - **Callback URL:** `http://localhost`
   - **Permissions:** Check `Account:Read` and `Repositories:Read`.
   - **IMPORTANT:** Check the box **"This is a private consumer"** (otherwise auth will fail).
4. Save and copy the **Key** and **Secret**.

## Usage

### Step 1: Migrate Repositories
1. Open `migrate.py`.
2. Fill in the `CONFIGURATION` section at the top.
3. Run: `python3 migrate.py`.

### Step 2: Update Local Projects
1. Open `update_remotes.py`.
2. Set `WORK_DIR` to your local code folder (e.g., `~/workspace`).
3. Run: `python3 update_remotes.py`.

## Notes
- All repositories are created as **Private** on GitHub by default.
- This script uses `git clone --mirror` to ensure 100% of your history is preserved.
