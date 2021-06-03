FROM atlasamglab/stats-base:root6.22.00
USER root
RUN bash -c "apt-get update && apt-get -y install curl"
COPY . /HistFitter
RUN root --version
RUN gcc --version
RUN chown -R nobody /HistFitter
USER nobody
RUN bash -c "cd /HistFitter && \
    . setup.sh && cd src && make && cd ../"

