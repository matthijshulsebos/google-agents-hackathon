# Research Agent Tool Query Improvements

## Problem Identified

The research agent was formulating **generic, example-based queries** instead of **contextual, patient-specific queries**.

### Before (❌ Bad Behavior)
```
Iteration 1: get_patient_details("Juan de Marco")
  → Result: Age 65, scheduled for Oxycodone 5mg

Iteration 2: search_nursing_procedures("oxycodone protocol for elderly patients")
  ❌ Generic query copied from tool description example
  ❌ Doesn't use specific patient age (65)
  ❌ Doesn't reference specific medication strength (5mg)
```

### After (✅ Good Behavior)
```
Iteration 1: get_patient_details("Juan de Marco")
  → Result: Age 65, scheduled for Oxycodone 5mg

Iteration 2: search_nursing_procedures("oxycodone 5mg administration protocol for 65 year old patient")
  ✅ Includes specific patient age from previous result
  ✅ Includes specific medication and strength
  ✅ Contextual query based on learned information
```

## Root Cause

### Issue 1: Example Queries in Parameter Descriptions
The parameter descriptions contained specific examples that the LLM would copy verbatim:

**Before:**
```python
"description": "Search query for nursing procedures (e.g., 'controlled medication administration', 'oxycodone protocol for elderly patients', 'medication audit requirements')"
```

The model saw `'oxycodone protocol for elderly patients'` and used it literally, even after learning the patient's specific age was 65.

### Issue 2: Insufficient System Instruction Guidance
The system instruction didn't explicitly tell the model to formulate contextual queries based on previous tool results.

## Solutions Implemented

### Solution 1: Updated Parameter Descriptions

**Nursing Procedures Tool:**
```python
"description": "Natural language search query for nursing procedures. Formulate specific queries based on context from previous tool calls (e.g., if patient is 65 years old and scheduled for oxycodone, query 'oxycodone administration for 65 year old patient' or 'controlled medication protocol geriatric patient over 60'). Include specific patient details like age, medication names, or conditions when available."
```

**Key Changes:**
- ✅ Removed static examples that could be copied
- ✅ Added "formulate specific queries based on context from previous tool calls"
- ✅ Examples now show the *pattern* with conditional logic ("if patient is X, query Y")
- ✅ Emphasizes including "specific patient details when available"

**Pharmacy Info Tool:**
```python
"description": "Natural language search query for pharmacy information. Formulate specific queries based on medication names and requirements discovered from previous tools (e.g., if patient needs oxycodone, query 'oxycodone 5mg inventory and audit status' or 'oxycodone availability and audit date for geriatric patients'). Include specific medication details when available."
```

**Key Changes:**
- ✅ "Based on medication names and requirements discovered from previous tools"
- ✅ Examples show conditional reasoning
- ✅ Emphasizes medication-specific details

### Solution 2: Enhanced System Instruction

Added **CRITICAL** section with explicit query formulation guidance:

```
CRITICAL - When formulating search queries for tools:
- DO NOT use generic queries - always include specific context from previous tool results
- After getting patient details, incorporate patient age, medication names, and specific conditions into your search queries
- Good query example: If patient is 65 years old and scheduled for oxycodone → "oxycodone administration protocol for 65 year old patient" or "controlled medication audit requirements patient over 60 years"
- Bad query example: "oxycodone protocol for elderly patients" (too generic, lacks specific patient context)
- Good query example: If you need pharmacy info about oxycodone → "oxycodone 5mg inventory status and audit date" or "oxycodone geriatric audit compliance"
- Bad query example: "oxycodone availability" (lacks specificity about what information you need)
```

**Key Elements:**
- ✅ Explicit DO NOT instruction for generic queries
- ✅ Side-by-side good vs. bad examples
- ✅ Explains *why* bad examples are bad
- ✅ Shows how to incorporate context from previous results
- ✅ Emphasizes specificity

## Expected Behavior Now

### Scenario: "What do I need to do today with patient Juan de Marco?"

**Iteration 1:**
```
Tool: get_patient_details("Juan de Marco")
Result: {age: 65, scheduled_medications: [{medication: "Oxycodone", strength: "5mg", time: "09:00 AM"}]}
```

