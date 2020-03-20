.PHONY: distortion dezing all

# This will build both dezing and distortion(unwarp)
# and "install" them by moving the built shared objects
# into the ../lib folder they are expected.
# Currently this is done in ./savu_installer.sh
# at the conda build of the savu recipe.
all: clean dezing distortion
	mkdir -p ../lib
	mv dezing/dezing.cpython*.so ../lib
	mv distortion/unwarp.cpython*.so ../lib

distortion:
	cd distortion; ./clean.sh; ./buildfloat.sh

dezing:
	cd dezing; ./clean.sh; ./build.sh

clean:
	# go back to source root and attempt to delete the lib folder, if it exists
	cd ..; if [[ -d ./lib ]]; then rm -r ./lib; fi
	cd dezing; ./clean.sh
	cd distortion; ./clean.sh