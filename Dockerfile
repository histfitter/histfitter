FROM rootproject/root:6.22.00-arch
USER root
COPY . /HistFitter
RUN root --version
RUN gcc --version
RUN chown -R nobody /HistFitter
USER nobody
RUN bash -c "cd /HistFitter && \
    . /usr/bin/thisroot.sh && \
    . setup.sh && cd src && make"
