# base image is debian
FROM ubuntu:latest

RUN apt-get update &&  \
	apt-get upgrade -qy && \
	apt-get dist-upgrade -qy && \
	apt-get install software-properties-common -qy

# set container dependencies as environment variable:
# DEPENDENCIES are to be installed with apt-get
# PIP_PACKAGES are to be installed with pip3 (python packages)

# languages
ENV DEPENDENCIES="python3 golang python3-pip python-virtualenv libssl-dev curl"

# libraries and services
ENV DEPENDENCIES="$DEPENDENCIES mongodb supervisor"

# ethereum
ENV DEPENDENCIES="$DEPENDENCIES ethereum "

ENV HOME="/societhy"

RUN add-apt-repository -y ppa:ethereum/ethereum && \
	add-apt-repository -y ppa:ethereum/ethereum-dev && \
	apt-get update -y

RUN apt-get install $DEPENDENCIES -qy

# parity dependencie
RUN curl https://raw.githubusercontent.com/ethcore/scripts/master/install-deps.sh -L | bash

RUN cp parity/target/release/parity /usr/local/bin

# python packages
ENV PIP_PACKAGES="$PIP_PACKAGES flask ipfsapi mongokat openpyxl ethjsonrpc pyJWT"

RUN pip3 install $PIP_PACKAGES

RUN pip3 install ethereum --upgrade

RUN apt-get autoremove -qy --purge

RUN echo 'alias run="python3 app/app.py"' >> ~/.bashrc

ENV IP="172.17.0.2"

ENV MONGOIP="163.5.84.117"

COPY ./utils /societhy/utils

# add code files and setup work directory
WORKDIR /societhy

RUN cd /societhy/utils ; ./install.sh