**Iteration 2 (Now Contextual):**
```
Tool: search_nursing_procedures("oxycodone 5mg administration protocol for 65 year old patient over 60 geriatric requirements")

Expected query variations:
✅ "oxycodone administration for 65 year old patient"
✅ "controlled medication protocol patient over 60 years oxycodone"
✅ "geriatric oxycodone 5mg administration requirements age 65"

NOT expected:
❌ "oxycodone protocol for elderly patients"
❌ "controlled medication administration"
```

**Iteration 3 (Now Contextual):**
```
Tool: search_pharmacy_info("oxycodone 5mg audit date geriatric patient compliance")

Expected query variations:
✅ "oxycodone 5mg inventory and audit status"
✅ "oxycodone audit date for patient over 60 years"
✅ "oxycodone geriatric audit compliance status"

NOT expected:
❌ "oxycodone availability"
❌ "controlled substances inventory"
```

## Testing the Improvements

### Quick Test
```bash
export GOOGLE_APPLICATION_CREDENTIALS=./sakey.json
python3 test_research_quick.py
```

**What to Look For:**
1. Check the tool call history in the output
2. Verify queries include specific patient details (age, medication name, strength)
3. Ensure queries are NOT copying examples from descriptions

### Full Demo
```bash
export GOOGLE_APPLICATION_CREDENTIALS=./sakey.json
python3 demo_research.py
```

Run Scenario 1 (Juan de Marco) and examine the tool call trace to verify contextual queries.

## Why This Matters

### Before: Generic Queries = Lower Quality Results
- Search returns generic protocols
- Less relevant information
- Misses age-specific requirements
- Requires more manual interpretation

### After: Contextual Queries = Higher Quality Results
- Search returns specific protocols for patient's age group
- More relevant, targeted information
- Identifies age-specific requirements automatically
- Direct, actionable guidance

## Benefits of This Approach

1. **Better Search Results**: Specific queries return more relevant documents
2. **Fewer Iterations**: Get the right information on first try
3. **Improved Reasoning**: Agent demonstrates understanding of context
4. **Safety**: More likely to find age-specific safety requirements
5. **Compliance**: Better at identifying audit requirements for specific patient groups

## Example Improvement in Practice

### Before (Generic Query):
```
Query: "oxycodone protocol for elderly patients"
Results: General protocol, may include ages 60-90, broad guidance
Agent: Might miss specific 6-month audit requirement for >60 years
```

### After (Contextual Query):
```
Query: "oxycodone 5mg administration protocol 65 year old patient geriatric audit"
Results: Age-specific protocol (>60 years), highlights 6-month audit requirement
Agent: Immediately identifies audit compliance issue
```

## Technical Details

### How Gemini Function Calling Works
1. Model receives function declarations with parameter descriptions
2. Model decides when to call functions and with what arguments
3. **Parameter descriptions guide argument formulation**
4. System instruction provides overall reasoning framework

### Why This Fix Works
- **Parameter descriptions** now guide the model to use context
- **System instruction** explicitly prohibits generic queries
- **Examples** show conditional reasoning patterns
- **Side-by-side comparisons** clarify good vs. bad approaches

## Files Modified

- ✅ `agents/research_agent.py`
  - Updated `search_nursing_procedures` parameter description
  - Updated `search_pharmacy_info` parameter description
  - Enhanced system instruction with CRITICAL guidance section

## Validation

Run these tests to verify improvements:

1. **Import Test**: `python3 -c "from agents.research_agent import ResearchAgent; print('OK')"`
2. **Quick Test**: `python3 test_research_quick.py` - Check tool call queries
3. **Full Demo**: `python3 demo_research.py` - Run Scenario 1, verify contextual queries
4. **API Test**: Start API and POST to `/research` endpoint

## Next Steps

Monitor actual queries in production to ensure:
- Queries consistently include patient-specific details
- Queries reference information from previous tool calls
- Search results quality improves
- Agent provides more actionable recommendations

If queries are still too generic, consider:
- Further strengthening system instruction
- Adding more explicit examples
- Implementing query validation/checking
- Adding reflection step to evaluate query quality
