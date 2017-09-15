#!/bin/bash
#set -x
REMOTE="origin"
BRANCH="develop"
DRYRUN="dryrun"

function process_branches {
    unmerged_branches=$(git branch -r --merged $REMOTE/$BRANCH | grep -e "feature/*" -e "bugfix/*")

    for branch in $unmerged_branches; do
        b=`echo "$branch" | cut -d '/' -f 2,3`
        if [ $DRYRUN != "dryrun" ]; then
            echo "Deleting '$b'"
            git push $REMOTE :$b
        else
            echo "DRYRUN: git push $REMOTE :$b"
        fi
    done
}

function help {
    echo "merged-branches <options>"
    echo "-h help"
    echo "-c commit"
    echo "-b target branch name (default 'develop')"
    echo "-r remote name (default 'origin')"
}

while getopts :r:b:ch option
do
    case ${option}
    in
        c) DRYRUN="commit";;
        b) BRANCH=$OPTARG;;
        h) help
           exit 0
           ;;
        r) REMOTE=$OPTARG;;
    esac
done

echo $DRYRUN
echo "Remote: $REMOTE"
echo "Branch: $BRANCH"

process_branches
