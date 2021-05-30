FROM rootproject/root:6.22.00-centos7
USER root
COPY . /HistFitter
RUN which root
RUN root --version
RUN chown -R nobody /HistFitter
USER nobody
RUN bash -c "cd /HistFitter && \
    . setup.sh && cd src && make"
