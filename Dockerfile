FROM rootproject/root:6.22.00-centos7
USER root
COPY . /HistFitter
RUN bash -c "rootpath=`find / -name thisroot.sh`&& cd /HistFitter && \
    . $rootpath && \
    . setup.sh && cd src && make"
