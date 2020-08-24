FROM python:3.8

#ENV LANGUAGE en_US.UTF-8
#ENV LANG en_US.UTF-8
#ENV LC_ALL en_US.UTF-8
#ENV LC_CTYPE en_US.UTF-8
#ENV LC_MESSAGES en_US.UTF-8

COPY req.txt requirements.txt
RUN set -ex \
    && buildDeps=' \
        freetds-dev \
        libkrb5-dev \
        libsasl2-dev \
        libssl-dev \
        libffi-dev \
        libpq-dev \
        git \
    ' \
#    && sed -i 's/^# en_US.UTF-8 UTF-8$/en_US.UTF-8 UTF-8/g' /etc/locale.gen \
#    && locale-gen \
#    && update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 \
    && apt-get update -yqq \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get -y update \
    && apt-get install -yqq --no-install-recommends \
        $buildDeps \
        google-chrome-stable \
        python3-dev \
        python-dev \
        unzip \
        python-psycopg2 \
    && wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/ \
    && pip install -r ./requirements.txt \
    && rm -rf /tmp/* \
    && apt-get purge --auto-remove -yqq $buildDeps \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf \
        /var/lib/apt/lists/* \
        /tmp/* \
        /var/tmp/* \
        /usr/share/man \
        /usr/share/doc \
        /usr/share/doc-base

#COPY req.txt requirements.txt
#RUN pip install -r ./requirements.txt


ENV APP_HOME /app
ENV PORT 5000

WORKDIR ${APP_HOME}

COPY . ${APP_HOME}
RUN apt-get update && apt-get install -y tree
RUN sh -c tree
RUN sh -c pwd


# -v /home/arty/python/clckbotx/src/logs:/app/src/logs/
#VOLUME ["/dev/shm", "/dev/shm"]
#VOLUME ["/home/arty/python/clckbotx/src/logs", "/app/src/logs/"]
CMD ["python", "src/collect.py"]







#RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
#RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
#RUN apt-get -y update
#RUN apt-get install -y google-chrome-stable python3-dev libpq-dev python-dev
#RUN apt-get install -y tor
#RUN echo "Log notice stdout" >> /etc/torrc
#RUN echo "SocksPort 0.0.0.0:9150" >> /etc/torrc
#RUN echo "CircuitBuildTimeout 10" >> /etc/torrc
#RUN echo "LearnCircuitBuildTimeout 0" >> /etc/torrc
#RUN echo "MaxCircuitDirtiness 1" >> /etc/torrc
#EXPOSE 9150



# install chromedriver
#RUN apt-get install -yqq unzip
#RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
#RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/


#RUN mkdir -p /usr/src/tor_driver/
#RUN wget -O /tmp/tor.tar.xz https://www.torproject.org/dist/torbrowser/9.5/tor-browser-linux64-9.5_en-US.tar.xz
#RUN tar -xf /tmp/tor.tar.xz -C /usr/src/tor_driver
##RUN sh -c './usr/src/tor_driver/Browser/start-tor-browser &'
#RUN /usr/src/tor_driver/Browser/start-tor-browser &

#RUN rm -rf /tmp/*

#RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - ; \\nRELEASE=$(lsb_release -cs) ; \\necho "deb http://apt.postgresql.org/pub/repos/apt/ ${RELEASE}"-pgdg main | sudo tee  /etc/apt/sources.list.d/pgdg.list ; \\nsudo apt update ; \\nsudo apt -y install postgresql-11
#
#COPY req.txt requirements.txt
#RUN pip install -r ./requirements.txt
#
#
#ENV APP_HOME /app
#ENV PORT 5000
#
##set workspace
#WORKDIR ${APP_HOME}
#
#COPY . .
##VOLUME ["/vol_logs", "/app/vol_logs"]
#VOLUME ["/dev/shm", "/dev/shm"]
#VOLUME ["./service/logs/", "./logs/"]
#
#
##CMD tor -f /etc/torrc &
##RUN tor -f /etc/torrc &
##ENTRYPOINT
#CMD ["python", "src/collect.py"]
