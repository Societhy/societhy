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
ENV DEPENDENCIES="python3 golang python3-pip python-virtualenv libssl-dev curl file binutils make git tmux colord zsh ethminer npm nodejs inetutils-ping"

# libraries and services
ENV DEPENDENCIES="$DEPENDENCIES mongodb supervisor"

# ethereum
ENV DEPENDENCIES="$DEPENDENCIES ethereum "

ENV HOME="/societhy"

RUN add-apt-repository -y ppa:ethereum/ethereum && \
	add-apt-repository -y ppa:ethereum/ethereum-dev && \
	apt-get update -y

RUN apt-get install $DEPENDENCIES -qy

# INSTALL PARITY

WORKDIR /societhy

COPY ./utils /societhy/utils

RUN bash /societhy/utils/install_parity.sh

# python packages
ENV PIP_PACKAGES="$PIP_PACKAGES flask ipfsapi openpyxl pyJWT pillow qrcode requests"

RUN pip3 install $PIP_PACKAGES

RUN pip3 install ethereum --upgrade

# INSTALL our own ethjsonrpc module

RUN git clone https://github.com/simonvadee/ethjsonrpc.git && \
        cd ethjsonrpc && \
        git pull && \
        python3 setup.py install && \
        cp -r ethjsonrpc /usr/local/lib/python3.5/dist-packages/ethjsonrpc

RUN git clone https://github.com/pricingassistant/mongokat.git && \
    cd mongokat && \
    git pull && \
    python3 setup.py install && \
    cp -r mongokat /usr/local/lib/python3.5/dist-packages/mongokat

RUN apt-get autoremove -qy --purge

ENV IP="172.17.0.2"

ENV MONGOIP="163.5.84.117"

ENV ETHIP="127.0.0.1"

ENV ETHPORT=8545

ENV KEYS_DIRECTORY="/societhy/.parity/keys"

ENV TERM=xterm-256color

RUN echo 'alias run="python3 app/app.py"' >> ~/.zshrc

RUN echo 'alias console="geth attach rpc:http://localhost:8545"' >> ~/.zshrc

RUN mkdir /societhy/.parity && mkdir /societhy/.parity/keys

# add test key to key directory

COPY ./utils/test_key.key $KEYS_DIRECTORY

EXPOSE 8080

EXPOSE 22

EXPOSE 80

RUN cd /societhy/utils ; ./install.sh
