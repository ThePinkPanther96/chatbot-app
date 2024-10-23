FROM python:3

LABEL maintainer="Gal"

WORKDIR /app

COPY app/ /app/
COPY app/requirements.txt /app/

RUN pip install --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt

EXPOSE 5001

ARG BUILD_NUMBER
ARG OPENAI_API_KEY

ENV ENVIRONMENT=DEV

RUN echo "${OPENAI_API_KEY}" > /app/.openai_key

ENTRYPOINT ["sh", "-c", "export OPENAI_API_KEY=$(cat /app/.openai_key) && python magabot.py"]