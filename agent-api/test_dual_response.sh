#!/bin/bash
# Test dual response feature via API

export GOOGLE_APPLICATION_CREDENTIALS=./sakey.json

echo "Starting API server in background..."
python3 api.py &
API_PID=$!

# Wait for server to start
echo "Waiting for API to start..."
sleep 5

echo ""
echo "=== Testing Dual Response Feature ==="
echo ""

# Test query
echo "Query: What about blood glucose monitoring?"
echo ""

RESPONSE=$(curl -s -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What about blood glucose monitoring?", "user_role": "nurse"}')

echo "Summary:"
echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('answer_summary', 'N/A'))"
echo ""

echo "Detailed (first 200 chars):"
echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('answer_detailed', 'N/A')[:200] + '...')"
echo ""

echo "Fields in response:"
echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print('\\n'.join([f'- {k}' for k in data.keys()]))"

# Kill the server
echo ""
echo "Stopping API server..."
kill $API_PID

echo "Test complete!"
