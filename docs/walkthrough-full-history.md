# Walkthrough, Full History

Example walkthrough of creating a new component-specific repo that contains full history for all affected files, including branch labels.

Also see the [clone-and-filter-repo](../bin/clone-and-filter-repo) script.  It automates most of the work that is detailed below.

The following is a walkthrough of the entire process, starting with cloning the `zcs-full` repository from stash and creating one of the component-focused git repositories documented in the *Zimbra Source Code Repositories* spreadsheet.

Here we are creating the `zm-backup-store` repo.

These are the mappings from Perforce to git that are defined in the spreadsheet:

**Perforce Path** | **zm-backup-store Path**
---- | -----
ZimbraBackup/src/java | src/java
ZimbraBackup/src/java-test | src/java-test
ZimbraBackup/docs | docs
ZimbraBackup/build.xml | build.xml


All of the content for the new `zm-backup-store` repo is derived from the top-level `ZimbraBackup` directory. However, there is additional content under the `ZimbraBackup` directory, so the steps described here will have to perform the following two functions:

- Filter out everything that is not part of the `ZimbraBackup` subdirectory, and 
- Remove all of the extra information that does not belong in the `zm-backup-store` repository 

Some of the steps described here take a long time to run. That is because of the following:

- We are trying to preserve all history related to the files in the new repository, including branch labels. 
- We have a lot of commits in the `zcs-full` repository

In particular, the second phase, application of the tree-filter, can take a *really* long time, depending upon how many items you are removing from the new repo that you populated from the subtree-filter. What has to happen is this:  For *every* commit in the
repo history, the tree-filter applies the `rm -rf ...` command.

## Clone zcs-full

Start with clone of `zcs-full`

    git clone ssh://git@stash.corp.synacor.com:7999/zimbra/zcs-full.git
    pushd zcs-full

Here are the remotes. Notice just the one origin.

    git remote -v
    origin  ssh://git@stash.corp.synacor.com:7999/zimbra/zcs-full.git (fetch)
    origin  ssh://git@stash.corp.synacor.com:7999/zimbra/zcs-full.git (push)


## Prepare the local repo

First delete all local branches:

	git checkout --detach
	git branch | grep --invert-match "*" | xargs git branch -D

Recreate all remote branches locally:

    for b in $(git branch --remotes --no-color | grep --invert-match '\->'); do git checkout -f --track "$b"; done

Remove the origin

    git remote remove origin

## Get rid of everything that doesn't belong

Now we are going to filter out everything but the `ZimbraBackup` directory.

    git filter-branch --prune-empty \
      --subdirectory-filter ZimbraBackup \
      -- --all

What we have left in the repo is the following:

    build.xml  ZimbraBackup.iml
	docs:
        backup.txt  mailboxMove.txt  soapbackup.txt  xml-meta.txt
	src:
        bin  db  java  java-test  libexec  zimlet

Notice that the following sub-components do not belong in the final result and must be filtered out.

- `ZimbraBackup.iml`
- `src/bin`
- `src/db`
- `src/libexec`
- `src/zimlet`

First we need to remove the backup refs from the previous operation:

    rm -rf .git/refs/original/*

Now perform the new filter operation. Just a quick note. It seems that one should be able to combine both `--subdirectory-filter` and `--tree-filter` in a single command, but I could not get that to work.

    git filter-branch --tree-filter \
      'rm -rf ZimbraBackup.iml src/bin src/db src/libexec src/zimlet' \
      -- --all

Once that finishes, we have exactly what is desired.

    build.xml
	docs/*
	src/java/*
	src/java-test/*

But this new repo is bigger than it needs to be:

	du -sh .
	1.5G   .

That is from all of the residue left from our filter operations. Cleaning up things to reduce the size:

	rm -rf .git/refs/original/* .git/subtree-cache/*
	git reflog expire --expire=now --all
	git gc --aggressive --prune=now

Check the results:

	du -sh .
	6.7M  .
