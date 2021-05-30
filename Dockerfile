FROM rootproject/root:6.22.00-centos7
USER root
COPY . /HistFitter
RUN chown -R builder /HistFitter
USER builder
RUN bash -c "cd /HistFitter && \
    . /usr/local/bin/thisroot.sh && \
    . setup.sh && cd src && make"
