# Getting Started with Git-Flow

## Introduction

The _git-flow_ tools (AVH edition) help enforce best practices when working with our _git_ repositories.  They do _not_ cover all possible _git_ operations that you may need to perform.  There is nothing you can do with the tools that you cannot do without them. But it is easy to forget certain critical steps when working with different kinds of branches and the tools help with that.

## Installation

All references to _git-flow_ refer to the [gitflow-avh](https://github.com/petervanderdoes/gitflow-avh) project code.  Please see [this wiki page](https://github.com/petervanderdoes/gitflow-avh/wiki/Installation) and refer to installation instructions that are appropriate for your operating system.

**Important:** If you are using an application to interact with _Git_, as opposed to using the command-line, please ensure the application honors your `$HOME/.gitconfig` settings.  This file is updated by the `gitflow-config-init` script described below.

## Initial Configuration

After installing _git_ and _git-flow_, please download a copy of the `gitflow-config-init` script, located in the `bin` directory of this repo.  You can run it with a `-h` option to get some help.  But, basically, you will just want to run it with no options.  This will update your `$HOME/.gitconfig` file so that certain _git-flow_ commands will have the proper options switched on (or off) by default.  **This is important.** The examples that follow assume that you have performed this step.  You **must** perform this _initial configuration_ on each computer or VM from which you are interacting with our _git_ repositories.

## Convenient Aliases

The _git-flow_ commands are a bit verbose and you can save some typing by creating a few convenient aliases for working with them.  As an example:

	alias gfi='git flow init'
	alias gff='git flow feature'
	alias gfb='git flow bugfix'
	alias gfr='git flow release'
	alias gfh='git flow hotfix'
	alias gfs='git flow support'
	alias gfv='git flow version'
	alias gfc='git flow config'
	alias gfl='git flow log'

## Updating your local repos to use git-flow


**NOTE:** Make sure you have a remote labeled `origin` that points to the appropriate GitHub (for FOSS) or Stash (for NETWORK) repository.  This will be the copy of the repository that resides in the `Zimbra` project, not your fork.  It is fine to still have a remote that points to your fork, but please be sure to label it something other than `origin`.  For example, you may wish to use your first name as a label.

To rename an existing remote in your local repo, just execute the following command:

	git remote rename OLD-NAME NEW-NAME


Assuming you have already run the `gitflow-config-init` command mentioned above, all you need to do is run the following from the top-level of the repo you are working with:

	git flow init

You will end up with the following branch/tag conventions established for the repo:

	$ git flow config

	Branch name for production releases: master
	Branch name for "next release" development: develop
	Feature branch prefix: feature/
	Bugfix branch prefix: bugfix/
	Release branch prefix: release/
	Hotfix branch prefix: hotfix/
	Support branch prefix: support/
	Version tag prefix:


## Branches in git-flow

There are only two permanent branches in any repository that is managed by _git-flow_:

- `master`
- `develop`

`master` represents production releases.  It's history is never rewritten, so it is not permitted to rebase `master`.  Each product release is _not_ saved as a new branch.  Instead, each product release is represented by a tag on the `master` branch.

`develop` represents the _next_ product release.  Work committed to the `develop` branch is available to be tested.  When we have code-freeze for the next release, a release-integration branch is created from the _HEAD_ of `develop`.  All work related to preparing and certifying the release is checked into the release-integration branch.  When the release is ready, the release-integration branch is merged into _both_ `master` and `develop`.  While release certification is in progress, other work (features, bugfixes, etc.) may be checked into the `develop` branch.


As you may intuit from the output of the `git flow config` command, the major "types" of branches that are handled by _git-flow_ are:

* Feature
* Bugfix
* Release
* Hotfix
* Support

## Starting a new branch

* Feature
  * `git flow feature start FEATURE-NAME`
  * This creates a new feature branch, based off of `develop` (by default), called `feature/FEATURE-NAME`.
  * Example: `git flow feature start imap`
* Bugfix
  * `git flow bugfix start TICKET` 
  * This creates a new bugfix branch, based off of `develop` (by default), called `bugfix/TICKET`.
  * Example: `git flow bugfix start zms-123`
* Release
  * `git flow release start VERSION`
  * This creates a new release integration branch, based off of `develop` (by default), called `release/VERSION`.
  * Example: `git flow release start 876`
* Hotfix
  * `git flow hotfix start VERSION`
  * This creates a new hotfix branch, based off of `master` (by default), called `hotfix/VERSION`
  * Example: `git flow hotfix start 876p1`
  * Tip: Run `git flow hotfix start -h` to see options for the command.
* Support
  * These are special case branches and only limited _git-flow_ options are available.
  * To create one: `git flow support start VERSION BASE`
  * This creates a new support branch called `support/VERSION` based off of the specified base tag or commit.
  * These support branches hang around until you delete them.  Git flow does not mandate any other special treatment for them.

You can list any branches of a given type by use of the following command:

	git flow BRANCH-TYPE list

Running `git flow BRANCH-TYPE` with no arguments executes the `list` command by default.  For example, if you type `git flow feature`, it will list all of your local feature branches.  When you list branches of a given type, or when you use a _git-flow_ command that applies to a branch of a given type, you will see or use just the "short" name of the branch.

Suppose you had three local feature branches with the following names:

- feature/imap
- feature/sieve
- feature/smime

If you executed the command `git flow feature` or `git flow feature list`, you would get the following output:

	imap
	sieve
	smime

## Pulling an existing branch down to your local repo

Suppose there is an existing feature branch in `origin`.  You don't have a copy of it in your local repo, but need to do some work with it.  Just issue the following commands:

	git fetch origin
	git flow feature track FEATURE-NAME

As an example, if `origin` contained a branch named `feature/imap`, you could fetch it locally and check it out with the following command:

	git flow feature track imap

The same concepts apply to other branch types as well.

### Updating your local feature branch

If at any time you ever need to make sure one of your local branches are up-to-date with `origin`, you can do the following steps.  Here we are using a feature branch as an example.

Start by pulling in the latest changes:

	git fetch origin

Case 1: If you have _never_ checked out the FEATURE feature branch locally:

	git flow feature track FEATURE

Case 2: If you are currently on your local FEATURE  feature branch (feature/FEATURE), merge in changes from `origin`:

	git merge origin/feature/FEATURE
	
Case 3: Lastly, if you do have a local FEATURE feature branch, but you are on a different branch right now, just move your local FEATURE branch pointer so that it is in sync with `origin`:

	git branch -f feature/FEATURE origin/feature/FEATURE

Most of the above commands used _git_ directly, and for those you must specify full branch names.  Remember, _git-flow_ doesn't completely shield you from _git_!


## Collaborating on a branch

Continuing with the feature branch example, suppose you are collaborating with other members of your team. Let's do some work on the "imap" feature branch (`feature/imap`). Suppose you were assigned to fix bug `ZMS-123` and that it is a bug that relates to the ongoing "imap" feature.  Before you start working on this bug, you will want to make sure you have the "imap" feature branch in your local repo.  If you do not, you can use the following _git-flow_ commands to pull it down:

	git fetch origin
	git flow feature track imap


### Working on your bug

Now start working on ticket `ZMS-123`.  Notice we tell _git-flow_ to use our team's `feature/imap` branch as the base for the bug, instead of the default (`develop`) branch.  The configuration options loaded by the `gitflow-init-script` will pull in changes from `origin` _before_ creating your bugfix branch.


	git flow bugfix start zms-123 feature/imap

This command gives the following output:

	Switched to a new branch 'bugfix/zms-123'

	Summary of actions:
	- A new branch 'bugfix/zms-123' was created, based on 'feature/imap'
	- You are now on branch 'bugfix/zms-123'

	Now, start committing on your bugfix. When done, use:

	    git flow bugfix finish zms-123
	
As you can see, you are given good instructions. Do the work, adding and committing as normal.  If the work takes a while, you should keep your working branch up-to-date with its base branch by rebasing regularly.  This lets you catch possible merge conflicts early and address them. Note that even if you do not periodically rebase your working branch, it will still be rebased by _git-flow_ when you "finish" the branch.  That automatic behavior will be present so long as you have updated your `$HOME/.gitconfg` via the `gitflow-config-init` script.

In this case, we based our bugfix branch off of the "imap" feature branch (`feature/imap`), and _git-flow_ knows that.  Follow these steps to do periodic rebasing of your work.

Start by making sure your local feature branch is up-to-date with `origin`.  Follow the steps described above in _Updating your local feature branch_.  Then do the following:

	git flow bugfix rebase zms-123

This rebases your local `bugfix/zms-123` branch on your local `feature/imap` branch.


When you are ready to generate a pull request, you can publish your bugfix branch.  If you have _not_ published it before, then just use the following command.  This will publish your bugfix branch to `origin`.   You may instead publish to your fork. That is covered below.

	git flow bugfix publish zms-123
	
The output:

	Summary of actions:
	- The remote branch 'bugfix/zms-123' was created or updated
	- The local branch 'bugfix/zms-123' was configured to track the remote branch
	- You are now on branch 'bugfix/zms-123'

If you _have_ published it before, and if you did rebase it since publishing, you will need to "force push" your changes as follows. Again note that, as this is a plain _git_ command, you must use full branch names:

	git push origin +bugfix/zms-123

Pull requests may be generated from your bugfix branch in `origin`.  If, instead, you prefer to issue the pull request from your fork, you may do that as well.  Instead of using `git flow bugfix publish...` or `git push origin...`, just do the following, where _FORK_ is the name of the remote you have assigned to your fork of the repo:

	git push FORK +bugfix/zms-123

If, as a result of feedback on your pull request, you need to make additional changes, just commit them locally and publish them back to `origin` or your fork as described above.  Once your pull request has been approved, you can finish (merge) your bugfix branch.  Again, the default configuration options that the `gitflow-config-init` script provided will ensure that the base branch is pulled and your changes are rebased on top of it _before_ merging it.

	git flow bugfix finish zms-123

The output:

    Summary of actions:
    - The bugfix branch 'bugfix/zms-123' was merged into 'feature/imap'
    - bugfix branch 'bugfix/zms-123' has been locally deleted; it has been remotely deleted from 'origin'
    - You are now on branch 'feature/imap'

**Note:** When you finish a bugfix branch, you must push your newly-updated local `<base>` branch back to `origin` as follows:

	git push origin <base>

## Finishing a Feature

Suppose you have a feature branch that has been completed and reviewed and is ready to be merged into the `develop` branch.  The command required to accomplish this is as follows:

	git flow feature FEATURE-NAME finish

So for our hypothetical "feature/imap" branch:

	git flow feature imap finish

The default options configured from the `gitflow-config-init` init script will take care of making sure that your feature branch has been properly rebased before merging into `develop`.  Finishing a bugfix branch based on `develop` works the same.

## Working With Releases

When we have code freeze for a release, the following steps will occur:

1. Create a _release-integration_ branch for each repository:

		git flow release start VERSION
		
	For example:
	
		git flow release start 876
		
	This will create a branch called `release/876`, based off the head of `develop`.  So `release/876` would be the _release-integration_ branch.

2. Normal development can continue.  It is safe to merge new bugfixes and features into the `develop` branch while the release is being certified.
3. Code changes that apply to the release get commited to the _release-integration_ branch.
4. If, at any time during the release certification, it becomes desireable to bring commits _from_ the _release-integration_ branch into the `develop` branch, then do so by rebasing the _develop_ branch onto the _release-integration_ branch as follows:

		git fetch origin
		git checkout develop
		git reset --hard origin/develop
		git rebase -p origin/release/VERSION
		git push origin +develop
		
	Let's examine each of those steps in detail.
	
	1. `git fetch origin` - This ensures your local repo has all of the current changes from `origin`.
	2. `git checkout develop` - Check out your local `develop` branch.
	3. `git reset --hard origin/develop` - Make your local `develop` branch match `origin/develop`
	4. `git rebase -p origin/release/VERSION` - Rebase your local `develop` branch onto the `HEAD` of the _release-integration_ branch.  In our example, _VERSION_ is `876`. The `-p` option ensures instructs _git_ to preserve merge commits.
	5. `git push origin +develop` - This pushes your local `develop` branch _back_ into `origin`. **NOTE:** This rewrites history for the `develop` branch.  Before doing all of this, make sure you _really need_ the commits from the _release-integration_ branch in `develop` before it has been certified!  It is recommended that one person from the team (who is comfortable working with _git_) be responsible for doing this.
	
5. Once the release has been certified, then it is "finished" by doing the following:

		git flow release finish
		
	This does the following:
	
	1. It merges the _release integration_ branch back in to `master` and `develop`.
	2. It tags the release (on `master`), using the following tag name:
	
			VERSION

