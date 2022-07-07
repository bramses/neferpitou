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
import filecmp
import pathlib

ALLOWED_EXTENSIONS = ['md']

cmpr = filecmp.dircmp(pathlib.Path('./tests').resolve(), pathlib.Path('./tests').resolve())
print(cmpr.common)

# get path of ./tests
tests = pathlib.Path('./tests').resolve()