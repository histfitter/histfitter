FROM atlasamglab/stats-base:root6.22.08-python2.7 as base

USER root
COPY . /HistFitter

# Create user "docker"
RUN useradd --shell /bin/bash -m docker && \
   cp /root/.profile /home/docker/ && \
   cp /root/.bashrc /home/docker/ && \
   chown -R --from=root docker /home/docker && \
   chown -R --from=root docker /HistFitter

USER docker
ENV HOME=/home/docker

WORKDIR /HistFitter
RUN root --version && \
    gcc --version && \
    python --version --version && \
    make --version && \
    . setup.sh && \
    cd src && \
    make -j$(($(nproc) - 1)) && \
    mkdir /home/docker/data

WORKDIR /home/docker/data
