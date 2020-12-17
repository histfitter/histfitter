FROM atlasamglab/stats-base:root6.20.06-python3.8 as base

SHELL [ "/bin/bash", "-c" ]

USER root
WORKDIR /usr/local/
COPY . HistFitter

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
    python3 -m pip --no-cache-dir install --upgrade pip setuptools wheel && \
    python3 -m pip --no-cache-dir install --requirement /usr/local/HistFitter/requirements.txt

USER docker
ENV HOME=/home/docker

# Build HistFitter, make $HOME/.local/bin for .profile to find and add to PATH,
# make $HOME/data user controlled, and automatically source HistFitter setup.sh
WORKDIR /usr/local/HistFitter
RUN root --version && \
    gcc --version && \
    python --version --version && \
    make --version && \
    . setup.sh && \
    cd src && \
    make -j$(($(nproc) - 1)) && \
    mkdir -p "${HOME}/.local/bin" && \
    mkdir "${HOME}/data" && \
    printf '\nif [ -f /usr/local/HistFitter/setup.sh ];then\n    . /usr/local/HistFitter/setup.sh\nfi\n' >> "${HOME}/.profile"

WORKDIR "${HOME}/data"

ENTRYPOINT ["/bin/bash", "-l", "-c"]
CMD ["/bin/bash"]
