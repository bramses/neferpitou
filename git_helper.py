# option 1: fetch each file from gh
# every day pull and see if files changed, upsert files to index if they changed
#    cons: a ton of http calls
# option 2: keep the folder locally
#    cons: cannot gitignore files