# Reading and Writing Nero .nra files.

This repository contains some routines to read and write Nero audio CD
project files, files that have a '.nra' suffix.  The files included
here contain my best guess at the format of the NRA file.

I did this because I had a reason to create Nero projects by reading a
database.  I have a copy of Nero and have no intention of replacing
it, I just needed to supplement it.  This is very much a work in
progress but I should share what I have learned in case anybody else
is goofy enough to want to do something similar.

My interpretation of the file format seems to work but could be
desperately wrong.  The files contained here are totally open and free
and anyone can do anything they want with them.  If you learn
something new please let me know.

I built and use these routines on a debian linux machine.  I have
never (and will never) run them on a Windows machine or an Apple.
There are some strange things in the code that are an artifact of this
approach.

Some notes, mostly to myself.

* I used emacs hexl mode heavily to do this.

* I used some linux tools to look at CDs.

  * libcdio based utilities

    To learn about your drive's capabilities use cd-drive

    To get an analysis of the disc including CD-TEXT use cd-info

    To read raw blocks from a CD (replace 1 and 5 with what you want)
    cd-read --mode=audio --start=1 --end=5


  * To create a toc file from a CD
    cdrdao read-toc xxx.toc
