# base image is debian
FROM ubuntu:latest

RUN apt-get update &&  \
	apt-get upgrade -qy && \
	apt-get dist-upgrade -qy && \
	apt-get update --fix-missing && \
	apt-get install software-properties-common -qy

RUN add-apt-repository -y ppa:ethereum/ethereum && \

    add-apt-repository -y ppa:ethereum/ethereum-dev && \
    apt-get update -y

RUN apt-get install $DEPENDENCIES -qy

# python packages
ENV PIP_PACKAGES="$PIP_PACKAGES flask ipfsapi openpyxl pyJWT pillow qrcode requests pytest web3 pysha3 flask-socketio eventlet Flask-Mail"

RUN pip3 install $PIP_PACKAGES

ENV DEPENDENCIES="python3 golang python3-pip python-virtualenv libssl-dev curl file binutils make git tmux colord zsh ethminer npm nodejs inetutils-ping solc pkg-config mongodb supervisor ethereum"

RUN apt-get install $DEPENDENCIES -qy

COPY ./utils/parity_bin /usr/local/bin/parity

#RUN bash /install_parity.sh

RUN pip3 install --upgrade pip

COPY ./utils/requirements.txt /societhy/requirements.txt

RUN pip3 install -r /societhy/requirements.txt --upgrade

RUN pip3 install -e git+https://github.com/simonvadee/ethjsonrpc#egg=ethjsonrpc

RUN pip3 install -e git+https://github.com/pricingassistant/mongokat#egg=mongokat

ENV HOME="/societhy"

WORKDIR /societhy

COPY ./utils/ /societhy/utils

RUN echo 'alias run="python3 app/app.py"' >> ~/.zshrc

RUN echo 'alias console="geth attach rpc:http://localhost:8545"' >> ~/.zshrc

EXPOSE 8080

EXPOSE 22
