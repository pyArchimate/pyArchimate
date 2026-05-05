#C/spe!/bin/sh

git fetch --all --prune
git checkout master
git pull origin master
git checkout develop
git pull origin develop
echo "Please check if you have any stale branches that need to be deleted locally."
git branch -a
# echo "Deleting stale branches..."
# git branch -vv | grep ': gone]' | awk '{print $1}' | xargs git branch -d
