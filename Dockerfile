FROM rootproject/root-ubuntu16:6.10
USER root
COPY . /HistFitter
RUN chown -R builder /HistFitter
USER builder
RUN bash -c "cd /HistFitter && \
    . /usr/local/bin/thisroot.sh && \
    . setup.sh && cd src && make"
