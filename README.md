# git-util

The purpose of this repository is to provide information and tools for working with git.

## bin

### clone-and-filter-repo

This is a bash script that automates most of the steps required to create a new  
component-focused repository that is based off of a top-level directory 
in one of the following "master" repositories:

- `zcs-full`
- `zd-full`
- `zqa-full`

This script maintains full history, including branch labels.  Run the script
with `-h` or `--help` option for instructions.
