#!/bin/bash
# Install dependencies
apt-get update
apt-get install -y python3-pip docker.io

# Install docker-compose
pip3 install docker-compose

# Clone repo
git clone https://github.com/erickweyunga/edu-fi
cd edu-fi

# Start the services
docker-compose -f backend/docker-compose.yml up -d