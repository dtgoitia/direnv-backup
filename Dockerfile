FROM python:3.10.5-slim-buster

RUN apt-get update \
  && apt-get -yy install gpg

ENV USER=rootless

RUN adduser $USER
USER $USER

ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Dev dependencies are not required, because this script must have zero dependencies
# COPY ./requirements /requirements
# RUN pip install -r /requirements/dev.txt
