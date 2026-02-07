#!/bin/bash
# Script to create an admin user for the Job Board Platform
# Usage: ./create_admin.sh [username] [email] [password]

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Creating admin user for Job Board Platform...${NC}"

# Check if running in Docker
if [ -f /.dockerenv ] || [ -n "$DOCKER_CONTAINER" ]; then
    echo "Running in Docker container..."
    CMD_PREFIX="docker-compose exec web"
else
    CMD_PREFIX=""
fi

# Get arguments or prompt
if [ $# -eq 3 ]; then
    # Non-interactive mode with all arguments
    $CMD_PREFIX python manage.py create_admin \
        --username "$1" \
        --email "$2" \
        --password "$3" \
        --no-input
elif [ $# -eq 0 ]; then
    # Interactive mode
    $CMD_PREFIX python manage.py create_admin
else
    echo "Usage: $0 [username] [email] [password]"
    echo "  With no arguments: Interactive mode"
    echo "  With 3 arguments: Non-interactive mode"
    exit 1
fi

echo -e "${GREEN}Admin user created successfully!${NC}"
echo -e "${YELLOW}You can now log in at: http://localhost:8000/admin/${NC}"
