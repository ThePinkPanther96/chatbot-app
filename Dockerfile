FROM python:3.12.5

MAINTAINER Gal

WORKDIR /app

COPY app /app

COPY app/requirements.txt ./

RUN pip install --upgrade pip

RUN echo ${BUILD_NUMBER} && pip install --no-cache-dir -r requirements.txt

EXPOSE 5001

ARG BUILD_NUMBER
#ARG OPENAI_API_KEY

ENV ENVIRONMENT=DEV
ENV OPENAI_API_KEY=

#ENV OPENAI_API_KEY=${OPENAI_API_KEY}

ENTRYPOINT ["python", "magabot.py"]