# Research Agent Implementation Guide

## Overview

The Research Agent is an agentic AI system that uses **ReAct-style reasoning** (Reason → Act → Observe) with **Gemini function calling** to perform multi-step research across hospital systems.

## Architecture

```
User Query
    ↓
Research Agent (ResearchAgent)
    ↓
Gemini 2.5 Flash (Function Calling)
    ↓
Tools (up to 10 iterations):
    ├─ get_patient_details()
    ├─ search_nursing_procedures()
    └─ search_pharmacy_info()
    ↓
Synthesized Answer
```

## Key Components

### 1. ResearchAgent Class
**File**: `agents/research_agent.py`

- **Purpose**: Orchestrate multi-step research using tool calling
- **Model**: Gemini 2.5 Flash with automatic function calling
- **Max Iterations**: 10 (configurable)
- **Temperature**: 0.1 (focused reasoning)

**Core Method**:
```python
research_agent.research(query: str) -> Dict[str, Any]
```

**Returns**:
- `answer`: Final synthesized answer
- `iterations`: Number of reasoning loops
- `tool_calls`: Total tool executions
- `tool_call_history`: Detailed trace of all tool calls

### 2. Available Tools

#### Tool 1: `get_patient_details(patient_name: str)`
- **Purpose**: Retrieve patient information
- **Returns**: Age, scheduled medications, medical history, allergies
- **Implementation**: Hardcoded patient database (demo)
- **Patients**:
  - Juan de Marco (65 years, scheduled for Oxycodone)
  - Maria Silva (45 years, scheduled for Ibuprofen)
  - Robert Johnson (72 years, scheduled for Morphine)

#### Tool 2: `search_nursing_procedures(query: str)`
- **Purpose**: Search nursing protocols and guidelines
- **Implementation**: Calls `NursingAgent.search_protocols()`
- **Data Source**: Vertex AI Search (nursing datastore)
- **Examples**: "controlled medication protocol", "audit requirements for elderly"

#### Tool 3: `search_pharmacy_info(query: str)`
- **Purpose**: Search medication inventory and audit data
- **Implementation**: Calls `PharmacyAgent.search_inventory()`
- **Data Source**: Vertex AI Search (pharmacy datastore)
- **Examples**: "oxycodone availability", "audit dates for controlled substances"

### 3. Supporting Documents

#### Nursing Protocol
**File**: `docs/nursing/controlled_medication_protocol_en.md`

**Key Content**:
- General controlled medication administration procedures
- **Age-Specific Requirements for Patients >60 years**:
  - Enhanced monitoring (vital signs every 15 min)
  - Reduced dosing ("start low, go slow")
  - **CRITICAL**: 6-month medication audit requirement
  - Audit must be current before administering opioids
- Oxycodone-specific protocols with audit verification steps

#### Pharmacy Inventory
**File**: `docs/pharmacy/medication_inventory_en.md`

**Key Updates**:
- Added audit date column for controlled substances
- **Oxycodone 5mg**: Last audit April 15, 2024 (⚠️ OVERDUE)
- **Oxycodone 10mg**: Last audit April 15, 2024 (⚠️ OVERDUE)
- Clear note about 6-month audit requirement per nursing protocol

### 4. API Endpoint
**File**: `api.py`

**Endpoint**: `POST /research`

**Request Body**:
```json
{
  "query": "What do I need to do today with patient Juan de Marco?"
}
```

**Response**:
```json
{
  "query": "...",
  "answer": "...",
  "agent": "research",
  "iterations": 4,
  "tool_calls": 3,
  "tool_call_history": [
    {
      "iteration": 1,
      "function": "get_patient_details",
      "arguments": {"patient_name": "Juan de Marco"},
      "result_summary": "..."
    },
    ...
  ],
  "timestamp": "2025-10-28T..."
}
```

### 5. Demo Script
**File**: `demo_research.py`

**Usage**:
```bash
export GOOGLE_APPLICATION_CREDENTIALS=./sakey.json
python3 demo_research.py
```

