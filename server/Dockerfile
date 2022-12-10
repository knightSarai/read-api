# FROM python:3.9-alpine
#
# ENV PYTHONUNBUFFERED=1
#
# RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
#
# COPY requirements.txt /tmp/requirements.txt
# RUN pip install --no-cache-dir -r /tmp/requirements.txt \
#     && rm -rf /tmp/requirements.txt \
#     && useradd -U app_user \
#     && install -d -m 0755 -o app_user -g app_user /app/static
#
#
# WORKDIR /app
#
# USER app_user:app_user
# COPY --chown=app_user:app_user . .
#
#
# RUN chmod +x entrypoint.sh
#
# ENTRYPOINT ["entrypoint.sh"]
#


FROM python:3.9-slim

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential libpq-dev \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm -rf /tmp/requirements.txt \
    && useradd -U app_user \
    && install -d -m 0755 -o app_user -g app_user /app/static

WORKDIR /app
USER app_user:app_user
COPY --chown=app_user:app_user . .
RUN chmod +x *.sh

ENTRYPOINT [ "./entrypoint.sh" ]
