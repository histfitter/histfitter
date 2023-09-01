FROM atlasamglab/stats-base:root6.28.00 as base

SHELL [ "/bin/bash", "-c" ]

USER root
WORKDIR /usr/local/
COPY . HistFitter

RUN mkdir build && \
    mkdir install && \
    mkdir workdir

# Add non-root user "docker" with relevant control and update pip
RUN apt-get -qq -y update && \
    apt-get -qq -y install --no-install-recommends \
      git && \
    apt-get -y autoclean && \
    apt-get -y autoremove && \
    rm -rf /var/lib/apt/lists/* && \
    useradd --shell /bin/bash -m docker && \
    cp /root/.profile /home/docker/ && \
    cp /root/.bashrc /home/docker/ && \
    chown -R --from=root docker /home/docker && \
    chown -R --from=root docker /usr/local/HistFitter && \
    chown -R --from=root docker /usr/local/build && \
    chown -R --from=root docker /usr/local/install && \
    chown -R --from=root docker /usr/local/workdir && \
    curl -s "https://cmake.org/files/v3.27/cmake-3.27.0-linux-x86_64.tar.gz" | tar --strip-components=1 -xz -C /usr/local && \
    export PATH=/usr/local/cmake-3.27/bin:$PATH && \
    python -m pip --no-cache-dir install --upgrade pip setuptools wheel pytest-order && \
    python -m pip --no-cache-dir install --requirement /usr/local/HistFitter/requirements.txt

# Build HistFitter, make $HOME/.local/bin for .profile to find and add to PATH,
# automatically source HistFitter setup.sh
#Delete source and build repos to properly test install
WORKDIR /usr/local
RUN root --version && \
    gcc --version && \
    g++ --version && \
    python --version --version && \
    cmake --version && \
    cd build && \
    cmake -DCMAKE_INSTALL_PREFIX=/usr/local/install /usr/local/HistFitter && \
    make -j$(($(nproc) - 1)) install && \
    rm -rf ../HistFitter && \
    rm -rf ../build && \
    cd ../workdir && \
    . ../install/bin/setup_histfitter.sh && \
    mkdir -p ${HOME}/.local/bin

ENTRYPOINT ["/bin/bash", "-l", "-c"]
CMD ["/bin/bash"]