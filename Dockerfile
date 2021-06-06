FROM atlasamglab/stats-base:root6.22.08-python2.7
USER root
RUN bash -c "source /usr/local/bin/thisroot.sh"
COPY . /HistFitter
RUN root --version
RUN gcc --version
RUN python --version
RUN make --version
RUN chown -R nobody /HistFitter
USER nobody
RUN bash -c "cd /HistFitter && \
    . setup.sh && cd src && make && cd ../"

