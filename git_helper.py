# option 1: fetch each file from gh
# every day pull and see if files changed, upsert files to index if they changed
#    cons: a ton of http calls
# option 2: keep the folder locally
#    cons: cannot gitignore files
# option 3: point to a remote folder
#    point to a directory that is seperately managed by git
#    fetch using git fetch to get filenames

# do not reindex the entire index every time a file is added
# do not clone the entire repo every time a file is added
import requests
import os
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()

token = os.getenv("GITHUB_TOKEN")
owner = os.getenv("GITHUB_OWNER")
repo = os.getenv("GITHUB_REPO")
query_url = f"https://api.github.com/repos/{owner}/{repo}/contents/src/extension.ts"
params = {}
headers = {'Authorization': f'token {token}'}
r = requests.get(query_url, headers=headers, params=params)
pprint(r.json())