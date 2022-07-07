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

def base():
    query_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
    params = {}
    headers = {'Authorization': f'token {token}'}
    r = requests.get(query_url, headers=headers, params=params)
    pprint(r.json())

def tree():
    url = "https://api.github.com/repos/{}/{}/git/trees/master?recursive=1".format(owner, repo)
    print(url)
    params = {}

    headers = {'Authorization': f'token {token}'}
    r = requests.get(url, headers=headers, params=params)
    res = r.json()

    for file in res["tree"]:
        print(file["path"])

def sha():
    url = "https://api.github.com/repos/{}/{}/branches/master".format(owner, repo)
    params = {}

    print(url)
    headers = {'Authorization': f'token {token}'}
    r = requests.get(url, headers=headers, params=params)
    res = r.json()

    print(res)
    
    head_tree_sha = res['commit']['tree']['sha']
    print(head_tree_sha)

tree()