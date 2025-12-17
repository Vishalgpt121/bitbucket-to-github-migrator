import os
import subprocess
import shutil
import requests

# --- CONFIGURATION ---
# Bitbucket OAuth (Workspace Settings > OAuth Consumers)
BB_KEY = "YOUR_BITBUCKET_KEY"
BB_SECRET = "YOUR_BITBUCKET_SECRET"
BB_WORKSPACE = "YOUR_WORKSPACE_ID"

# GitHub PAT (Settings > Developer Settings > Tokens)
GH_USERNAME = "YOUR_GITHUB_USERNAME"
GH_TOKEN = "YOUR_GITHUB_PAT"

# Local temp folder for cloning
TEMP_DIR = "temp_migration_dump"

def get_bb_token(key, secret):
    print("Authenticating with Bitbucket...")
    resp = requests.post(
        "https://bitbucket.org/site/oauth2/access_token",
        auth=(key, secret),
        data={"grant_type": "client_credentials"}
    )
    if resp.status_code != 200:
        raise Exception(f"Bitbucket Auth Failed: {resp.text}")
    return resp.json()["access_token"]

def get_bb_repos(token):
    repos = []
    url = f"https://api.bitbucket.org/2.0/repositories/{BB_WORKSPACE}"
    headers = {"Authorization": f"Bearer {token}"}
    print(f"Fetching repository list from {BB_WORKSPACE}...")
    while url:
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200: break
        data = resp.json()
        repos.extend([r['slug'] for r in data['values']])
        url = data.get('next')
    return repos

def clean_zombie_refs(repo_dir):
    """Deletes 40-char branch names that cause GH002 errors."""
    # List all refs
    result = subprocess.run(["git", "show-ref"], cwd=repo_dir, capture_output=True, text=True)
    for line in result.stdout.splitlines():
        sha, ref = line.split(" ")
        ref_name = ref.split("/")[-1]
        
        # Check if ref name is exactly 40 hex chars (looks like a SHA)
        if len(ref_name) == 40 and all(c in '0123456789abcdef' for c in ref_name):
            print(f"  [Fix] Deleting ambiguous ref: {ref_name}")
            subprocess.run(["git", "update-ref", "-d", ref], cwd=repo_dir)

def migrate():
    if os.path.exists(TEMP_DIR): shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR)
    
    bb_token = get_bb_token(BB_KEY, BB_SECRET)
    repos = get_bb_repos(bb_token)
    print(f"Found {len(repos)} repositories to migrate.\n")

    for repo in repos:
        print(f"--- Processing {repo} ---")
        
        # 1. Clone Mirror from Bitbucket
        bb_url = f"https://x-token-auth:{bb_token}@bitbucket.org/{BB_WORKSPACE}/{repo}.git"
        subprocess.run(["git", "clone", "--mirror", bb_url], cwd=TEMP_DIR, check=True)
        
        repo_path = os.path.join(TEMP_DIR, f"{repo}.git")
        
        # 2. Fix GH002 Error (Ambiguous Ref names)
        clean_zombie_refs(repo_path)

        # 3. Create Empty Repo on GitHub
        requests.post(
            "https://api.github.com/user/repos",
            auth=(GH_USERNAME, GH_TOKEN),
            json={"name": repo, "private": True}
        )

        # 4. Push Mirror to GitHub
        gh_url = f"https://{GH_USERNAME}:{GH_TOKEN}@github.com/{GH_USERNAME}/{repo}.git"
        try:
            subprocess.run(["git", "push", "--mirror", gh_url], cwd=repo_path, check=True)
            print(f"  [Success] Migrated {repo}")
        except Exception as e:
            print(f"  [Error] Failed to push {repo}: {e}")

    shutil.rmtree(TEMP_DIR)
    print("\nMigration Complete.")

if __name__ == "__main__":
    migrate()
