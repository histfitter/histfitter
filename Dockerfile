FROM atlasamglab/stats-base:root6.22.00
USER root
COPY . /HistFitter
RUN root --version
RUN gcc --version
RUN chown -R nobody /HistFitter
USER nobody
RUN bash -c "cd /HistFitter && \
    . /opt/root/bin/thisroot.sh && \
    . setup.sh && cd src && make"
