from ubuntu:22.04

RUN apt-get update && \
    apt-get install -y python3 python3-pip

WORKDIR /

RUN pip3 install --upgrade pip && mkdir app

COPY ./dependencies.txt /
# WORKDIR /app

RUN pip3 install -r dependencies.txt