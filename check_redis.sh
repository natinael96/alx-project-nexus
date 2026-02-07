#!/bin/bash
# Script to check if Redis is working

echo "=== Redis Connection Test ==="

# Check if Redis container is running
echo "1. Checking if Redis container is running..."
if docker ps | grep -q jobboard_redis; then
    echo "   ✓ Redis container is running"
else
    echo "   ✗ Redis container is not running"
    exit 1
fi

# Test Redis connection from host
echo ""
echo "2. Testing Redis connection from host..."
if command -v redis-cli &> /dev/null; then
    if redis-cli -h localhost -p 6379 ping 2>/dev/null | grep -q PONG; then
        echo "   ✓ Redis is responding to PING"
    else
        echo "   ✗ Redis is not responding"
    fi
else
    echo "   ⚠ redis-cli not installed locally (this is OK)"
fi

# Test Redis connection from web container
echo ""
echo "3. Testing Redis connection from web container..."
if docker exec jobboard_web python -c "import redis; r = redis.Redis(host='redis', port=6379, db=0); print('✓ Redis connection successful' if r.ping() else '✗ Redis connection failed')" 2>/dev/null; then
    echo "   ✓ Redis connection from Django container works"
else
    echo "   ✗ Redis connection from Django container failed"
    echo "   Note: Make sure the web container is running"
fi

# Check Redis info
echo ""
echo "4. Redis Information:"
if docker exec jobboard_redis redis-cli INFO server 2>/dev/null | head -5; then
    echo "   ✓ Redis info retrieved successfully"
else
    echo "   ✗ Could not retrieve Redis info"
fi

echo ""
echo "=== Test Complete ==="
