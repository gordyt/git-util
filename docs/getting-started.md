## Getting Started

Make sure you have a fairly recent version of git installed. I would recommend at least version `1.9.1`.

You should set-up the global git configuration file.  It is named `.gitconfig` and it should be placed in your `$HOME` directory.  Please see the [sample git config file](../config/DOT.gitconfig) for a reasonable set of defaults.

## Creating a new, empty repository

You can create new git repositories anywhere.  The basic syntax is...

	git init REPO-NAME

...where `REPO-NAME` is the name of the new repository that you wish to create.  Here is an example:

	$ git init sample-repo

	Initialized empty Git repository in /Users/gordy/tmp/sample-repo/.git/

	$ cd sample-repo
	$ ls -al

    total 0
    drwxr-xr-x   3 gordy  staff   102 Jul 25 09:53 .
    drwxr-xr-x  73 gordy  staff  2482 Jul 25 09:53 ..
    drwxr-xr-x   9 gordy  staff   306 Jul 25 09:54 .git

	$ git branch
	
	<no output>

At this point you have a new diretory that contains a newly-initialized `.git` directory.  This `.git` directory is where git keeps all of the information related to the objects that are tracked.

Adding a new file is easy.

	echo "this is a test" > README.txt

Check the status of the repo:

    $ git status
    
    On branch master
    
    Initial commit
    
    Untracked files:
      (use "git add <file>..." to include in what will be committed)
    
    	README.txt
    
    nothing added to commit but untracked files present (use "git add" to track)

Notice that git provides a bit of guidance where possible.  To make git start tracking changes on your new file, you must `add` the file as follows:

	$ git add README.txt

Check the status again.

    $ git status
    
    On branch master
    
    Initial commit
    
    Changes to be committed:
      (use "git rm --cached <file>..." to unstage)
    
    	new file:   README.txt

So git knows about your new file.  Adding a file in git basically stages the file so that when you *commit* your changes, the file's state (at the time you executed the `git add FILE` command) will be captured into a commit.

    $ git commit -m 'initial creation of README'
    
    [master (root-commit) d7ccb50] initial creation of README
     1 file changed, 1 insertion(+)
     create mode 100644 README.txt

Check status again.

    $ git status
    
    On branch master
    nothing to commit, working directory clean

List your local branches:

    $ git branch
    
    * master

## Working with remotes

A remote is another copy of the repository that you are working with.  You can have as many remotes "registered" with your repo as you wish.  In working with the collection of repositories in the *Zimbra* projects, you will typically have the following remotes registered in your local copy of any given repository:

- Your *fork* of a repository in the *Zimbra* project
- The actual repository in the *Zimbra* project

More information about working with remotes can be found in the [basic workflow](basic-workflow.md) document.
