
FROM docker-registry.diamond.ac.uk/diamond-apps/nvidia/cuda:9.0-devel-centos7
MAINTAINER Matthew Frost

USER root

# Deps
RUN yum groupinstall -y 'Development Tools' && yum install -y mesa-libGL-devel mesa-libGLU-devel wget boost-devel && yum clean all && rm -rf /var/cache/yum

ENV VERSION=2.3.1
ENV FTTW=3.3.8
ENV OPENMPI=3.1.3

# Install FTTW3
ADD http://fftw.org/fftw-${FTTW}.tar.gz /fftw-${FTTW}.tar.gz
RUN tar -xf fftw-${FTTW}.tar.gz && \
    /fftw-${FTTW}/configure --enable-threads --enable-shared --disable-static && make /fftw-${FTTW}/ && make install /fftw-${FTTW}/ && make clean /fftw-${FTTW}/ && \
    /fftw-${FTTW}/configure --enable-threads --enable-shared --enable-float --disable-static && make /fftw-${FTTW}/ && make install /fftw-${FTTW}/ && make clean /fftw-${FTTW}/ && \
    /fftw-${FTTW}/configure --enable-threads --enable-shared --enable-long-double --disable-static && make /fftw-${FTTW}/ && make install /fftw-${FTTW}/ && rm -rf /fftw*

# Download openmpi ${OPENMPI} and build it 
ADD https://www.open-mpi.org/software/ompi/v3.1/downloads/openmpi-${OPENMPI}.tar.gz /openmpi-${OPENMPI}.tar.gz
RUN tar -xf openmpi-${OPENMPI}.tar.gz && \
    /openmpi-${OPENMPI}/configure --with-sge --enable-orterun-prefix-by-default --disable-static && make /openmpi-${OPENMPI}/ && make install /openmpi-${OPENMPI}/ && rm -rf /openmpi*

ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

# Get and install Savu 
COPY get-and-install-savu.sh /get-and-install-savu.sh
RUN chmod +x /get-and-install-savu.sh && \
    /get-and-install-savu.sh $VERSION

ENV PATH=/root/miniconda/bin:$PATH

ENTRYPOINT ["/root/miniconda/bin/savu"]
