# Testing the Hospital Multi-Agent RAG System

## Quick Start

The system is now using a **RAG (Retrieval Augmented Generation)** approach with Vertex AI Search. Here's how to test it:

## Option 1: Interactive Test Script (Recommended)

```bash
export GOOGLE_APPLICATION_CREDENTIALS=./sakey.json
python3 test_rag.py
```

This gives you a menu with options:
1. **Test Nursing Queries** - Run automated tests for nursing protocols
2. **Test Multilingual Support** - Test English and Spanish queries
3. **Interactive Mode** - Ask your own questions
4. **Quick Single Test** - Fast test of blood glucose monitoring

## Option 2: Direct Python Test

```bash
export GOOGLE_APPLICATION_CREDENTIALS=./sakey.json
python3 << 'EOF'
from orchestrator import HospitalOrchestrator

# Initialize
orch = HospitalOrchestrator()

# Test query
result = orch.process_query("What about blood glucose monitoring?")

# Print result
if not result.get('error'):
    print(f"\n✅ Success!")
    print(f"📊 Found {result.get('total_results')} results")
    print(f"\nAnswer:\n{result['answer']}")
else:
    print(f"❌ Error: {result['message']}")
EOF
```

## Option 3: Original Demo Script

The original demo still works but only the nursing agent uses the new RAG system:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=./sakey.json
python3 demo.py
```

When prompted, choose:
- `n` to skip interactive mode initially
- Then `y` to enter interactive mode and test queries

## Test Queries to Try

### Nursing (English)
- "What about blood glucose monitoring?"
- "How do I insert an IV line?"
- "What are the steps for wound dressing?"
- "Tell me about vital signs monitoring"
- "What equipment is needed for IV insertion?"

### Nursing (Spanish)
- "¿Cuál es el protocolo para curar heridas?"
- "¿Cómo inserto una vía intravenosa?"
- "¿Qué pasos debo seguir para la curación?"

### Expected Results

You should see:
- ✅ **Agent**: nursing
- ✅ **Total Results**: 20-50+ (varies by query)
- ✅ **Sources Used**: 3-5 documents
- ✅ **Answer**: Detailed response with:
  - Overview
  - Equipment Needed
  - Procedure Steps (numbered)
  - Safety Considerations
  - Documentation requirements
  - References

## Verify It's Working

The system is working correctly if you see:

1. **Log messages** showing:
   ```
   RAG Pipeline initialized with search engine: poc-medical-csv-data_1761595774470
   Searching for: [your query]...
   Generating response with 5 search results...
   ```

2. **Result includes**:
   - `total_results` > 0
   - `grounding_metadata` with 3-5 sources
   - Detailed `answer` with structured information

3. **Answer contains** specific information from your Vertex AI Search datastore, not generic medical knowledge

## Troubleshooting

### No results found
- Check that your Vertex AI Search engine has documents uploaded
- Verify the engine ID: `poc-medical-csv-data_1761595774470`

### Permission errors
- Ensure `GOOGLE_APPLICATION_CREDENTIALS` is set
- Check that your service account has:
  - Discovery Engine API access
  - Vertex AI API access

### Generic answers (not from your docs)
- If answers don't reference specific procedures/protocols, the RAG may not be retrieving results
- Check logs for "Searching for:" and "Generating response with X search results"
- If search results = 0, your datastore may be empty or the engine ID is wrong

## Next Steps

Once nursing agent tests pass, you can update HR and Pharmacy agents to use the same RAG approach!