**Demo Scenarios**:
1. **Juan de Marco** - Complex scenario with audit compliance check
2. **Maria Silva** - Simple medication schedule query
3. **Protocol Research** - Age-specific requirements for oxycodone
4. **Inventory Check** - Availability + compliance verification

## Example Research Flow

**Query**: "What do I need to do today with patient Juan de Marco?"

### Agent's Reasoning Process:

**Iteration 1**: Identify need for patient information
- **Tool Call**: `get_patient_details("Juan de Marco")`
- **Result**: Age 65, scheduled for Oxycodone 5mg at 9 AM

**Iteration 2**: Check nursing protocols for elderly patients on opioids
- **Tool Call**: `search_nursing_procedures("controlled medication oxycodone elderly over 60")`
- **Result**: Found 6-month audit requirement for patients >60 years

**Iteration 3**: Verify pharmacy audit compliance
- **Tool Call**: `search_pharmacy_info("oxycodone audit date")`
- **Result**: Last audit April 15, 2024 (>6 months ago, OVERDUE)

**Iteration 4**: Synthesize findings
- **Final Answer**:
  ```
  ⚠️ IMPORTANT - DO NOT ADMINISTER OXYCODONE

  Patient Juan de Marco (Age 65) is scheduled for:
  - Oxycodone 5mg at 09:00 AM (POST-SURGICAL PAIN)
  - Metformin 500mg at 08:00 AM (DIABETES)
  - Lisinopril 10mg at 08:00 AM (HYPERTENSION)

  CRITICAL ISSUE IDENTIFIED:
  Juan de Marco is over 60 years old and scheduled for controlled
  opioid medication (Oxycodone). Per nursing protocol NURSE-CTRL-MED-001,
  a comprehensive medication audit is required every 6 months for
  geriatric patients on opioids.

  Current audit status: OVERDUE (last audit: April 15, 2024)

  REQUIRED ACTIONS BEFORE ADMINISTERING OXYCODONE:
  1. DO NOT administer Oxycodone until audit is completed
  2. Contact attending physician (Dr. Sarah Thompson) immediately
  3. Notify Pain Management Team (Ext. 4650)
  4. Contact Pharmacy Department (Ext. 4500)
  5. Complete comprehensive medication audit

  Safe to administer today:
  ✓ Metformin 500mg at 08:00 AM
  ✓ Lisinopril 10mg at 08:00 AM
  ```

## Technical Implementation Details

### Gemini Function Calling Configuration

```python
# System instruction emphasizes step-by-step reasoning
system_instruction = """You are a hospital research assistant...
- Think step-by-step and reason through what information you need
- Use tools iteratively to gather relevant information
- Cross-reference information from different sources
- Identify any compliance issues or missing information
- Provide a clear, actionable answer
"""

# Generate with function calling
response = gemini_client.models.generate_content(
    model="gemini-2.5-flash",
    contents=contents,
    config=types.GenerateContentConfig(
        system_instruction=system_instruction,
        tools=[self.tools],  # Function declarations
        temperature=0.1
    )
)
```

### ReAct Loop Implementation

```python
iteration = 0
while iteration < max_iterations:
    iteration += 1

    # Generate response (may include function calls)
    response = gemini_client.models.generate_content(...)

    # Check if model wants to call a function
    if has_function_call(response):
        # Execute the function
        result = execute_tool(function_name, arguments)

        # Add to conversation history
        contents.append(function_call)
        contents.append(function_response)

        # Continue loop - model will process result
        continue

    # If text response, we have final answer
    if has_text(response):
        return final_answer
```

### Error Handling

- Tool execution errors are returned to the agent to handle
- Max iterations prevents infinite loops
- Graceful degradation if agent can't find complete answer
- All errors logged with detailed context

## Testing

### Unit Test (Import Check)
```bash
python3 -c "from agents.research_agent import ResearchAgent; print('✓ OK')"
```

### Full Demo
```bash
export GOOGLE_APPLICATION_CREDENTIALS=./sakey.json
python3 demo_research.py
```

