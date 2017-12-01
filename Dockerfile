FROM cs04r-sc-vserv-74.diamond.ac.uk/diamond-apps/nvidia/cuda:9.0-devel-centos7
MAINTAINER Matthew Frost

USER root

# Deps
RUN yum groupinstall -y 'Development Tools'
RUN yum -y install wget
RUN yum install -y mesa-libGL-devel mesa-libGLU-devel


# Install FTTW3
ADD http://fftw.org/fftw-3.3.7.tar.gz /fftw-3.3.7.tar.gz
RUN tar -xf fftw-3.3.7.tar.gz
RUN /fftw-3.3.7/configure --enable-threads --enable-shared && make /fftw-3.3.7/ && make install /fftw-3.3.7/
RUN /fftw-3.3.7/configure --enable-threads --enable-shared --enable-float && make /fftw-3.3.7/ && make install /fftw-3.3.7/
RUN /fftw-3.3.7/configure --enable-threads --enable-shared --enable-long-double && make /fftw-3.3.7/ && make install /fftw-3.3.7/

# Download openmpi 3.0.0 and build it
ADD https://www.open-mpi.org/software/ompi/v3.0/downloads/openmpi-3.0.0.tar.gz /openmpi-3.0.0.tar.gz
RUN tar -xf openmpi-3.0.0.tar.gz
RUN /openmpi-3.0.0/configure --with-sge --enable-orterun-prefix-by-default && make /openmpi-3.0.0/ && make install /openmpi-3.0.0/

# Download Savu and build it
ADD https://savu.readthedocs.io/en/latest/_downloads/savu_v2.1.1.tar.gz /savu.tar.gz
RUN tar -xf savu.tar.gz

ADD savu_installer.sh /savu_v2.1.1/
ADD environment.yml /savu_v2.1.1/


ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

RUN chmod +x /savu_v2.1.1/savu_installer.sh
RUN /bin/bash /savu_v2.1.1/savu_installer.sh --no_prompts

ENV PATH=/root/miniconda/bin:$PATH

# Workaround
RUN pip install h5py

ENTRYPOINT ["/root/miniconda/bin/savu"]
