# Jupyterlab

Jupyterlab is a Docker container with custom kernel installation and python library addition.

## Installation

```bash
git clone https://github.com/umaraziz10/jupyterlab-guriang
```

```bash
mv jupyterlab-guriang/ jupyterlab/
cd jupyterlab/
docker build -t {image_name}:{tag} .
```

## Usage
This container need to run by docker-compose. Makesure to build the container and register to registry.
