mkdir -p ${SRC_DIR}/tomophantom
cd tomophantom

#issue cmake to create setup.py
cmake -G "Unix Makefiles" ../ -DBUILD_PYTHON_WRAPPER=ON -DCONDA_BUILD=ON -DCMAKE_BUILD_TYPE="Release" -DLIBRARY_LIB=$CONDA_PREFIX/lib -DLIBRARY_INC=$CONDA_PREFIX -DCMAKE_INSTALL_PREFIX=$PREFIX
make install

