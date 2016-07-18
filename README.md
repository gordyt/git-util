# git-util

The purpose of this repository is to provide information and tools for working with git.

## bin

[analyze-repo](bin/analyze-repo)

This is a bash script that will identify the largest files in a local git repo.  Credits:

- [Steve Lorek](http://stevelorek.com/how-to-shrink-a-git-repository.html)
- [Anthony Stubbs](https://stubbisms.wordpress.com/2009/07/10/git-script-to-show-largest-pack-objects-and-trim-your-waist-line/)

[clone-and-filter-repo](bin/clone-and-filter-repo)

This has been rewritten in Python for better performance and also to make it more flexible.  It can now handle creating a new component-focused repository that is based off of one *or more* top-level directories, typically based off one of the following:

- `zcs-full`
- `zd-full`
- `zqa-full`

This script maintains full history, including branch labels. Run the script with `-h` or `--help` option for instructions.  There are probably three typical patterns where this script can help.  These are listed in order from fastest to slowest execution time.

1. You just need to extract one subtree out of the source repo, with full history. You would use the following arguments: -s SRC-REPO -d DEST-REP -f FILTER-DIR
2. You want to extract one subtree out of the source repo, and then further filter out parts of that subtree that are not required.  You would use the following arguments: -s SRC-REPO -d DEST-REP -f FILTER-DIR -i INCLUDE-PATHS-FILE
3. You want to extract multiple subtrees out of the source repo, and further filter out parts of the subtree that are not required. You would use the following arguments: -s SRC-REPO -d DEST-REP -f INCLUDE-PATHS-FILE

The crucial difference to keep in mind between action #2 and action #3 is the format of the *INCLUDE-PATHS-FILE*.  The process of extracting a subtree first (as in action #2) promotes all of the children of *FILTER-DIR* to the top-level of *DEST-REPO*.  But in action #3, because we do not first apply a subtree filter (you can only do that with one subtree), then the new contents of *DEST-REPO* maintain their full hierarchy.

Examples will follow.

## docs


- [creating-stash-repo](docs/creating-stash-repo.md) - instructions for creating a new repository in stash.
- [creating-ram-disk](docs/creating-ram-disk.md) - basic instructions for creating a RAM disk as a working area for reposity operations.  This is especially handy if you are performing your work from a system that has conventional drives but plenty of RAM.
- [managing-build-dependencies](docs/managing-build-dependencies.md) - guidelines for managing build dependencies in the new git component-focused repositories
- [rearranging-commits](docs/rearranging-commits.md) - how to fix commit histories, in painful detail
- [stash-repos](docs/stash-repos.md) - the list of master repositories in stash from which all of the component-focused repositories are based.
- [walkthrough-full-history](docs/walkthrough-full-history.md) - a walkthrough of the process required to create a component-focused repository with full history, including branch labels. This document shows how to do everything "by hand," without the assistance of the `clone-and-filter-repo` script.
- [walkthrough-multiple-folders](docs/walkthrough-multiple-folders.md) - a walkthrough of the entire process for creating a component-focused repo based off of multiple top-level source directories.
- [walkthrough-multiple-split](docs/walkthrough-multiple-split.md) - a different method for creating a new repo based off of multiple top-level source directories.

## additional notes about filtering repositories

1. Some of the operations described in the procedures below can take a very long time to run.  If you have available RAM on your machine, creating a RAM disk upon which to store your output repositories temporarily can help.
2. If the list of files and directories to filter out of the new repository is excessively long, then the `--tree-filter` operation can take a *really* long time.  In those cases it may be better to broaden the list of files/folders to include and then manually delete the extra ones that remain in the output repo after the operation has completed.  When I tested with the `zm-timezones` repository, there sere **814** paths that had to be (potentially) removed from *every* commit in the output repo.
3. If you do not require full history with branch labels in the new repo, then when you create your local clone repository (as the source), do not pull in every branch from stash, just the current main branch (or branches) that you need.

## tutorials

Tutorials will be maintained in separate repositories as they may depend on having a specific organization of branches, etc., to facilitate proper execution of the tutorial.

### rebase-merge-feature

This tutorial will walk you through the essential actions needed to manipulate the structure of your git repository.  This will be especially important as teams transition to following [recommended git best practices](http://nvie.com/posts/a-successful-git-branching-model/).

Start by cloning the tutorial to your local drive, then following the instructions in the README.

	git clone git@gitlab.com:gordyt/rebase-merge-feature.git

Or, if you don't have credentials registered with GitLab

    git clone https://gitlab.com/gordyt/rebase-merge-feature.git

Then prepare the repo by pulling down all of the remote branches:

    cd rebase-merge-feature
    for b in $(git branch --remotes --no-color | grep --invert-match 'master'); do git checkout -f --track "$b"; done
    git checkout master

