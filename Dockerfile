FROM ubuntu:20.04

RUN apt-get -y update
RUN apt-get install -y sudo git python3.8 python3-pip python3-dev
RUN python3 -m pip install slacker pytz pyupbit
RUN adduser --disabled-password --gecos "" ubuntu && echo 'ubuntu:ubuntu' | \
    chpasswd && adduser ubuntu sudo && echo 'ubuntu ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER ubuntu
WORKDIR /home/ubuntu

COPY ./eth_trading_bot.py /home/ubuntu/eth_trading_bot.py
COPY ./logger.py /home/ubuntu/logger.py
