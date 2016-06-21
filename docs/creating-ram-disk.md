# Creating a RAM disk

These instructions are written for use on a typical Linux system.  In particular, I did the following from an Ubuntu 14.04 machine.

First, create a directory that will serve as the mounting point for your RAM disk.  By the way, all of the following operations were performed as the `root` user.


	mkdir -p /mnt/working

## Creating a permanent RAM disk

Make a backup of your fstab file, in case things get messed up.

	cp /etc/fstab /etc/fstab.bak

Edit the `/etc/fstab` file and add a line like the following. Note that the following creates a 6 GB RAM disk:

	tmpfs /mnt/working tmpfs rw,size=6G 0 0

Now mount it:

	mount -a

Then change ownership to your normal user.  Be sure and replace `<user>` with your username.

	chown <user>:<user> /mnt/working

## Creating a temporary RAM disk

This will not require that you make any changes to your `/etc/fstab` file.  If you reboot your system you will have to recreate it.  That's no big deal.  Remember, if you reboot you will lose whatever was in your RAM disk anyway...


	mount -t tmpfs -o size=6G tmpfs /mnt/working

And, again, assign ownership as before:

	chown <user>:<user> /mnt/working

