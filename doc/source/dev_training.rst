Savu Diamond User Training
**************************

Github Savu
===========

To become a Savu developer you will need your own Savu Github repository and a clone on your local machine.  
The basic commands to do this are listed below; for a more detailed explanation see 

https://help.github.com/articles/fork-a-repo/

Set up your Savu Github repository (**DO THIS ONCE**)
-----------------------------------------------------

1. Navigate to https://github.com/DiamondLightSource/Savu and click on Fork (right hand corner).
2. Navigate to **YOUR FORK** of the repository and copy the url e.g. |A| (ensure SSH is chosen)..

.. |A| image:: ../../images/ssh_url.png

3. Open a terminal (or command prompt) on your local machine, change a relevant folder to install Savu, and follow the instructions below: 

    >>> git clone <ssh url>

    >>> ssh-keygen -t rsa -b 4096 -C "your_github_email@example.com".

    >>> git remote add upstream git@github.com:DiamondLightSource/Savu.git

    .. note:: You may need to generate an ssh key. See https://help.github.com/articles/generating-a-new-ssh-key/  




.. _my-reference-label:

Maintain **YOUR** Savu repository
---------------------------------
You can now go ahead and make changes to your local copy of Savu.  These changes need to be frequently *committed* to your **local** repository
and periodically *pushed* to your **remote** repository on GitHub.  

To see a list of files that you have recently updated and **NOT** yet committed:

    >>> git status

To commit these changes locally:

    >>> git commit -a -m "your commit message here" 

To push these changes to your remote GitHub repository:
   
    >>> git push



Keep **YOUR** repository up-to-date with the **ORIGINAL**
---------------------------------------------------------

    >>> git pull upstream

Then follow the steps in :ref:`my-reference-label`.


Tracking and untracking files
-----------------------------

    >>> git status 

gives a list of tracked and untracked files (if there are any).  Untracked files are only held locally and changes to
these files will not be tracked by the repository.  If you create a new file, it will not automatically be tracked by
the repository. 


To track a file
---------------

>>> git status
>>> git add <untracked file_path>

Then commit and push as per :ref:`my-reference-label`.

To untrack a file
-----------------

>>> git rm <option> <file_path>

option is ``--cached`` if you want to untrack the file but keep a local copy.  

option is ``-f`` if you want to completely delete the file.  


See the Git Cheat Sheet for additional commands https://training.github.com/kit/downloads/github-git-cheat-sheet.pdf

