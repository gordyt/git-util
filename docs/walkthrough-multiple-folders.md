# Walkthrough, Multiple Folders, Full History

This is an example walkthrough to demonstrate how to create a new component-specific repo that is based off of more than one top-level directory from the source repository.  For this example we will be doing the `zm-timezones` repo.

These are the mappings from the `zcs-full` repository to the new `zm-timezones` repo:

**zcs-full path**                        | **zm-timezones path**
---------------------------------------- | -----------------------
ZimbraServer/conf/tz (directory)         | conf/tz
ZimbraServer/conf/timezones.ics          | conf/timezones.ics
ZimbraWebClient/WebRoot/messages/AjxMsg* | WebRoot/messages/AjxMsg*

A couple of things to note:

- The first two paths come from the top-level `ZimbraServer` directory.
- The third path comes from the top-level `ZimbraWebClient` directory.
- The third path must filter out all of the properies files whose name starts with `AjxMsg`.

For this example we will make use of the [clone-and-filter-repo](../bin/clone-and-filter-repo) script to do the heavy lifting.

## Setup

The instructions that follow assume you have a local copy of the `zcs-full` repository, with all branches replicated to it (assuming you want history from all branches).

Create a file that contains all of the paths from `zcs-full` that you want to remain in the new repository.  Let's call it `zm-timezones.paths`.  It should have the following contents:

    ./ZimbraServer/conf/tz
    ./ZimbraServer/conf/timezones.ics
    ./ZimbraWebClient/WebRoot/messages/AjxMsg


Three things to note:

- In this case, since we are doing only a tree-filter and not *first* applying a sub-directory filter, you must specify the full path, including the top-level directory.
- All paths start with `./`
- No trailing slashes.  Note that the third entry above will case the filter to include only those message files that start with `AjxMsg`.


    - `zcs-full` - A clone of the repo from stash with all branches replicated locally.
	- `clone-and-filter-repo` - The utility script
	- `zm-timezones.paths` - The paths file we created above.

Here is the command:

	./clone-and-filter-repo -s zcs-full -d zm-timezones -i zm-timezones.paths -b judaspriest-870


The tree-filter will take a *long* time to run. It has to remove a long list of paths from each of the 147163 commits.

When it is finished, just check out the branch that you want to work with and use `git mv` commands to rearrange the remaining parts as you like.
