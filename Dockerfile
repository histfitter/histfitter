FROM atlasamglab/stats-base:root6.22.08-python2.7 as base

SHELL [ "/bin/bash", "-c" ]

USER root
WORKDIR /usr/local/
COPY . HistFitter

# Create user "docker"
RUN useradd --shell /bin/bash -m docker && \
   cp /root/.profile /home/docker/ && \
   cp /root/.bashrc /home/docker/ && \
   chown -R --from=root docker /home/docker && \
   chown -R --from=root docker /usr/local/HistFitter

USER docker
ENV HOME=/home/docker

WORKDIR /usr/local/HistFitter
RUN root --version && \
    gcc --version && \
    python --version --version && \
    make --version && \
    . setup.sh && \
    cd src && \
    make -j$(($(nproc) - 1)) && \
    mkdir "${HOME}/data" && \
    printf '\nif [ -f /usr/local/HistFitter/setup.sh ];then\n    . /usr/local/HistFitter/setup.sh\nfi\n' >> "${HOME}/.profile"

WORKDIR "${HOME}/data"

ENTRYPOINT ["/bin/bash", "-l", "-c"]
CMD ["/bin/bash"]
