#!/bin/bash

# Helper script for Docker development with Poetry

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Edu-Fi Development Environment${NC}"

case $1 in
    build)
        echo -e "${GREEN}Building Docker containers with Poetry...${NC}"
        docker-compose build --no-cache
        ;;
    up)
        echo -e "${GREEN}Starting development environment...${NC}"
        docker-compose up
        ;;
    down)
        echo -e "${GREEN}Stopping development environment...${NC}"
        docker-compose down
        ;;
    recreate)
        echo -e "${GREEN}Recreating containers...${NC}"
        docker-compose down
        docker-compose up --build
        ;;
    migrate)
        echo -e "${GREEN}Running database migrations...${NC}"
        docker-compose exec backend python manage.py db migrate -m "$2" -a
        ;;
    upgrade)
        echo -e "${GREEN}Applying migrations...${NC}"
        docker-compose exec backend python manage.py db upgrade
        ;;
    test)
        echo -e "${GREEN}Running tests...${NC}"
        docker-compose exec backend pytest "$2"
        ;;
    shell)
        echo -e "${GREEN}Opening shell in backend container...${NC}"
        docker-compose exec backend bash
        ;;
    logs)
        echo -e "${GREEN}Showing logs...${NC}"
        docker-compose logs -f backend
        ;;
    *)
        echo -e "${YELLOW}Edu-Fi Development Commands:${NC}"
        echo -e "  ${GREEN}build${NC}     - Build containers (--no-cache)"
        echo -e "  ${GREEN}up${NC}        - Start development environment"
        echo -e "  ${GREEN}down${NC}      - Stop development environment"
        echo -e "  ${GREEN}recreate${NC}  - Recreate and start containers"
        echo -e "  ${GREEN}migrate${NC}   - Generate migration (requires message)"
        echo -e "  ${GREEN}upgrade${NC}   - Apply migrations"
        echo -e "  ${GREEN}test${NC}      - Run tests (optional path)"
        echo -e "  ${GREEN}shell${NC}     - Open bash shell in backend container"
        echo -e "  ${GREEN}logs${NC}      - Show backend logs"
        ;;
esac