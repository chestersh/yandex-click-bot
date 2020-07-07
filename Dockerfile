FROM python:3.8

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable python3-dev libpq-dev python-dev

# install chromedriver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

#RUN mkdir -p /usr/src/tor_driver/
#RUN wget -O /tmp/tor.tar.xz https://www.torproject.org/dist/torbrowser/9.5/tor-browser-linux64-9.5_en-US.tar.xz
#RUN tar -xf /tmp/tor.tar.xz -C /usr/src/tor_driver
##RUN sh -c './usr/src/tor_driver/Browser/start-tor-browser &'
#RUN /usr/src/tor_driver/Browser/start-tor-browser &

RUN rm -rf /tmp/*

#RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - ; \\nRELEASE=$(lsb_release -cs) ; \\necho "deb http://apt.postgresql.org/pub/repos/apt/ ${RELEASE}"-pgdg main | sudo tee  /etc/apt/sources.list.d/pgdg.list ; \\nsudo apt update ; \\nsudo apt -y install postgresql-11

COPY req.txt requirements.txt
RUN pip install -r ./requirements.txt


ENV APP_HOME /app
ENV PORT 5000

#set workspace
WORKDIR ${APP_HOME}

COPY . .

EXPOSE 8080 8118 9050 9051

VOLUME ["./vol_logs", "/app/vol_logs"]
CMD ["python", "src/collect.py"]
