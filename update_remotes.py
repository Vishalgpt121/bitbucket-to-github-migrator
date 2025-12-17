import os
import subprocess

# --- CONFIGURATION ---
# Folder containing your active projects
WORK_DIR = "YOUR_WORKSPACE_DIRECTORY"
GH_USERNAME = "YOUR_GITHUB_USERNAME"

def update_remote(repo_path):
    try:
        res = subprocess.run(["git", "remote", "get-url", "origin"], cwd=repo_path, capture_output=True, text=True)
        if res.returncode != 0 or "bitbucket.org" not in res.stdout: return
        
        current_url = res.stdout.strip()
        repo_name = current_url.split("/")[-1].replace(".git", "")
        new_url = f"https://github.com/{GH_USERNAME}/{repo_name}.git"
        
        print(f"Updating {repo_name}...")
        subprocess.run(["git", "remote", "set-url", "origin", new_url], cwd=repo_path, check=True)
        print(f"  -> Pointed to GitHub")
    except: pass

print(f"Scanning {WORK_DIR}...")
for item in os.listdir(WORK_DIR):
    path = os.path.join(WORK_DIR, item)
    if os.path.isdir(os.path.join(path, ".git")):
        update_remote(path)
print("Done.")
