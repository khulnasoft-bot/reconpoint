include .env
.DEFAULT_GOAL:=help

# Credits: https://github.com/sherifabdlnaby/elastdocker/

# This for future release of Compose that will use Docker Buildkit, which is much efficient.
COMPOSE_PREFIX_CMD := COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1

COMPOSE_ALL_FILES := -f docker-compose.yml
SERVICES          := db web proxy redis celery celery-beat ollama

# Check if 'docker compose' command is available, otherwise use 'docker-compose'
DOCKER_COMPOSE := $(shell if command -v docker > /dev/null && docker compose version > /dev/null 2>&1; then echo "docker compose"; else echo "docker-compose"; fi)
$(info Using: $(shell echo "$(DOCKER_COMPOSE)"))

# --------------------------

.PHONY: setup certs up build username pull down stop restart rm logs

certs:		    ## Generate certificates.
	@${COMPOSE_PREFIX_CMD} ${DOCKER_COMPOSE} -f docker-compose.setup.yml run --rm certs

setup:			## Generate certificates.
	@make certs

setup_devcontainer:		## Set up devcontainer environment.
	@docker build -f .devcontainer/Dockerfile -t reconpoint-dev .

up:				## Build and start all services.
	${COMPOSE_PREFIX_CMD} ${DOCKER_COMPOSE} ${COMPOSE_ALL_FILES} up -d --build ${SERVICES}

build:			## Build all services.
	@echo "Setting up buildx for multi-platform support..."
	@docker buildx create --use --name reconpoint-builder 2>/dev/null || docker buildx use reconpoint-builder
	${COMPOSE_PREFIX_CMD} ${DOCKER_COMPOSE} ${COMPOSE_ALL_FILES} build --parallel ${SERVICES}

build-multiplatform:	## Build all services for multiple platforms (amd64, arm64) and push to registry.
	@echo "Building multi-platform images with remote caching..."
	@docker buildx create --use --name multiplatform-builder 2>/dev/null || docker buildx use multiplatform-builder
	@docker buildx build --platform linux/amd64,linux/arm64 \
		-t khulnasoft/reconpoint:latest \
		--cache-from type=registry,ref=khulnasoft/reconpoint:buildcache \
		--cache-to type=registry,ref=khulnasoft/reconpoint:buildcache,mode=max \
		--push ./web
	@echo "Multi-platform build complete. Images and cache pushed to registry."

username:		## Generate Username (Use only after make up).
ifeq ($(isNonInteractive), true)
	${COMPOSE_PREFIX_CMD} ${DOCKER_COMPOSE} ${COMPOSE_ALL_FILES} exec web python3 manage.py createsuperuser --username ${DJANGO_SUPERUSER_USERNAME} --email ${DJANGO_SUPERUSER_EMAIL} --noinput
else
	${COMPOSE_PREFIX_CMD} ${DOCKER_COMPOSE} ${COMPOSE_ALL_FILES} exec web python3 manage.py createsuperuser
endif

changepassword:	## Change password for user
	${COMPOSE_PREFIX_CMD} ${DOCKER_COMPOSE} ${COMPOSE_ALL_FILES} exec web python3 manage.py changepassword

migrate:		## Apply migrations
	${COMPOSE_PREFIX_CMD} ${DOCKER_COMPOSE} ${COMPOSE_ALL_FILES} exec web python3 manage.py migrate

pull:			## Pull Docker images.
	docker login docker.pkg.github.com
	${COMPOSE_PREFIX_CMD} ${DOCKER_COMPOSE} ${COMPOSE_ALL_FILES} pull

down:			## Down all services.
	${COMPOSE_PREFIX_CMD} ${DOCKER_COMPOSE} ${COMPOSE_ALL_FILES} down

stop:			## Stop all services.
	${COMPOSE_PREFIX_CMD} ${DOCKER_COMPOSE} ${COMPOSE_ALL_FILES} stop ${SERVICES}

restart:		## Restart all services.
	${COMPOSE_PREFIX_CMD} ${DOCKER_COMPOSE} ${COMPOSE_ALL_FILES} restart ${SERVICES}

rm:				## Remove all services containers.
	${COMPOSE_PREFIX_CMD} ${DOCKER_COMPOSE} $(COMPOSE_ALL_FILES) rm -f ${SERVICES}

test:
	${COMPOSE_PREFIX_CMD} ${DOCKER_COMPOSE} $(COMPOSE_ALL_FILES) exec celery python3 -m unittest tests/test_scan.py

lint:			## Run linting checks (flake8).
	${COMPOSE_PREFIX_CMD} ${DOCKER_COMPOSE} $(COMPOSE_ALL_FILES) exec web flake8 .

format:			## Format code with black and isort.
	${COMPOSE_PREFIX_CMD} ${DOCKER_COMPOSE} $(COMPOSE_ALL_FILES) exec web black .
	${COMPOSE_PREFIX_CMD} ${DOCKER_COMPOSE} $(COMPOSE_ALL_FILES) exec web isort .

type-check:		## Run mypy type checking.
	${COMPOSE_PREFIX_CMD} ${DOCKER_COMPOSE} $(COMPOSE_ALL_FILES) exec web mypy .

logs:			## Tail all logs with -n 1000.
	${COMPOSE_PREFIX_CMD} ${DOCKER_COMPOSE} $(COMPOSE_ALL_FILES) logs --follow --tail=1000 ${SERVICES}

images:			## Show all Docker images.
	${COMPOSE_PREFIX_CMD} ${DOCKER_COMPOSE} $(COMPOSE_ALL_FILES) images ${SERVICES}

prune:			## Remove containers and delete volume data.
	@make stop && make rm && docker volume prune -f

help:			## Show this help.
	@echo "Make application Docker images and manage containers using Docker Compose files."
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m (default: help)\n\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
