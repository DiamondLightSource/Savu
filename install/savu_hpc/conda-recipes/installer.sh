#!/bin/bash

package=$1

echo "Building $package..."
conda build $recipes/$package
build=$(conda build $recipes/$package --output)

echo "Installing $package..."
conda install -y -q --use-local $build
