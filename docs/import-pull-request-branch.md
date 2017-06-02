## Importing a Pull Request Branch

### Setup

You have a pull request submitted from a forked repo that you want to create a *feature* or *bugfix* branch from.  The following will work (and do the right thing) no matter how many commits are in the pull request.

#### Assumptions:

- You are working with one of our *FOSS* repos
- You have enabled [gitflow-avh](https://github.com/petervanderdoes/gitflow-avh) for the repo and have run the `gitflow-config-init` script on the computer from which you are working so that the proper defaults have been established. The latest version of this script as of the time of this tutorial, is 4.  You can always check your config version via the following command:

        git config --get gitflow.default-config-version
        4

- You have configured the convenient aliases for gitflow that were talked about during previous presentations and tutorials.  In case you haven't got them, here they are:

        alias gfb='git flow bugfix'
        alias gfc='git flow config'
        alias gff='git flow feature'
        alias gfh='git flow hotfix'
        alias gfi='git flow init'
        alias gfl='git flow log'
        alias gfr='git flow release'
        alias gfs='git flow support'
        alias gfv='git flow version'

### Example

For the example that follows I will use an [actual pull request issued from Jason Yi](https://github.com/Zimbra/zm-mailbox/pull/172).  It is from his `feature/imap` branch against the `feature/imap` branch of `zm-mailbox` in the *Zimbra* project.  You need to lookup the URL of Jason's fork.  You can find that out by clicking on his name in GitHub, finding is fork, and clicking on it. In this case it is as follows:

    https://github.com/jasonyi-zimbra/zm-mailbox

There wasn't an actual ticket number associated with the pull request, but for the sake of this demonstration, let's say it was a *bugfix* and the ticket number was `ZCS-1234`.  So the following steps assume you are in your local gitflow-enabled checkout of `zm-mailbox`.

First check out the base branch (in this case `feature/imap`) and make sure it is up to date with origin. Please note the use of the upper-case `-B` option.

	git fetch origin
	git checkout -B feature/imap origin/feature/imap


Next create the new *bugfix* branch to work with.  **Remember** that, by default, `develop` will be used as the base branch. But in this case, we need it to be based on `feature/imap`.

	gfb start zcs-1234 feature/imap


Next fetch the remote branch that the pull request is based on. You do *not* need to add a new remote first.  The syntax is as follows:

	git fetch REPO-URL REPO-BRANCH-NAME

Using the above-mentioned pull request as an example:

    git fetch https://github.com/jasonyi-zimbra/zm-mailbox feature/imap
    remote: Counting objects: 20, done.
    remote: Total 20 (delta 12), reused 12 (delta 12), pack-reused 8
    Unpacking objects: 100% (20/20), done.
    From https://github.com/jasonyi-zimbra/zm-mailbox
     * branch            feature/imap -> FETCH_HEAD

Take a look at that last line where it mentions `FETCH_HEAD`.  `cat` that file:

	cat .git/FETCH_HEAD

	2f189fa2fc24d3601544962cd2790381a54fe66f                branch 'feature/imap' of https://github.com/jasonyi-zimbra/zm-mailbox

So now we know the last commit that we just fetched from the remote fork & branch.  At this point, you can examine the git log and see what you need to bring in.


    git loll 2f189fa2fc24d3601544962cd2790381a54fe66f

    *  2f189fa [Jason Yi] Initialize ZimbraPerf to collect stats to imapd.csv
    *  fbabebd [Jason Yi] Initialize ZimbraPerf for ImapDaemon to collect stats to imapd.csv
    *  e761a54 [Gordon Tillman] ImapHandlerTest - fix test compile error
    *  b329a80 [Greg Solovyev] remove 'ignore' annotations from remote imap tests
    ...

Here `loll` is the following alias, defined in my `$HOME/.gitconfig` file:

    git config --get alias.loll
    log --graph --decorate --pretty='format: %h [%an]%d %s' --abbrev-commit


You can see the two commits from Jason that are in his pull request.  All we need to do is bring them in.  Here is the command. Explanation follows.

    git cherry-pick e761a54..2f189fa

#### Explanation:


* You had already created the sample bugfix branch and it was checked out, so the incoming commits will be handled properly.
* The two short commit hashes that complete the command are the base branch for the range of commits to bring in and the ending point for the range of commits.  From the snippet of log above, you can see that Jason's branch was based off of commit `e761a54` and ended with commit `2f189fa`.
* **Important:** The base and ending commits are specified using a *range* format; i.e., `BASE-COMMIT..END-COMMIT`.  If you were just bringing in a single commit, you can use the same syntax, or just specify the hash of the single commit to bring in.


So what do we have now?

    *  5e043e4 [Jason Yi] (HEAD -> bugfix/zcs-1234) Initialize ZimbraPerf to collect stats to imapd.csv
    *  b92f07d [Jason Yi] Initialize ZimbraPerf for ImapDaemon to collect stats to imapd.csv
    *    b1f6713 [Gordon Tillman] (origin/feature/imap, feature/imap) Merge branch 'feature/zcs-1515' into feature/imap
    |\
    | *  2a8ea26 [Gordon Tillman] ZCS-1515 Conditionaly init ephemeral backend extension
    | *  6ba2f0a [Gordon Tillman] ZCS-1515 Relocate initEphemeralBackendExtension
    | *  fedca33 [Gordon Tillman] ZCS-1515 PMD updates
    |/
    *  686fc6c [Gordon Tillman] (bugfix/zcs-1580) ImapHandlerTest - do not use Ehcache


At this point you may work with the new branch using the standard *gitflow* commands.  For example you can publish it to origin (`gfb publish zcs-1234`).  Once it has been tested/approved/etc., you finish it the same as any other *bugfix* branch:

    gfb finish zcs-1234
    git push origin feature/imap
    git push origin :zcs-1234

Explanation:


* The first command fetches from *origin*, rebases the *bugfix* branch on it's base branch (`feature/imap`), and merges it.
* The second command pushes the newly-updated `feature/imap` branch back to *origin*.
* The third command deletes the now-obsolete *bugfix* branch from *origin*. **NOTE:** as mentioned in the *Assumptions* at the top of this tutorial, this assumes you are have installed at least version 4 of the gitflow config via the `gitflow-config-init` command.
