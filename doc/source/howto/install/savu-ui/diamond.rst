How to run the Savu UI at Diamond
#################################

.. start_of_main_text

There are two ways that the Savu UI can be run at Diamond:

#. production deployment using Kubernetes (for beamline staff and users)
#. development deployment using Podman (for developers)


Production deployment using Kubernetes
**************************************

Start by visiting the following URL: https://hebi.diamond.ac.uk/launcher/.
It should present you with a webpage that looks like this:

.. image:: /files_and_images/hebi-launcher-login-page.png


From that webpage, click the "Login" button, and this should redirect to a
Diamond CAS webpage asking you to provide your FedID and password:

.. image:: /files_and_images/hebi-launcher-cas-login.png


After providing your login credentials and clicking "Login", it should briefly
show a webpage saying that you have been successfully authenticated:

.. image:: /files_and_images/hebi-launcher-login-success.png


.. note:: If you have logged into another Diamond web app using CAS
   authentication (such as JIRA or Confluence), the "Login" button at
   https://hebi.diamond.ac.uk/launcher/ will redirect straight to the
   successful authentication webpage.


You should then be presented with a webpage with two buttons labelled "Start a
new session" and "Continue session":

.. image:: /files_and_images/hebi-launcher-main-page.png


Click "Start a new session", after which there will be a wait of around 5 - 10
seconds, before then redirecting to the process list editor in the Savu UI:

.. image:: /files_and_images/hebi-process-list-editor.png
