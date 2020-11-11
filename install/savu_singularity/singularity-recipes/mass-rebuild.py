#!/usr/bin/env python3

import os
import sys
import getpass
from collections import namedtuple
from spython.main import Client as spython_client
import base64
from pathlib import Path

SavuImage = namedtuple('SavuImage', ['name', 'push'])

images = (
        SavuImage('SavuDeps', push=False),
        SavuImage('SavuCore', push=False),
        SavuImage('SavuAstra', push=True),
        )

GOOGLE_CREDENTIALS_FILE = Path.home() / 'google-credentials.json'

# sregistry should be used only when building locally or when on CIRCLECI and branch is master
use_sregistry = False

if 'CIRCLE_TAG' in os.environ or os.environ.get('CIRCLE_BRANCH') == 'master' or 'CIRCLECI' not in os.environ:
    import sregistry
    use_sregistry = True
    os.environ['SREGISTRY_CLIENT'] = 'google-storage' # activate google-storage backend
    os.environ['SREGISTRY_GOOGLE_STORAGE_BUCKET'] = 'singularity-savu' # name of the GS bucket
    GOOGLE_CREDENTIALS_FILE.write_bytes(base64.decodebytes(os.environ['GOOGLE_CREDENTIALS'].encode()))
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(GOOGLE_CREDENTIALS_FILE)
    from sregistry.main import get_client
    sregistry_client = get_client()



username = getpass.getuser()
sudo_options = None

if use_sregistry and os.path.isdir(os.path.join('/dls/science/users', username)):
    # DLS specific settings, for a local build on our RHEL7 workstations
    os.environ['SREGISTRY_DATABASE'] = os.path.join('/dls/science/users', username, 'singularity')
    os.environ['SREGISTRY_STORAGE'] = os.path.join(os.environ['SREGISTRY_DATABASE'], 'shub')
    os.environ['SREGISTRY_TMPDIR'] = os.path.join('/', 'scratch', 'tmp')
    os.makedirs(os.environ['SREGISTRY_STORAGE'], exist_ok=True)
    os.environ['SINGULARITY_CACHEDIR'] = os.path.join('/', 'scratch', 'singularity')
    os.environ['SINGULARITY_TMPDIR'] = os.path.join('/', 'scratch', 'tmp')
    sudo_options = '--preserve-env=SINGULARITY_CACHEDIR,SINGULARITY_TMPDIR'



for image in images:

    local_image = image.name + '.simg'
    registry_image = 'savu/' + local_image[4:].lower()

    if 'CIRCLE_TAG' in os.environ:
        registry_image += ':' + os.environ['CIRCLE_TAG']
    elif os.environ.get('CIRCLE_BRANCH') == 'master':
        registry_image += ':' + os.environ['CIRCLE_SHA1'][:8]

    print('#########################')
    print('#')
    print(('#   Building {}'.format(image.name)))
    print(('#   local_image: {}'.format(local_image)))
    print(('#   registry_image: {}'.format(registry_image)))
    print('#')
    print('#########################')

    #
    # remove the image, if it has been built before, including from local registry
    #
    try:
        os.unlink(local_image)
    except FileNotFoundError:
        pass

    if 'CIRCLECI' not in os.environ and use_sregistry is True:
        sregistry_client.rm(registry_image)

    #
    # build the image
    #
    spython_client.quiet = False # circumvent problem with sregistry setting this attribute to True, which kills my local builds!
    filename = spython_client.build(recipe='Singularity.' + image.name, image=local_image, sudo_options=sudo_options)
    if filename is None:
        print(("Error creating singularity image {}".format(local_image)))
        sys.exit(1)

    #
    # add to local registry
    #
    if 'CIRCLECI' not in os.environ and use_sregistry is True:
        sregistry_client.add(image_path=local_image, image_uri=registry_image, copy=True)

    #
    # push to GS bucket
    #
    if image.push is True and use_sregistry is True and 'CIRCLECI' in os.environ:
        print(("Pushing {} to {}".format(local_image, registry_image)))
        sregistry_client.push(path=local_image, name=registry_image)

