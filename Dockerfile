FROM rootproject/root-ubuntu16
COPY --chown=builder . /HistFitter
RUN bash -c "cd /HistFitter && \
    . /usr/local/bin/thisroot.sh && \
    . setup.sh && cd src && make"
