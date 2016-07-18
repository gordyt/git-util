# Walkthrough, Shrink Repo

## zm-common walkthrough

This is an example of steps taken to reduce the size of the `zm-common` git repository to find and remove paths that do not belong there, from every commit.  Credits to Shrikant for requesting this.

### Initial Repo Creation

Here we create the `zm-common` repo, which is just a simple subtree extraction:

    clone-and-filter-repo -s ~/Projects/z/zcs-full -d zm-common -f ZimbraCommon

What do we end up with?

	cd zm-common
	ls -1

    build.xml
    conf
    pom.xml
    qatool.txt
    src
    ZimbraCommon.iml

### Analysis

How big is the repo?

	du -sh .
	79M

Why so big?

    analyze-repo
    
    All sizes are in kB. The pack column is the size of the object, compressed, inside the pack file.
    size   pack  SHA                                       location
    12083  4908  36b1613639986e554c9840e4de5739d1c644ec95  ImportWizard/ImportWizard.ncb
    6900   1238  0b233a0f2b2418a5155144c9ebe00f8d922e7605  Prototypes/prototypes/SearchPods/search                   pods.dir
    5900   725   4b18e3338c0c07e642faff24be7660dc4e9ff0cc  ZimbraWebClient/img/sourceimages/master                   iconfactory   icons.psd
    4848   315   a0dbb29a1236294651fb7fc7726da7ee307a8b99  ZimbraWebClient/WebRoot/skins/walnut/walnut_template.psd
    3402   3387  f8fde63597c50fb963b71517d87e35998e1c16f6  Prototypes/prototypes/SearchPods/searchpods_movie.mov
    3326   379   97dbb1a78fc77c378677c59c2bd4987e7e1446f0  Prototypes/old                                            icons/Liquid  icons      050726.psd

### Fix

We can see paths from other subtrees, including some binaries.  How to fix?  Notice that when I ran `clone-and-filter-repo` to perform tree filtering with deletes based upon some include paths, I did not specify a base branch (via `-b <BRANCH>`) to base the computation on.  This means that *every* branch will be examined to look for paths that should be deleted.

	find . -maxdepth 1 | grep -E --invert-match '\.$|\.git' > ../paths
    cd ..
    clone-and-filter-repo -r -d zm-common -i paths


How big is the repo now?

    du -sh zm-common
    16M     zm-common

So a significant reclamation of space.

## zm-client walkthrough

This is an example of steps taken to reduce the size of the `zm-client` git repository to find and remove paths that do not belong there, from every commit.  Credits to Rupali for requesting this.

### Initial Repo Creation

    ~/Projects/z/clone-and-filter-repo -s ~/Projects/z/zcs-full -d zm-client -f ZimbraClient2

Results:

	du -sh zm-client
	623M    zm-client

	cd zm-client
	ls -1
	
	build.xml
	pom.xml
	src

### Analysis

    analyze-repo
    
    All sizes are in kB. The pack column is the size of the object, compressed, inside the pack file.
    size   pack   SHA                                       location
    59648  12909  475121e52d0f0d7af5ddc6cf43194cd147ab67c3  ZimbraMigrationTools/src/c/Exchange/MapiExchange/ipch/mapiexchange-73f64a8/mapiexchange-224e0056.ipch
    47764  13450  58ff61719906d801256dcb994bf0aa7d5d5c544a  ZimbraMigrationTools/src/c/Exchange/MapiExchange/MapiExchange.sdf
    25386  24989  195560faf9b8365da4a7d59eb043b8418abed497  ZimbraMAPIInstaller/Tools/Wix35.msi
    21270  4776   b1794d72cbc80ebab47496c85fd4550dba329665  ZimbraDocs/Zimbra                                                                                      User               Guide_7_0/pdf/Zimbra-User-Guide.ps
    20571  20277  dc0b5f6c6716abc5a8eec2a50eb8125e21dbae1f  ZimbraMAPIInstaller/Tools/Wix35.msi
    20190  1754   17eb56d7b597d6a94dd425f08e1f7576e334c1a8  ZimbraDocs/Zimbra_Connectors/ZCO                                                                       User               Guide/User                          Instructions         Connector  for      Outlook.fm
    19408  2286   6263b9b8e135ae1244e4b26b16137f2f31da12d9  ZimbraDocs/Migration_Import_Guides/Migration                                                           Wizard/MigWizards  with                                conditional_text.fm
    18696  2451   26732106eb9a44fa9dfe35e882673048cd9678f7  ZimbraDocs/Zimbra                                                                                      Desktop/Zimbra     Desktop                             Install              Guide/ZD   install  reference.fm
    18432  5583   01fd0bfddf988a8f8526929dff1ebeb76929b7e8  ZimbraMigrationTools/src/c/Exchange/MapiExchange/MapiExchange/Debug/MapiExchange.pch
    16436  2326   4505d66bafa26c9ed5accef026a202a045d7b8e7  ZimbraDocs/Admin_Guide/Appliance/pdf/ZCA_Administration_Guide.ps


### Fix

	find . -maxdepth 1 | grep -E --invert-match '\.$|\.git' > ../paths
	cd ..
	clone-and-filter-repo -r -d zm-client -i paths

Resulting size:

    du -sh zm-client/
    17M     zm-client/


## Comments

You can run the tree-filter step multiple times if you like.  When processing our big repos I've noticed it is not uncommon to see messages like this:

	 error: duplicate parent 32134aaf47f4bce8e8e76dcdaf08561d13176328 ignored

From what I've been able to find, there are a couple of situations that will cause this error message to be displayed:

- There is an existing commit that has the same parent more than once.  You can manually run the command `git filter-branch` with no arguments and git can repair this.
- You have a commit with a pair of parents that are currently distinct but which become identical after the changes done by the `filter-branch` operation.  This is the likely case in our scenario.  This is not a problem and you can ignore that message.


