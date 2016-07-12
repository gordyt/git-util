## Rearranging Commits

In this scenario, you have some commits that were merged without reabasing them first and you want to clean up the commit history.  The following documents the steps required to fix that.

## Initial State

This is what we are starting with.  Three comments:

- We can see that that work was merged from different branches without rebasing them first.
- Some of the commit messages are too long.  Standard git conventions restrict the *first line* of a commit message to 50 characters.  If you want to add more information to a commit message, keep the first line short, add a blank line after it, then put in any additional information that is required.
- We should be sure to include bug numbers in the first line of the commit message, where applicable.

Here is the tree:

    *   5b17aeb (HEAD, upstream/master, upstream/HEAD, master) Merge branch '105752'
    |\
    | *   ca268fc resolve merge conflicts and keep modifications to classpath for junit tests
    | |\
    | | *   524927d Merge pull request #6 in ZIMBRA/zm-zcs from ~SHRIKANT.PRASAD/zm-zcs:105737 to master
    | | |\
    | | | * 3085537 added claspath for running unit test
    | |_|/
    |/| |
    | | *   2e96fd5 Merge pull request #5 in ZIMBRA/zm-zcs from 105752 to master
    | | |\
    | |/ /
    |/| |
    | * | 3ef3d5f remove dist.lib and dist.lib.ext dirs from common build-init (addressing Gren's comment)
    | * | f38a2e4 add missing definitions of dist.lib.dir and dist.lib.ext.dir
    | * | 677bcd0 add common build-init task
    | * | aa29f48 incorporate Shrikant's changes and fix 'test' target for projects that do not have unit tests
    | |/
    | * b68552b (upstream/105752) add /opt/zimbra/lib/jars to local resolver in order to be able to work on a dev environment created wit
    |/
    * 30d9f1d remove duplicate resolve target
    *   cb6bef5 bug 105712 - ivy updates

## Procedure

It is a little difficult to tell what commits are related (hence reason for including bug numbers), so it may be helpful to include the names of the person associated with each commit in the output:


    *    5b17aeb [Greg Solovyev] (HEAD, upstream/master, upstream/HEAD, master) Merge branch '105752'
    |\
    | *    ca268fc [Greg Solovyev] resolve merge conflicts and keep modifications to classpath for junit tests
    | |\
    | | *    524927d [Greg Solovyev] Merge pull request #6 in ZIMBRA/zm-zcs from ~SHRIKANT.PRASAD/zm-zcs:105737 to master
    | | |\
    | | | *  3085537 [Shrikant] added claspath for running unit test
    | |_|/
    |/| |
    | | *    2e96fd5 [Greg Solovyev] Merge pull request #5 in ZIMBRA/zm-zcs from 105752 to master
    | | |\
    | |/ /
    |/| |
    | * |  3ef3d5f [Greg Solovyev] remove dist.lib and dist.lib.ext dirs from common build-init (addressing Gren's comment)
    | * |  f38a2e4 [Greg Solovyev] add missing definitions of dist.lib.dir and dist.lib.ext.dir
    | * |  677bcd0 [Greg Solovyev] add common build-init task
    | * |  aa29f48 [Greg Solovyev] incorporate Shrikant's changes and fix 'test' target for projects that do not have unit tests
    | |/
    | *  b68552b [Greg Solovyev] (upstream/105752) add /opt/zimbra/lib/jars to local resolver in order to be able to work on a dev enviro
    |/
    *  30d9f1d [Gordon Tillman] remove duplicate resolve target
    *    cb6bef5 [Gordon Tillman] bug 105712 - ivy updates

There are 3 pull requests involved here:

- [#5 - add /opt/zimbra/lib/jars to local resolver](https://stash.corp.synacor.com/projects/ZIMBRA/repos/zm-zcs/pull-requests/5/commits).  It has only one commit (not including the empty merge commit, which we do not need):
  - `b68552b`
- [#6 - added claspath for running unit test](added claspath for running unit test).  This one also has only one commit (not including the merge commit, which we do not need):
  - `3085537`
- [#7 - 105752](https://stash.corp.synacor.com/projects/ZIMBRA/repos/zm-zcs/pull-requests/7/commits). This one has 5 commits (not including the merge commit).  This pull request does require a merge commit as it is comprised of multiple steps, multiple commits.
  - `aa29f48`
  - `677bcd0`
  - `f38a2e4`
  - `3ef3d5f`
  - `ca268fc`

So we should apply these three pull requests, in order.

## Pull request 5

Ignoring the empty merge commit, we can see that commit is alread based off of commit `30d9f1d`, so it is fine.

## Pull request 6

Here we just need to rebase the single commit from this pull request on top of the commit from pull request 5.  We will use the `git rebase --onto` command:

	git rebase --onto b68552b 30d9f1d 3085537

I'll go ahead and created a "working" branch with the current `HEAD` just to help keep track of things.

	git checkout -b working

This gives us the following:

    * 36f7c34 (HEAD, working) added claspath for running unit test
    | *   5b17aeb (upstream/master, upstream/HEAD, master) Merge branch '105752'
    | |\
    | | *   ca268fc resolve merge conflicts and keep modifications to classpath for junit tests
    | | |\
    | | | *   524927d Merge pull request #6 in ZIMBRA/zm-zcs from ~SHRIKANT.PRASAD/zm-zcs:105737 to master
    | | | |\
    | | | | * 3085537 added claspath for running unit test
    | | |_|/
    | |/| |
    | | | *   2e96fd5 Merge pull request #5 in ZIMBRA/zm-zcs from 105752 to master
    | | | |\
    | | |/ /
    | |/| /
    | |_|/
    |/| |
    | | * 3ef3d5f remove dist.lib and dist.lib.ext dirs from common build-init (addressing Gren's comment)
    | | * f38a2e4 add missing definitions of dist.lib.dir and dist.lib.ext.dir
    | | * 677bcd0 add common build-init task
    | | * aa29f48 incorporate Shrikant's changes and fix 'test' target for projects that do not have unit tests
    | |/
    |/|
    * | b68552b (upstream/105752) add /opt/zimbra/lib/jars to local resolver in order to be able to work on a dev environment created wit
    |/
    * 30d9f1d remove duplicate resolve target
    *   cb6bef5 bug 105712 - ivy updates

## Pull Request 7

Now we use the `git rebase --onto` command to move the 5 commits from pull request 7 on top of `cc64912`, which is the single commit from pull request 6.

	git rebase --onto working b68552b ca268fc

We get a merge conflict here:

    Applying: added claspath for running unit test
    Using index info to reconstruct a base tree...
    M       ant-global.xml
    ...
    Applying: incorporate Shrikant's changes and fix 'test' target for projects that do not have unit tests
    Using index info to reconstruct a base tree...
    M       ant-global.xml
    Falling back to patching base and 3-way merge...
    Auto-merging ant-global.xml
    CONFLICT (content): Merge conflict in ant-global.xml
    Failed to merge in the changes.
    Patch failed at 0002 incorporate Shrikant's changes and fix 'test' target for projects that do not have unit tests

We know that Greg had already done the work of resolving this, so we tell git to just keep the new file:

	git checkout --theirs ant-global.xml
	git add ant-global.xml
	git rebase --continue

Now what do we have?


    * 350912b (HEAD) remove dist.lib and dist.lib.ext dirs from common build-init (addressing Gren's comment)
    * 9c6dda2 add missing definitions of dist.lib.dir and dist.lib.ext.dir
    * 49ff353 add common build-init task
    * 47a2d5a incorporate Shrikant's changes and fix 'test' target for projects that do not have unit tests
    * 36f7c34 (working) added claspath for running unit test
    | *   5b17aeb (upstream/master, upstream/HEAD, master) Merge branch '105752'
    | |\
    | | *   ca268fc resolve merge conflicts and keep modifications to classpath for junit tests
    | | |\
    | | | *   524927d Merge pull request #6 in ZIMBRA/zm-zcs from ~SHRIKANT.PRASAD/zm-zcs:105737 to master
    | | | |\
    | | | | * 3085537 added claspath for running unit test
    | | |_|/
    | |/| |
    | | | *   2e96fd5 Merge pull request #5 in ZIMBRA/zm-zcs from 105752 to master
    | | | |\
    | | |/ /
    | |/| /
    | |_|/
    |/| |
    | | * 3ef3d5f remove dist.lib and dist.lib.ext dirs from common build-init (addressing Gren's comment)
    | | * f38a2e4 add missing definitions of dist.lib.dir and dist.lib.ext.dir
    | | * 677bcd0 add common build-init task
    | | * aa29f48 incorporate Shrikant's changes and fix 'test' target for projects that do not have unit tests
    | |/
    |/|
    * | b68552b (upstream/105752) add /opt/zimbra/lib/jars to local resolver in order to be able to work on a dev environment created with publis
    |/
    * 30d9f1d remove duplicate resolve target
    *   cb6bef5 bug 105712 - ivy updates

This is looking good, except notice that it didn't pull in the last commit `ca268fc`.  Let's try and cherry-pick it.

	git cherry-pick ca268fc

	error: Commit ca268fc24f2e180407793bd6d8665c94c5e65205 is a merge but no -m option was given.
	fatal: cherry-pick failed

So that commit was a merge commit and we need to give git a little more information to let it know what parent that was based on.  These parents are labelled 1, 2, 3, ..., with 1 being the immediate parent. That is what we want:

	git cherry-pick ca268fc -m 1

What does it look like now?


    * 39b3eae (HEAD) resolve merge conflicts and keep modifications to classpath for junit tests
    * 350912b remove dist.lib and dist.lib.ext dirs from common build-init (addressing Gren's comment)
    * 9c6dda2 add missing definitions of dist.lib.dir and dist.lib.ext.dir
    * 49ff353 add common build-init task
    * 47a2d5a incorporate Shrikant's changes and fix 'test' target for projects that do not have unit tests
    * 36f7c34 (working) added claspath for running unit test
    | *   5b17aeb (upstream/master, upstream/HEAD, master) Merge branch '105752'
    | |\
    | | *   ca268fc resolve merge conflicts and keep modifications to classpath for junit tests
    | | |\
    | | | *   524927d Merge pull request #6 in ZIMBRA/zm-zcs from ~SHRIKANT.PRASAD/zm-zcs:105737 to master
    | | | |\
    | | | | * 3085537 added claspath for running unit test
    | | |_|/
    | |/| |
    | | | *   2e96fd5 Merge pull request #5 in ZIMBRA/zm-zcs from 105752 to master
    | | | |\
    | | |/ /
    | |/| /
    | |_|/
    |/| |
    | | * 3ef3d5f remove dist.lib and dist.lib.ext dirs from common build-init (addressing Gren's comment)
    | | * f38a2e4 add missing definitions of dist.lib.dir and dist.lib.ext.dir
    | | * 677bcd0 add common build-init task
    | | * aa29f48 incorporate Shrikant's changes and fix 'test' target for projects that do not have unit tests
    | |/
    |/|
    * | b68552b (upstream/105752) add /opt/zimbra/lib/jars to local resolver in order to be able to work on a dev environment created with publis
    |/
    * 30d9f1d remove duplicate resolve target
    *   cb6bef5 bug 105712 - ivy updates


Now that worked.  Let's just take a moment to assure ourselves that what we did worked correctly.  Let's diff our files as they are now, with what is in the upstream.

	git diff upstream/master ant-global.xml

Perfect.  How about this one?

	git diff upstream/master ivysettings.xml

Yep, that is fine to.  Our next step is to create the empty merge commit that will let is group all of the commits from that last pull request together.

Make a note of that top commit number `39b3eae`

	git checkout working
	git merge --no-ff 39b3eae

We are prompted for a commit message.  Enter something suitable like this (remembering to keep within the 50 character limit for the first line).

bug 105752 - build script: zm-nginx-lookup-store

This is now what we have:

    *   53ca741 (HEAD, working) bug 105752 - build script: zm-nginx-lookup-store
    |\
    | * 39b3eae resolve merge conflicts and keep modifications to classpath for junit tests
    | * 350912b remove dist.lib and dist.lib.ext dirs from common build-init (addressing Gren's comment)
    | * 9c6dda2 add missing definitions of dist.lib.dir and dist.lib.ext.dir
    | * 49ff353 add common build-init task
    | * 47a2d5a incorporate Shrikant's changes and fix 'test' target for projects that do not have unit tests
    |/
    * 36f7c34 added claspath for running unit test
    | *   5b17aeb (upstream/master, upstream/HEAD, master) Merge branch '105752'
    | |\
    | | *   ca268fc resolve merge conflicts and keep modifications to classpath for junit tests
    | | |\
    | | | *   524927d Merge pull request #6 in ZIMBRA/zm-zcs from ~SHRIKANT.PRASAD/zm-zcs:105737 to master
    | | | |\
    | | | | * 3085537 added claspath for running unit test
    | | |_|/
    | |/| |
    | | | *   2e96fd5 Merge pull request #5 in ZIMBRA/zm-zcs from 105752 to master
    | | | |\
    | | |/ /
    | |/| /
    | |_|/
    |/| |
    | | * 3ef3d5f remove dist.lib and dist.lib.ext dirs from common build-init (addressing Gren's comment)
    | | * f38a2e4 add missing definitions of dist.lib.dir and dist.lib.ext.dir
    | | * 677bcd0 add common build-init task
    | | * aa29f48 incorporate Shrikant's changes and fix 'test' target for projects that do not have unit tests
    | |/
    |/|
    * | b68552b (upstream/105752) add /opt/zimbra/lib/jars to local resolver in order to be able to work on a dev environment created with publis
    |/
    * 30d9f1d remove duplicate resolve target
    *   cb6bef5 bug 105712 - ivy updates


All that is left to do is to push up our new branch (working) to the upstream master.  Since we have rewritten history, we will have to force it.

	git push upstream +working:master

Housekeeping:

Move my local `master` branch to `HEAD`

	git branch -f master HEAD

Check out `master` and delete my `working` branch:

	git checkout master
	git branch -D working

Here is the final state of the tree:

    *   53ca741 (HEAD, upstream/master, upstream/HEAD, master) bug 105752 - build script: zm-nginx-lookup-store
    |\
    | * 39b3eae resolve merge conflicts and keep modifications to classpath for junit tests
    | * 350912b remove dist.lib and dist.lib.ext dirs from common build-init (addressing Gren's comment)
    | * 9c6dda2 add missing definitions of dist.lib.dir and dist.lib.ext.dir
    | * 49ff353 add common build-init task
    | * 47a2d5a incorporate Shrikant's changes and fix 'test' target for projects that do not have unit tests
    |/
    * 36f7c34 added claspath for running unit test
    * b68552b (upstream/105752) add /opt/zimbra/lib/jars to local resolver in order to be able to work on a dev environment created with publishe
    * 30d9f1d remove duplicate resolve target
    *   cb6bef5 bug 105712 - ivy updates
    |\
    | * 30b861e bug 105712 - ivy reoranizations
    | * a877f32 Chain-resolver returns first match found
    |/
    * dadb84d add 'resolve' task that can be used by other projects and add dependency on 'resolve' and 'build-init' tasks to 'compile' task, so
    *   94a89a4 bug 105712 - global changes for new build system
    |\
    | * f21127d bug 105712 - Automatically download Ivy if needed.
    | * 39e66af bug 105712 - added ivysettings.xml
    | * 8012cdb bug 105712 - ant-global updates
    |/
    *   d1896ed Merge branch '105454'
    |\
    | * 8a006a3 (upstream/105454) modify ant-global.xml to take build properties from zimbra-package-stub which is available at https://github.co
    |/
    * d677043 add ant-global.xml that allows zm-archive-store to compile
