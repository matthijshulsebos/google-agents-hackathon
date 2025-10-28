# Conversation Flow Testing Guide

## ✅ Conversation Context Feature Verified

The application now correctly handles conversation sessions with the Google Agents API!

## How It Works

### First Message in Session
```bash
# User asks first question - NO conversation_id sent
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Do we have Oxycodone?",
    "user_role": "employee"
  }'
```

**Response includes:**
```json
{
  "conversation_id": "004e51e5-0ea7-4dcf-acbd-d49146a3ebb3",
  "answer": "Yes, we have Oxycodone 5mg available...",
  ...
}
```

### Follow-up Messages
```bash
# User asks follow-up - conversation_id IS sent
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Is it audited?",
    "user_role": "employee",
    "conversation_id": "004e51e5-0ea7-4dcf-acbd-d49146a3ebb3"
  }'
```

**AI understands context!**
```json
{
  "conversation_id": "004e51e5-0ea7-4dcf-acbd-d49146a3ebb3",
  "answer": "Yes, all the listed batches of Oxycodone have been audited...",
  ...
}
```

Notice: The AI knows "it" refers to Oxycodone from the previous question!

## Implementation Details

### API Service (`src/services/agentApi.ts`)

```typescript
export async function queryAgent(
  message: string,
  conversationId?: string,  // Optional - undefined for first message
  userRole: string = 'employee'
): Promise<AgentAPIResponse> {
  const requestBody: Record<string, string> = {
    query: message,
    user_role: userRole,
  };

  // Only include conversation_id if it exists
  if (conversationId) {
    requestBody.conversation_id = conversationId;
  }

  // Send request...
}
```

### Chat Hook (`src/hooks/useChatMessages.ts`)

```typescript
const [conversationId, setConversationId] = useState<string | undefined>();

// First message: conversationId is undefined
const apiResponse = await queryAgent(userMessage, conversationId);

// Store conversation_id from response
if (!conversationId) {
  setConversationId(apiResponse.conversation_id);
}

// Next messages: conversationId has value, gets sent automatically!
```

## Testing in the UI

### Scenario 1: Medication Availability + Follow-up

1. **First Question:**
   ```
   "Do we have Oxycodone?"
   ```
   - App sends: `{ query: "...", user_role: "employee" }`
   - No `conversation_id` in request
   - AI responds with medication details
   - App stores returned `conversation_id`

2. **Follow-up Question:**
   ```
   "Is it audited?"
   ```
   - App sends: `{ query: "...", user_role: "employee", conversation_id: "abc-123" }`
   - Includes stored `conversation_id`
   - AI understands "it" = Oxycodone
   - Responds with audit information

### Scenario 2: Stock Levels + Location

1. **First:** "How many units of Morphine do we have?"
2. **Follow-up:** "Where is it stored?"
   - AI knows "it" = Morphine
   - Returns location from context

### Scenario 3: Multiple Follow-ups

1. **First:** "Do we have controlled substances?"
2. **Follow-up 1:** "Which ones are refrigerated?"
3. **Follow-up 2:** "Show me their expiry dates"
   - All questions maintain context
   - Same `conversation_id` throughout

## Request Flow Diagram

```
User Action                  Request Body                        Response
═══════════════════════════════════════════════════════════════════════════

[New Chat Session]
├─ "Do we have Oxycodone?"
│  └─> { query: "...",              ──────>  { conversation_id: "abc-123",
│        user_role: "employee" }                answer: "Yes, we have..." }
│
├─ App stores: conversationId = "abc-123"
│
├─ "Is it audited?"
│  └─> { query: "...",              ──────>  { conversation_id: "abc-123",
│        user_role: "employee",                 answer: "Yes, all batches..." }
│        conversation_id: "abc-123" }
│
├─ "Where is it located?"
│  └─> { query: "...",              ──────>  { conversation_id: "abc-123",
│        user_role: "employee",                 answer: "Locations: A19-E-18..." }
│        conversation_id: "abc-123" }
│
└─ All using same conversation_id!
```

## Parameters Explained

### `user_role`
- **Default:** `"employee"`
- **Purpose:** Identifies user's role for access control
- **Values:** `"employee"`, `"admin"`, `"pharmacist"`, etc.
- **Sent:** With every request

### `conversation_id`
- **Default:** `undefined` (not sent)
- **Purpose:** Maintains conversation context
- **Format:** UUID string (e.g., `"90399413-437c-47e9-9718-eaddf88e5044"`)
- **Sent:** Only after first response, with all follow-ups

## Testing Checklist

In the browser (http://localhost:5173):

- [ ] Ask: "Do we have Oxycodone?"
- [ ] Verify medication cards appear
- [ ] Ask: "Is it audited?"
- [ ] Verify AI responds about Oxycodone audits (understands context)
- [ ] Ask: "Where is it stored?"
- [ ] Verify AI provides locations (still in context)
- [ ] Open Browser DevTools → Network tab
- [ ] Check first request: NO `conversation_id` field
- [ ] Check second request: HAS `conversation_id` field
- [ ] Verify all requests have `user_role: "employee"`

## Debugging

### Check Network Requests

Open Browser DevTools (F12) → Network tab:

**First Request:**
```json
{
  "query": "Do we have Oxycodone?",
  "user_role": "employee"
  // NO conversation_id
}
```

**Second Request:**
```json
{
  "query": "Is it audited?",
  "user_role": "employee",
  "conversation_id": "004e51e5-0ea7-4dcf-acbd-d49146a3ebb3"
  // HAS conversation_id
}
```

### Check Console

Look for logs showing conversation_id being stored:
```javascript
console.log('Conversation ID:', conversationId); // undefined first time
console.log('Storing conversation ID:', apiResponse.conversation_id);
console.log('Using conversation ID:', conversationId); // has value second time
```

## Benefits

✅ **Natural Conversations**
- Ask follow-up questions naturally
- Use pronouns like "it", "them", "that"
- No need to repeat medication names

✅ **Contextual Understanding**
- AI remembers previous questions
- Can drill down into details
- Multi-turn conversations work smoothly

✅ **Better UX**
- Faster queries (shorter questions)
- More natural interaction
- Less typing for users

## Example Conversations

### Example 1: Detailed Inquiry
```
You: "Show me all controlled substances"
AI: [Lists controlled substances]

You: "Which ones expire in 2026?"
AI: [Filters to 2026 expiry dates]

You: "Are they refrigerated?"
AI: [Provides storage info for those items]
```

### Example 2: Stock Management
```
You: "Do we have Morphine?"
AI: [Shows Morphine inventory]

You: "Is any batch below reorder level?"
AI: [Checks reorder levels]

You: "When were they last audited?"
AI: [Provides audit dates]
```

---

**Status:** 🟢 Conversation Context Fully Working

The application seamlessly manages conversation state and enables natural, contextual interactions with the Google Agents API!
