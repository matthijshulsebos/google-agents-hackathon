# Google Agents API Integration Guide

This guide explains how to integrate the MedAssist Nursing Assistant application with the Google Agents API for pharmacy/medication inventory queries.

## Overview

The application now supports integration with the Google Agents API, specifically for pharmacy and medication inventory queries. The API returns detailed medication information including stock levels, batch numbers, storage requirements, and more.

## API Response Format

The Google Agents API returns responses in this format:

```json
{
  "conversation_id": "d2e00ca8-df89-4d24-b54a-d041e67959d0",
  "query": "do we have Oxycodone available?",
  "answer": "Yes, we have Oxycodone 5mg available...",
  "agent": "pharmacy",
  "language": "en",
  "total_results": 200,
  "sources_count": 5,
  "grounding_metadata": [
    {
      "id": "unique-doc-id",
      "document": {
        "id": "doc-id",
        "name": "projects/.../documents/...",
        "data": {
          "supplier": "HealthLine Suppliers",
          "quantity": "642",
          "storage_requirement": "Refrigerated",
          "item_id": "ITEM-00111",
          "unit_price_eur": "263.51",
          "drug_name": "Oxycodone 5mg",
          "last_audit_date": "2025-05-24",
          "batch_number": "GXES3LT7",
          "expiry_date": "2026-03-16",
          "total_cost_eur": "169173.42",
          "controlled_substance": "No",
          "ndc": "65050-4484-07",
          "reorder_level": "123",
          "location": "A19-E-18"
        }
      }
    }
  ],
  "routing_info": {
    "category": "pharmacy",
    "confidence": "high",
    "method": "gemini",
    "raw_response": "pharmacy"
  },
  "timestamp": "2025-10-27T22:34:33.044984"
}
```

## Setup Instructions

### 1. Configure Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and configure:
```env
# Your Google Agents API endpoint
VITE_AGENT_API_URL=http://localhost:8000

# Enable real API (set to 'true' to use real API instead of mock data)
VITE_ENABLE_REAL_API=true
```

### 2. API Endpoint Requirements

Your backend API should expose a POST endpoint at `/query` that accepts:

**First Request (no conversation_id):**
```json
{
  "query": "Do we have Oxycodone?",
  "user_role": "employee"
}
```

**Follow-up Request (with conversation_id from previous response):**
```json
{
  "query": "Is it audited?",
  "user_role": "employee",
  "conversation_id": "90399413-437c-47e9-9718-eaddf88e5044"
}
```

**Response:** The Google Agents API response format shown above.

### 3. Testing the Integration

#### With Mock Data (Default)
The application works out of the box with mock data. No configuration needed.

#### With Real API
1. Set `VITE_ENABLE_REAL_API=true` in `.env`
2. Ensure your API is running at the configured URL
3. Restart the dev server: `npm run dev`
4. Ask medication-related questions in the chat

Example queries:
- "Do we have Oxycodone available?"
- "Check inventory for Morphine"
- "Show me all available pain medications"

## Implementation Details

### Key Files

1. **`src/types/api.ts`** - TypeScript types for the API response
2. **`src/services/agentApi.ts`** - API service functions
3. **`src/hooks/useChatMessages.ts`** - Chat hook with API integration
4. **`src/components/chat/MedicationPanel.tsx`** - UI component for displaying medication data

### API Service Functions

```typescript
import { queryAgent, isMedicationResponse, parseMedicationData } from './services/agentApi';

// Query the agent
const response = await queryAgent("do we have Oxycodone available?");

// Check if response contains medication data
if (isMedicationResponse(response)) {
  // Parse grounding metadata into medication items
  const medications = parseMedicationData(response);
  // Use medications in UI
}
```

### Data Flow

1. User types a message in the chat input
2. Message is sent to the agent API via `queryAgent()`
3. API response is checked with `isMedicationResponse()`
4. If medication data exists, `parseMedicationData()` extracts and formats it
5. `MedicationPanel` component displays the medication cards
6. Conversation ID is preserved for context

### Medication Data Display

The `MedicationPanel` component shows:
- Drug name and strength
- Stock status (in-stock, low-stock, out-of-stock)
- Current quantity vs reorder level
- Batch number and NDC code
- Storage requirements with visual indicators
- Expiry date
- Location in warehouse
- Supplier information
- Unit price
- Controlled substance indicator

### Stock Status Logic

```typescript
// Automatic status determination
if (quantity === 0) {
  status = 'out-of-stock';
} else if (quantity <= reorderLevel) {
  status = 'low-stock';
} else {
  status = 'in-stock';
}
```

## UI Features

### Visual Indicators

