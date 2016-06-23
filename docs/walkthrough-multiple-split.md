# Multiple Folders Using Subtree Splits

This is a good method to use when you want to have multiple top-level folders to merge into an output repository.  It preserves commits, but not branch labels.  This walkthrough also uses the `zm-timezones` repository.


Start in your source repository and checkout the branch that you want to base your new repo on.  Here I use `judaspriest-870`

	pushd zcs-full
	git checkout -b judaspriest-870

Now split out the subtrees into separate branches that you are going to need.  For `zm-tiemzones` I need the following pieces:

- `ZimbraServer/conf`
- `ZimbraWebClient/WebRoot/messages`

Splitting out `ZimbraServer/conf`

	git subtree split --prefix=ZimbraServer/conf -b zs-conf

Splitting out `ZimbraWebClient/WebRoot/messages`

	git subtree split --prefix=ZimbraWebClient/WebRoot/messages -b zwc-messages

So at this point we have the following three branches:

- `judaspriest-870` - the one we checked out originally
- `zs-conf` - the branch that was created from the subtree split of the `ZimbraServer/conf` top-level directory
- `zwc-messages` - the branch that was created from the subtree split of the `ZimbraWebClient/WebRoot/messages` directory.

The next step is to pull both the two new branches out into the new repository.

Create the new output repository and initialize it with a commit.  This will establish the branch called `master`.

	popd
	mkdir zm-timezones
	pushd zm-timezones
	git init
	echo 'TODO - README' > README.md
	git add README.md
	git commit -m 'initial commit'


Pull in the first branch (zs-conf).  Start by adding `zcs-full` as a remote and fetching branch info (via the `-f` option):


	git remote add -f origin ../zcs-full

You should now see the following:


    $ git branch -r
    
      origin/judaspriest-870
      origin/zs-conf
      origin/zwc-messages

Pull in the first branch (zs-conf) into it's own subdirectory called `conf`:


	git merge -s ours --no-commit origin/zs-conf
	git read-tree --prefix=conf/ -u origin/zs-conf
	git commit -m 'Merged zs-conf as subdirectory'


Pull in the second branch (zwc-messages) into it's own subdirectory (`WebRoot/messages`):

	git merge -s ours --no-commit origin/zwc-messages
	git read-tree --prefix=WebRoot/messages/ -u origin/zwc-messages
	git commit -m 'Merged zwc-messages as subdirectory'

At this point the new repo looks like this:


    git branch
    * master
    
    ls
    conf  README.md  WebRoot


The next thing you need to do is remove the files and directories that you do not need in the new repository.  There are a couple of ways to do this:

1. Rewrite the entire history by going through every command and removing those items you do not require. The `clone-and-filter-repo` script can automate this task for you.  This will result in the smallest possible repository. **Warning:** It does take a long time due to the large number of commits and the large number of operations that must be performed for each of those commits.
2. With the `master` branch checked out, manually delete everything that you do not want via the `git rm` command and commit your change.  This is very fast, but because all of the deleting items remain in the prior history, the new repository is larger than it needs to be.

Here is a demonstration of option 1.  Starting in the parent directory of your new repo, do the following.

	
Create a paths file. We'll call it `zm-timezones.paths`:

	./conf/tz
	./conf/timezones.ics
	./WebRoot/messages/AjxMsg

The following command:

	./clone-and-filter-repo -d zm-timezones -i zm-timezones.paths -r


	
