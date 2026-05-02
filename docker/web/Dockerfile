FROM --platform=$BUILDPLATFORM python:3.12-slim

# Labels and Credits
LABEL \
    name="reconPoint" \
    author="KhulnaSoft (https://github.com/KhulnaSoft) & KhulnaSoft Ltd <yogesh.ojha11@gmail.com>" \
    description="reconPoint is a automated pipeline of recon process, useful for information gathering during web application penetration testing."

# Environment Variables
ENV DEBIAN_FRONTEND="noninteractive" \
    DATABASE="postgres"
ENV USERNAME="reconpoint"
ARG HOST_UID
ARG HOST_GID

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    curl \
    openssh-client \
    fontconfig \
    fonts-freefont-ttf \
    fonts-noto \
    fonts-terminus \
    net-tools \
    htop \
    vim \
    build-essential \
    gcc \
    python3-dev \
    libpango1.0-dev \
    zlib1g-dev \
    libjpeg-dev \
    libopenjp2-7-dev \
    g++ \
    libffi-dev \
    libpq-dev \
    postgresql-client \
    pipx \
    python3-watchdog \
    && fc-cache -f \
    && fc-list | sort \
    && groupadd --gid $HOST_GID $USERNAME \
    && useradd --uid $HOST_UID --gid $HOST_GID --shell /bin/bash --create-home $USERNAME \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/local/bin/python3 /usr/local/bin/python

USER $USERNAME
WORKDIR /home/$USERNAME

ENV TOOLPATH="/home/${USERNAME}/tools"
ENV BINPATH="/home/${USERNAME}/.local/bin"
ENV PIPX_BIN_DIR="${TOOLPATH}/pipx"
ENV PATH="${PATH}:${BINPATH}:${PIPX_BIN_DIR}"

RUN mkdir -p $TOOLPATH && \
    mkdir -p $BINPATH && \
    mkdir -p /home/$USERNAME/.ssh && \
    mkdir -p /home/$USERNAME/docker

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install poetry via pipx with retry logic
RUN pipx install --verbose poetry || \
    (echo "Retrying poetry installation..." && \
     pipx install --verbose poetry)

# Copy poetry config files
COPY --chown=$USERNAME:$USERNAME ./pyproject.toml /home/$USERNAME/pyproject.toml

# Install reconPoint dependencies with enhanced retry logic
RUN for i in 1 2 3; do \
        echo "Attempt $i: Installing dependencies..." && \
        poetry install --without dev --verbose && break || \
        (echo "Attempt $i failed, clearing cache and retrying..." && \
         poetry cache clear --all pypi && \
         if [ $i -eq 3 ]; then echo "All attempts failed"; exit 1; fi); \
    done

# Ensure poetry environment is properly activated in PATH
ENV PATH="/home/reconpoint/.cache/pypoetry/virtualenvs/reconpoint-zFb_Et9c-py3.12/bin:/home/reconpoint/.local/bin:$PATH"

EXPOSE 8000
RUN mkdir -p /home/$USERNAME/reconpoint
VOLUME /home/$USERNAME/reconpoint
WORKDIR /home/$USERNAME/reconpoint
ENTRYPOINT ["/entrypoint.sh"]