- **✓ In Stock** - Green badge (quantity > reorder level)
- **⚠ Low Stock** - Yellow badge (quantity ≤ reorder level)
- **✗ Out of Stock** - Red badge (quantity = 0)
- **🔒 Controlled** - Red tag for controlled substances
- **❄️** - Refrigerated/Frozen storage
- **🌡️** - Room temperature storage

### Medication Cards

Each medication batch is displayed as a card showing:
- Header with drug name, status, and controlled substance indicator
- Batch number and NDC
- Stock quantity and reorder level
- Supplier and pricing
- Storage location and requirements
- Expiry date and last audit date

## Extending the Integration

### Supporting Other Agents

The current implementation focuses on the `pharmacy` agent. To support other agents:

1. Add new types in `src/types/api.ts`
2. Create parsing functions in `src/services/agentApi.ts`
3. Create display components (similar to `MedicationPanel.tsx`)
4. Update `BotMessage.tsx` to render new panel types
5. Update the routing logic in `useChatMessages.ts`

Example for a hypothetical "patient" agent:

```typescript
// In src/services/agentApi.ts
export function isPatientResponse(response: AgentAPIResponse): boolean {
  return response.agent === 'patient' && response.grounding_metadata.length > 0;
}

export function parsePatientData(response: AgentAPIResponse): PatientInfo[] {
  // Parse patient data from grounding_metadata
}

// In src/hooks/useChatMessages.ts
if (isMedicationResponse(apiResponse)) {
  // Handle medication
} else if (isPatientResponse(apiResponse)) {
  // Handle patient data
}
```

### Error Handling

The implementation includes error handling:
- Network errors are caught and displayed to the user
- Fallback to error message if API fails
- Mock data mode as a backup option

### Conversation Context

Conversation IDs are automatically managed to enable contextual follow-up questions:

1. **First Query:**
   - Sent WITHOUT `conversation_id`
   - API creates new conversation session
   - Returns `conversation_id` in response
   - App stores ID in component state

2. **Follow-up Queries:**
   - Sent WITH stored `conversation_id`
   - API maintains conversation context
   - Can ask contextual questions like "Is it audited?" or "Show me more details"

**Example Flow:**
```typescript
// First query - no conversation_id
User: "Do we have Oxycodone?"
Request: { query: "...", user_role: "employee" }
Response: { conversation_id: "abc-123", ... }

// Follow-up query - includes conversation_id
User: "Is it audited?"
Request: { query: "...", user_role: "employee", conversation_id: "abc-123" }
Response: { conversation_id: "abc-123", answer: "Yes, all batches audited..." }
```

The AI understands context from previous questions in the same conversation!

## Example Integration

Here's a complete example of using the API:

```typescript
import { queryAgent, isMedicationResponse, parseMedicationData } from './services/agentApi';

async function checkMedication(query: string) {
  try {
    // Send query to agent
    const response = await queryAgent(query);

    console.log('Agent:', response.agent);
    console.log('Answer:', response.answer);

    // Check if pharmacy response
    if (isMedicationResponse(response)) {
      const medications = parseMedicationData(response);

      medications.forEach(med => {
        console.log(`${med.drugName}: ${med.quantity} units in stock`);
        console.log(`Status: ${med.status}`);
        console.log(`Location: ${med.location}`);
        console.log(`Controlled: ${med.controlledSubstance ? 'Yes' : 'No'}`);
      });
    }

    return response;
  } catch (error) {
    console.error('Error:', error);
  }
}

// Usage
checkMedication("do we have Oxycodone available?");
```

## Testing Checklist

- [ ] API endpoint is accessible
- [ ] Environment variables are configured
- [ ] Real API mode is enabled
- [ ] Medication queries return data
- [ ] Medication cards display correctly
- [ ] Stock status badges show correct colors
- [ ] Controlled substance indicators appear
- [ ] Storage icons display appropriately
- [ ] Conversation context is maintained
- [ ] Error handling works for failed requests

## Troubleshooting

### API Not Responding
- Check `VITE_AGENT_API_URL` in `.env`
- Verify the API server is running
- Check browser console for network errors
- Try with `VITE_ENABLE_REAL_API=false` to use mock data

### Data Not Displaying
- Check that `grounding_metadata` exists in API response
- Verify `agent` field is "pharmacy"
- Check browser console for parsing errors
- Inspect the response structure

### Conversation Context Lost
- Check that `conversation_id` is being returned by the API
- Verify it's being stored in component state
- Check that subsequent requests include the ID

## Future Enhancements

- Support for multiple agent types (scheduling, patient care, etc.)
- Real-time inventory updates via WebSocket
- Medication search and filtering
- Export medication reports
- Integration with hospital inventory systems
- Barcode scanning for quick lookups
- Low stock alerts and notifications
- Batch expiry warnings
