#!/bin/bash
# Used for migrating ZMS work on "feature" branch of zm-store repository
# to "store" sub-directory of "zm-mailbox" repository.
# Do one changeset at a time.
sc_name=`basename $0`

usage_error ()
{
    cat >&2 <<EOF
usage : $sc_name -F fromCommit -T toCommit [-r sourc-repo] [-d target-dir] [-t target-branch] [-u upstream remote]
    -r default value:${repo}
    -t default value:${targetBranch}
    -d default value:${targetDir}
    -u default value:${upstreamRemote}
EOF
    exit 1
}

upstreamRemote="origin"
targetBranch="dev"
repo="zm-common"
targetDir="common"
tmpBranch="newTree42"
fromRev=unset
toRev=unset
while getopts F:T:r:t:u:d: CurrOpt
do
    case $CurrOpt in
    F)        fromRev="$OPTARG";;
    T)        toRev="$OPTARG";;
    r)        repo="$OPTARG";;
    t)        targetbranch="$OPTARG";;
    d)        targetDir="$OPTARG";;
    u)        upstreamRemote="$OPTARG";;
    ?)        usage_error;;
    esac
done

if [ "${fromRev}" = "unset" -o "${toRev}" = "unset" ]
then
    usage_error
fi

commitMsgFile=/tmp/commitMsg
(set -x;rm -f ${commitMsgFile})
if [ $? -ne 0 ]
then
    echo "Problem deleting ${commitMsgFile}"
    exit 1
fi
// author=$(cd ../${repo} && git show --name-only --format=short --abbrev-commit ${toRev}|grep ^Author:|sed 's/Author: //')
author=$(cd ../${repo} && git log --format="%an <%ae>" -n 1 ${toRev})
$(cd ../${repo} && git log --format="%B" -n 1 ${toRev}>${commitMsgFile})
echo AUTHOR:$author
(set -x;cat ${commitMsgFile})

(set -x;git checkout ${targetBranch})
if [ $? -ne 0 ]
then
    echo "Problem checking out target branch ${targetBranch}"
    exit 1
fi

(set -x;git branch -D ${tmpBranch})
(set -x;git checkout -b ${tmpBranch})
if [ $? -ne 0 ]
then
    echo "Problem creating work branch ${tmpBranch}"
    exit 1
fi
(set -x;git --git-dir=../${repo}/.git format-patch --stdout ${fromRev}..${toRev} | git am -3 --directory=${targetDir})
(set -x;git checkout ${targetBranch})
if [ $? -ne 0 ]
then
    echo "Problem creating work branch ${targetBranch}"
    exit 1
fi
(set -x;git merge --no-edit --no-ff ${tmpBranch})
(set -x;git commit --amend --author="$author" -F ${commitMsgFile})
