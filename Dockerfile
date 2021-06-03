FROM atlasamglab/stats-base:root6.22.00
USER root
COPY . /HistFitter
RUN root --version
RUN gcc --version
RUN chown -R nobody /HistFitter
USER nobody
RUN bash -c "cd /HistFitter && \
    . setup.sh && cd src && make && cd ../"
RUN bash -c "sudo apt-get update && sudo apt-get -y install curl"
