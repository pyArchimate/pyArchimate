#C/spe!/bin/sh

git fetch --all --prune
git checkout master
git pull origin master --rebase
git checkout develop
git pull origin develop --rebase
echo "Please check if you have any stale branches that need to be deleted locally."
git branch -a
# echo "Deleting stale branches..."
# git branch -vv | grep ': gone]' | awk '{print $1}' | xargs git branch -d

echo "Updating dependencies to latest compatible versions..."
poetry update
git add poetry.lock
git diff --cached --quiet || git commit -m "chore: update dependencies"
