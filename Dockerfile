FROM python:3

MAINTAINER Gal

WORKDIR /app

COPY app/ /app/

COPY app/requirements.txt /app/

RUN pip install --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt

EXPOSE 5001

ARG BUILD_NUMBER
ARG OPENAI_API_KEY

ENV ENVIRONMENT=DEV
ENV OPENAI_API_KEY=${OPENAI_API_KEY}

ENTRYPOINT ["python", "magabot.py"]