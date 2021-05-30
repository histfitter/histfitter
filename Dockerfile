FROM rootproject/root:6.22.00-ubuntu20.04
USER root
COPY . /HistFitter
RUN cat /etc/passwd
RUN find / -name thisroot.sh
RUN chown -R builder /HistFitter
USER builder
RUN bash -c "cd /HistFitter && \
    . /usr/local/bin/thisroot.sh && \
    . setup.sh && cd src && make"
