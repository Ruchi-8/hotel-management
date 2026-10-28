"""
Push HotelPro project to GitHub repository:
https://github.com/Ruchi-8/hotel-management.git
"""

import os
import sys
import certifi

# Ensure SSL certificates are properly located on Windows
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

import dulwich.porcelain as p
from dulwich.repo import Repo

REPO_PATH = os.path.dirname(os.path.abspath(__file__))
REMOTE_REPO = "github.com/Ruchi-8/hotel-management.git"
USERNAME = "Ruchi-8"
USER_EMAIL = "chaturvediruchi0809@gmail.com"

def push(token: str):
    if not token or not token.strip():
        print("Error: GitHub Personal Access Token is required.")
        return False

    token = token.strip()
    remote_url = f"https://{USERNAME}:{token}@{REMOTE_REPO}"

    repo = Repo(REPO_PATH)

    print(f"Adding all changes to git index...")
    # Refresh index with all files respecting .gitignore
    p.add(repo)

    # Check if there are uncommitted changes
    status = p.status(repo)
    has_changes = bool(status.staged["add"] or status.staged["modify"] or status.staged["delete"] or status.untracked)

    if has_changes:
        print("Creating commit...")
        author = f"{USERNAME} <{USER_EMAIL}>".encode("utf-8")
        p.commit(repo, message=b"HotelPro: Hotel Management Solution with Streamlit and MERN", author=author, committer=author)
        print("Committed successfully.")

    print(f"Pushing to https://{REMOTE_REPO} on branch main...")
    try:
        # Push HEAD to main branch
        p.push(repo, remote_url, refspecs=b"HEAD:refs/heads/main")
        print("SUCCESS! Successfully pushed HotelPro to https://github.com/Ruchi-8/hotel-management.git")
        return True
    except Exception as e:
        print(f"Push failed: {e}")
        return False

if __name__ == "__main__":
    token = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("GITHUB_TOKEN", "")
    if not token:
        token = input("Enter your GitHub Personal Access Token (PAT): ").strip()
    success = push(token)
    sys.exit(0 if success else 1)
