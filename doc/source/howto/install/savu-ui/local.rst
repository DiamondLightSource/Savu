.. _`Podman`: https://podman.io/
.. _`Podman installation documentation`: https://podman.io/getting-started/installation
.. _`Docker`: https://www.docker.com/
.. _`Docker installation documentation`: https://docs.docker.com/get-docker/

How to install and run the Savu UI on a local machine
#####################################################

.. start_of_main_text

The currently supported containerisation software for running the Savu UI
are `Podman`_ and `Docker`_.

Podman
******

Installing Podman
=================

Please follow the `Podman installation documentation`_.

.. note:: The installation method of Podman should be the only difference
   between the various Linux based operating systems (ie, using a different
   package manager); from this point onwards, the steps should be the same for
   all Linux based operating systems.

Downloading the Savu UI container images
========================================

The container images that form the Savu UI are hosted on a public image
registry hosted by Google and maintained by Diamond. To download the relevant
container images, please run the following commands in a terminal:

.. code-block:: console

   podman pull gcr.io/diamond-pubreg/hebi/web:prod-local
   podman pull gcr.io/diamond-pubreg/hebi/api:prod-savu-lite-4.0_2021.09-py37_0
   podman pull gcr.io/diamond-pubreg/hebi/file-browser-server:format-flag


Running the Savu UI containers
==============================

Once the container images have been downloaded, please run the following
commands in a terminal to run the relevant containers:

.. code-block:: console

   podman pod create --name savu-ui-pod -p 8080:8080

   podman run --pod savu-ui-pod -d --name savu-ui-web \
       -e FEDID=$USER -e ACTIVATE_CAS_AUTH=False -e ACTIVATE_WEBSOCKET=False \
       gcr.io/diamond-pubreg/hebi/web:prod-local

   podman run --pod savu-ui-pod -d --name savu-ui-api \
       -v /home/$USER/:/files/home/$USER/ \
       gcr.io/diamond-pubreg/hebi/api:prod-savu-lite-4.0_2021.09-py37_0

   podman run --pod savu-ui-pod -d --name file-browser-server \
       -v /home/$USER/:/files/home/$USER/ \
       gcr.io/diamond-pubreg/hebi/file-browser-server:format-flag

It can be verified that all the contianers are running by using the command
:code:`podman ps -a` and looking at the :code:`STATUS` column of all the
containers. If all has gone well, the status of the three containers should
start with "Up", followed by the time since that container had first started
running.

When all the containers are verified to be running, open up a web browser and
navigate to the following address: http://localhost:8080, and that should
present the process list editor.

Docker
******

Installing Docker
=================

Please follow the `Docker installation documentation`_.

.. note:: Docker can be installed on Windows machines as well as Linux
   machines, so the installation process of Docker can be more varied depending
   on which operating system you are using.

Downloading the Savu UI container images
========================================

The Docker commands for downloading the Savu UI container images are largely
the same as the Podman commands, with the only difference being the use of
:code:`docker` instead of :code:`podman`:

.. code-block:: console

   sudo docker pull gcr.io/diamond-pubreg/hebi/web:prod-local
   sudo docker pull gcr.io/diamond-pubreg/hebi/api:prod-savu-lite-4.0_2021.09-py37_0
   sudo docker pull gcr.io/diamond-pubreg/hebi/file-browser-server:format-flag

Running the Savu UI containers
==============================

As with Podman, there are a few commands that need to be run in a terminal to
run the relevant containers from the downloaded images. The commands are
slightly different to the ones for Podman, most notably, the addition of the
:code:`--network host` flag:

.. code-block:: console

   sudo docker run -d --network host --name savu-ui-web \
       -e FEDID=$USER -e ACTIVATE_CAS_AUTH=False -e ACTIVATE_WEBSOCKET=False \
       gcr.io/diamond-pubreg/hebi/web:prod-local

   sudo docker run -d --network host --name savu-ui-api \
       -v /home/$USER/:/files/home/$USER/ \
       gcr.io/diamond-pubreg/hebi/api:prod-savu-lite-4.0_2021.09-py37_0

   sudo docker run -d --network host --name file-browser-server \
       -v /home/$USER/:/files/home/$USER/ \
       gcr.io/diamond-pubreg/hebi/file-browser-server:format-flag

Similarly to Podman, the containers can be checked to see if they are
up/running by using :code:`sudo docker ps -a` and looking at the :code:`STATUS`
column.  When all the containers are running, open up a web browser and
navigate to the following address: http://localhost:8080, and that should
present the process list editor.


Notes on running the Savu UI on a local machine
###############################################

Upon running the Savu UI successfully for the first time, the following will be
created on the **host machine**:

#. the directory :code:`/home/$USER/.hebi/`
#. the file :code:`/home/$USER/.hebi/config.yaml`
