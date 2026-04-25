FROM python:3.14-slim AS base

ARG APP_USER=template
ARG APP_UID=1000
ARG APP_GID=1000

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    passwd \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . /app

# Create non-root user and set ownership for /app. Use || true to be resilient
# if the user/group already exist in some build environments.
RUN groupadd -g ${APP_GID} ${APP_USER} || true \
    && useradd -m -u ${APP_UID} -g ${APP_GID} -s /bin/bash ${APP_USER} || true \
    && chown -R ${APP_USER}:${APP_USER} /app

# Run containers as non-root user by default
USER ${APP_USER}

ENV PATH="/home/${APP_USER}/.local/bin:${PATH}"

CMD ["uvicorn", "--factory", "src.app.factory:create_app", "--host", "0.0.0.0", "--port", "8000"]
