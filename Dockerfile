FROM rootproject/root:6.22.00-ubuntu20.04
USER root
COPY . /HistFitter
RUN bash -c "cd /HistFitter && \
    . /usr/local/bin/thisroot.sh && \
    . setup.sh && cd src && make"
