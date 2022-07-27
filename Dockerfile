FROM python:3.10.5-slim-buster

RUN apt-get update \
  && apt-get -yy install gpg

RUN adduser rootless
USER rootless

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY ./requirements /requirements
RUN pip install -r /requirements/dev.txt
