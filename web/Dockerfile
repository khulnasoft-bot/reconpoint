# syntax=docker/dockerfile:1

# --- Go Builder Stage ---
FROM --platform=$BUILDPLATFORM golang:1.21-bullseye AS go-builder

ARG TARGETARCH
ENV GOOS=linux
ENV GOARCH=$TARGETARCH
ENV CGO_ENABLED=0

WORKDIR /app

# Install Go tools
RUN printf "\
    github.com/jaeles-project/gospider@latest\n\
    github.com/tomnomnom/gf@latest\n\
    github.com/tomnomnom/unfurl@latest\n\
    github.com/tomnomnom/waybackurls@latest\n\
    github.com/projectdiscovery/httpx/cmd/httpx@latest\n\
    github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest\n\
    github.com/projectdiscovery/chaos-client/cmd/chaos@latest\n\
    github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest\n\
    github.com/projectdiscovery/naabu/v2/cmd/naabu@latest\n\
    github.com/hakluke/hakrawler@latest\n\
    github.com/lc/gau/v2/cmd/gau@latest\n\
    github.com/owasp-amass/amass/v3/...@latest\n\
    github.com/ffuf/ffuf@latest\n\
    github.com/projectdiscovery/tlsx/cmd/tlsx@latest\n\
    github.com/hahwul/dalfox/v2@latest\n\
    github.com/projectdiscovery/katana/cmd/katana@latest\n\
    github.com/dwisiswant0/crlfuzz/cmd/crlfuzz@latest\n\
    github.com/sa7mon/s3scanner@latest\n" | \
    xargs -L1 -I {} sh -c 'go install -ldflags="-s -w" {}'

# --- Final Stage ---
FROM ubuntu:22.04 AS final

ARG TARGETARCH
ARG GECKOVERSION=0.33.0
ENV DEBIAN_FRONTEND="noninteractive"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="${PATH}:/root/.cargo/bin"

WORKDIR /usr/src/app

# Install system dependencies
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
        python3.10 python3-dev python3-pip \
        build-essential cmake geoip-bin geoip-database \
        gcc git libpq-dev libpango-1.0-0 libpangoft2-1.0-0 \
        libpcap-dev netcat-traditional nmap x11-utils xvfb wget curl \
        python3-netaddr software-properties-common \
        gpg-agent \
    && add-apt-repository -y ppa:mozillateam/ppa \
    && apt-get update

# Install Gecko Driver (Arch-aware)
RUN ARCH=$(dpkg --print-architecture) \
    && if [ "${ARCH}" = "arm64" ] || [ "${ARCH}" = "aarch64" ]; then \
      GECKOPATH="geckodriver-v${GECKOVERSION}-linux-aarch64.tar.gz"; \
    else \
      GECKOPATH="geckodriver-v${GECKOVERSION}-linux64.tar.gz"; \
    fi \
    && wget -q https://github.com/mozilla/geckodriver/releases/download/v${GECKOVERSION}/${GECKOPATH} \
    && tar -xzf ${GECKOPATH} -C /usr/bin \
    && rm ${GECKOPATH}

# Install Rust (required for some python packages)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy Go binaries from builder
COPY --from=go-builder /go/bin/ /usr/local/bin/

# Update tools that have auto-update features
RUN nuclei -update-templates && chaos -update || true

# Install Python dependencies
COPY ./requirements.txt /tmp/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install --upgrade setuptools==72.1.0 && \
    pip3 install -r /tmp/requirements.txt && \
    pip3 install eyewitness fuzzywuzzy selenium==4.9.1 python-Levenshtein pyvirtualdisplay netaddr

# Copy source code
COPY . .

LABEL \
    name="reconPoint" \
    author="KhulnaSoft Ltd <security@khulnasoft.com>" \
    description="reconPoint is a automated pipeline of recon process."
