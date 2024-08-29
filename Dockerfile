# FROM ubuntu:22.04.4-alpine
FROM python:3.10.12-alpine

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# RUN apt-get update
# RUN apt-get install -y python3.10
# RUN apt-get install -y python-setuptools
# RUN apt-get install -y python-pip
# RUN apt-get install -y nano
# RUN apt-get install -y telnet
# RUN apt-get install -y vim

# RUN apt-get install -y gnupg curl
# RUN curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
# gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg \
# --dearmor
# RUN echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-7.0.list
# RUN apt-get update
# RUN apt-get install -y mongodb-org
# RUN echo "mongodb-org hold" | dpkg --set-selections
# RUN echo "mongodb-org-database hold" | dpkg --set-selections
# RUN echo "mongodb-org-server hold" | dpkg --set-selections
# RUN echo "mongodb-mongosh hold" | dpkg --set-selections
# RUN echo "mongodb-org-mongos hold" | dpkg --set-selections
# RUN echo "mongodb-org-tools hold" | dpkg --set-selections
# RUN systemctl start mongod
# RUN systemctl status mongod
# python setup
RUN apk add --no-cache --update \
    python3 python3-dev gcc \
    gfortran musl-dev \
    libffi-dev openssl-dev

RUN python -m pip install --upgrade pip
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Switch to the non-privileged user to run the application.
USER appuser

# Copy the source code into the container.
COPY .env /app
COPY . .

# Run the application.
CMD python ./bot.py
