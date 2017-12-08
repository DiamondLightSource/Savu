
FROM docker-registry.diamond.ac.uk/diamond-apps/nvidia/cuda:9.0-devel-centos7
MAINTAINER Matthew Frost

USER root

# Deps
RUN yum groupinstall -y 'Development Tools'
RUN yum -y install wget 
RUN yum install -y mesa-libGL-devel mesa-libGLU-devel

ENV VERSION=2.2
ENV FTTW=3.3.7
ENV OPENMPI=3.0.0

# Install FTTW3
ADD http://fftw.org/fftw-${FTTW}.tar.gz /fftw-${FTTW}.tar.gz
RUN tar -xf fftw-${FTTW}.tar.gz
RUN /fftw-${FTTW}/configure --enable-threads --enable-shared && make /fftw-${FTTW}/ && make install /fftw-${FTTW}/
RUN /fftw-${FTTW}/configure --enable-threads --enable-shared --enable-float && make /fftw-${FTTW}/ && make install /fftw-${FTTW}/
RUN /fftw-${FTTW}/configure --enable-threads --enable-shared --enable-long-double && make /fftw-${FTTW}/ && make install /fftw-${FTTW}/

# Download openmpi ${OPENMPI} and build it 
ADD https://www.open-mpi.org/software/ompi/v3.0/downloads/openmpi-${OPENMPI}.tar.gz /openmpi-${OPENMPI}.tar.gz
RUN tar -xf openmpi-${OPENMPI}.tar.gz 
RUN /openmpi-${OPENMPI}/configure --with-sge --enable-orterun-prefix-by-default && make /openmpi-${OPENMPI}/ && make install /openmpi-${OPENMPI}/

# Download Savu and build it  
ADD https://savu.readthedocs.io/en/latest/_downloads/savu_v${VERSION}.tar.gz /savu.tar.gz
RUN tar -xf savu.tar.gz

ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

RUN chmod +x /savu_v${VERSION}/savu_installer.sh
RUN /bin/bash /savu_v${VERSION}/savu_installer.sh --no_prompts

ENV PATH=/root/miniconda/bin:$PATH

ENTRYPOINT ["/root/miniconda/bin/savu"]
