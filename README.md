# git-util

The purpose of this repository is to provide information and tools for working with git.

## bin

[clone-and-filter-repo](bin/clone-and-filter-repo)

This is a bash script that automates most of the steps required to create a new component-focused repository that is based off of a top-level directory in one of the following "master" repositories:

- `zcs-full`
- `zd-full`
- `zqa-full`

This script maintains full history, including branch labels. Run the script with `-h` or `--help` option for instructions.

## docs


- [creating-stash-repo](docs/creating-stash-repo.md) - instructions for creating a new repository in stash.
- [stash-repos](docs/stash-repos.md) - the list of master repositories in stash from which all of the component-focused repositories are based.
- [walkthrough-full-history](docs/walkthrough-full-history.md) - a walkthrough of the process required to create a component-focused repository with full history, including branch labels. This document shows how to do everything "by hand," without the assistance of the `clone-and-filter-repo` script.

## additional notes about filtering repositories

1. Some of the operations described in the procedures below can take a very long time to run.  If you have available RAM on your machine, creating a RAM disk upon which to store your output repositories temporarily can help.
2. If the list of files and directories to filter out of the new repository is excessively long, then the `--tree-filter` operation can take a *really* long time.  In those cases it may be better to broaden the list of files/folders to include and then manually delete the extra ones that remain in the output repo after the operation has completed.  When I tested with the `zm-timezones` repository, there sere **814** paths that had to be (potentially) removed from *every* commit in the output repo.
3. If you do not require full history with branch labels in the new repo, then when you create your local clone repository (as the source), do not pull in every branch from stash, just the current main branch (or branches) that you need.
