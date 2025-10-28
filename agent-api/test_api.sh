#!/bin/bash
# Test script for the HTTP API

export GOOGLE_APPLICATION_CREDENTIALS=./sakey.json

echo "Starting API server in background..."
python3 api.py &
API_PID=$!

# Wait for server to start
echo "Waiting for API to start..."
sleep 5

# Test endpoints
echo ""
echo "=== Testing API Endpoints ==="
echo ""

echo "1. Root endpoint:"
curl -s http://localhost:8000/ | python3 -m json.tool
echo ""

echo "2. Health check:"
curl -s http://localhost:8000/health | python3 -m json.tool
echo ""

echo "3. Agent info:"
curl -s http://localhost:8000/agents | python3 -m json.tool
echo ""

echo "4. Query test (Nursing - English):"
curl -s -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What about blood glucose monitoring?", "user_role": "nurse"}' | python3 -m json.tool
echo ""

# Kill the server
echo "Stopping API server..."
kill $API_PID

echo "Test complete!"