### API Test
```bash
# Start API server
uvicorn api:app --reload

# Test endpoint
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"query": "What do I need to do today with patient Juan de Marco?"}'
```

## Configuration

**Environment Variables** (in `.env`):
```env
GCP_PROJECT_ID=your-project-id
GCP_LOCATION=us-central1
NURSING_DATASTORE_ID=your-nursing-datastore-id
PHARMACY_DATASTORE_ID=your-pharmacy-datastore-id
MODEL_NAME=gemini-2.5-flash
TEMPERATURE=0.1
```

## Key Advantages of This Approach

### 1. **ADK-Native**
- Uses Google's official Gemini function calling
- Compositional (sequential) tool execution
- Aligned with ADK best practices

### 2. **Transparent Reasoning**
- Full tool call history captured
- Iteration count visible
- Easy to debug and audit

### 3. **Flexible & Extensible**
- Easy to add new tools (just create function declaration)
- Max iterations configurable
- Temperature adjustable per query

### 4. **Safe & Compliant**
- Identifies safety issues (overdue audits)
- Cross-references multiple sources
- Provides actionable recommendations

### 5. **Efficient**
- Only calls tools when needed
- Stops when answer found
- Limits iterations to prevent waste

## Comparison: Research Agent vs Standard Orchestrator

| Feature | Standard Orchestrator | Research Agent |
|---------|----------------------|----------------|
| Routing | Single-shot classification | Multi-step reasoning |
| Data Sources | One datastore per query | Multiple sources per query |
| Cross-referencing | No | Yes (automatic) |
| Tool Usage | Pre-determined | Dynamic (agent decides) |
| Iterations | 1 | Up to 10 |
| Complexity | Simple queries | Complex multi-step queries |
| Patient Context | Limited | Full integration |
| Compliance Checking | Manual | Automatic |

## Best Use Cases

### Use Research Agent When:
- ✅ Query requires multiple data sources
- ✅ Need to cross-reference information
- ✅ Patient-specific context required
- ✅ Compliance checking needed
- ✅ Multi-step reasoning beneficial

### Use Standard Orchestrator When:
- ✅ Simple single-domain query
- ✅ Fast response critical
- ✅ No cross-referencing needed
- ✅ Direct answer sufficient

## Future Enhancements

1. **Database Integration**: Replace hardcoded patient data with real EMR/EHR
2. **More Tools**: Add scheduling, lab results, imaging, billing
3. **Memory**: Persistent conversation history
4. **Parallel Tools**: Call independent tools simultaneously
5. **Confidence Scoring**: Track reasoning confidence
6. **Human-in-Loop**: Request approval for critical actions
7. **Audit Logging**: Full compliance audit trail

## Troubleshooting

### Issue: "Research agent not initialized"
**Solution**: Check API startup logs, ensure ResearchAgent initialized

### Issue: Max iterations reached
**Solution**: Query may be too broad - try more specific query

### Issue: Tool execution errors
**Solution**: Check agent initialization, verify Vertex AI Search access

### Issue: Empty/incomplete answers
**Solution**: Check document coverage, verify search results quality

## Files Modified/Created

### New Files
- ✨ `agents/research_agent.py` - Main research agent implementation
- ✨ `docs/nursing/controlled_medication_protocol_en.md` - Nursing protocol with audit requirements
- ✨ `demo_research.py` - Interactive demo script
- ✨ `RESEARCH_AGENT_SETUP.md` - This documentation

### Modified Files
- 📝 `api.py` - Added `/research` endpoint and ResearchAgent initialization
- 📝 `docs/pharmacy/medication_inventory_en.md` - Added audit dates for oxycodone

## Summary

The Research Agent demonstrates advanced agentic capabilities using Google ADK's native function calling. It successfully:

✅ Implements ReAct-style reasoning loop
✅ Dynamically calls tools based on context
✅ Cross-references multiple data sources
✅ Identifies compliance issues automatically
✅ Provides detailed reasoning trace
✅ Scales from simple to complex queries

Perfect for complex healthcare workflows requiring multi-step reasoning and safety compliance.
