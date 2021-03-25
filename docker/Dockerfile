FROM python:3.9.2-alpine
LABEL maintainer="Dash Developers <dev@dash.org>"
LABEL description="Dockerised Sentinel"

RUN apt-get update && \
    apt-get install git curl -y --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN git clone https://github.com/dashpay/sentinel.git --single-branch --branch master /sentinel && \
    cd /sentinel && \
    rm sentinel.conf && \
    rm -rf .git && \
    pip install -r requirements.txt && exit 0

ENV HOME /sentinel
WORKDIR /sentinel

ADD run.sh /

CMD /run.sh
