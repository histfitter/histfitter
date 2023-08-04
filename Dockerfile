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
    apt-get -qq -y install --no-install-recommends \
      cmake && \
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
    python -m pip --no-cache-dir install --upgrade pip setuptools wheel pytest-order && \
    python -m pip --no-cache-dir install --requirement /usr/local/HistFitter/requirements.txt

# Build HistFitter, make $HOME/.local/bin for .profile to find and add to PATH,
# automatically source HistFitter setup.sh
WORKDIR /usr/local
RUN root --version && \
    gcc --version && \
    g++ --version && \
    python --version --version && \
    cmake --version && \
    cd HistFitter && \
    cmake .
    #make -j$(($(nproc) - 1)) install && \
    #cd ../workdir && \
    #. ../install/bin/histfitter.sh && \
    #. ../install/bin/histfitter_setup_workdir.sh && \
    #mkdir -p ${HOME}/.local/bin && \
    #printf '\nif [ -f /usr/local/install/histfitter.sh ];then\n    . /usr/local/install/histfitter.sh\nfi\n' >> "${HOME}/.profile"

