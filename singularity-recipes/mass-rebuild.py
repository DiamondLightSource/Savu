#!/usr/bin/env python3

import os
import getpass
from collections import namedtuple
from spython.main import Client as spython_client

SavuImage = namedtuple('SavuImage', ['name', 'push'])

images = (
        SavuImage('SavuDeps', push=False),
        SavuImage('SavuCore', push=False),
        SavuImage('SavuAstra', push=True),
        )


# sregistry should be used only when locally or when on CIRCLECI and branch is master
use_sregistry = False

#if os.environ['CIRCLE_BRANCH'] == 'master' or 'CIRCLECI' not in os.environ:
if 'CIRCLE_BRANCH' in os.environ or 'CIRCLECI' not in os.environ:
    import sregistry
    use_sregistry = True
    os.environ['SREGISTRY_CLIENT'] = 's3'
    os.environ['SREGISTRY_S3_BUCKET'] = 'singularity-savu'
    from sregistry.main import get_client
    sregistry_client = get_client()



username = getpass.getuser()
sudo_options = None

if use_sregistry and os.path.isdir(os.path.join('/dls/science/users', username)):
    os.environ['SREGISTRY_DATABASE'] = os.path.join('/dls/science/users', username, 'singularity')
    os.environ['SREGISTRY_STORAGE'] = os.path.join(os.environ['SREGISTRY_DATABASE'], 'shub')
    os.makedirs(os.environ['SREGISTRY_STORAGE'], exist_ok=True)
    os.environ['SINGULARITY_CACHEDIR'] = os.path.join('/', 'scratch', 'singularity')
    os.environ['SINGULARITY_TMPDIR'] = os.path.join('/', 'scratch', 'tmp')
    sudo_options = '--preserve-env=SINGULARITY_CACHEDIR,SINGULARITY_TMPDIR'



for image in images:

    local_image = image.name + '.simg'
    registry_image = 'savu/' + local_image[4:].lower()

    if 'CIRCLE_TAG' in os.environ:
        registry_image += ':' + os.environ['CIRCLE_TAG']
    #elif os.environ['CIRCLE_BRANCH'] == 'master':
    elif 'CIRCLE_BRANCH' in os.environ:
        registry_image += ':' + os.environ['CIRCLE_SHA1'][:8]

    print('#########################')
    print('#')
    print('#   Building {}'.format(image.name))
    print('#   local_image: {}'.format(local_image))
    print('#   registry_image: {}'.format(registry_image))
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
    spython_client.build(recipe='Singularity.' + image.name, image=local_image, sudo_options=sudo_options)

    #
    # add to local registry
    #
    if 'CIRCLECI' not in os.environ and use_sregistry is True:
        sregistry_client.add(image_path=local_image, image_uri=registry_image, copy=True)

    #
    # push to S3 bucket
    #
    if image.push is True and use_sregistry is True and 'CIRCLECI' in os.environ:
        print("Pushing {} to {}".format(local_image, registry_image))
        sregistry_client.push(path=local_image, name=registry_image)

