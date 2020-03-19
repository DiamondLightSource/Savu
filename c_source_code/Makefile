.PHONY: distortion dezing all

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