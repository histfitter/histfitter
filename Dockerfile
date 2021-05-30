FROM rootproject/root:6.22.00-centos7
USER root
COPY . /HistFitter
RUN chown -R nobody /HistFitter
USER nobody
RUN bash -c "cd /HistFitter && \
    . /opt/root/bin/thisroot.sh && \
    . setup.sh && cd src && make"
