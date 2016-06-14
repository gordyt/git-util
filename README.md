# git-util

The purpose of this repository is to provide information and tools for working with git.

## bin

[clone-and-filter-repo](bin/clone-and-filter-repo)

This is a bash script that automates most of the steps required to create a new  
component-focused repository that is based off of a top-level directory 
in one of the following "master" repositories:

- `zcs-full`
- `zd-full`
- `zqa-full`

This script maintains full history, including branch labels.  Run the script
with `-h` or `--help` option for instructions.

## docs

- [stash-repos](docs/stash-repos.md) - the list of master repositories
  in stash from which all of the component-focused repositories are
  based.
- [walkthrough-full-history](docs/walkthrough-full-history.md) - a
  walkthrough of the process required to create a component-focused
  repository with full history, including branch labels.
