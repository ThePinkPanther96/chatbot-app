FROM python:3

MAINTAINER Gal

WORKDIR /app

COPY app /app
COPY app/requirements.txt ./

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 5001

ENV ENVIRONMENT=DEV

ENTRYPOINT ["python", "magabot.py"]