# Quick Start: Google Agents API Integration

Get your MedAssist Nursing Assistant application connected to the Google Agents API in 3 simple steps!

## Prerequisites

- Node.js 18+ installed
- Google Agents API endpoint running (typically at `http://localhost:8000`)
- Application already set up (see main README if not)

## Step 1: Configure Environment

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and set:

```env
# Point to your Google Agents API endpoint
VITE_AGENT_API_URL=http://localhost:8000

# Enable real API mode
VITE_ENABLE_REAL_API=true
```

## Step 2: Start the Application

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## Step 3: Test It!

Open the application and try these queries in the chat:

1. **"Do we have Oxycodone available?"**
   - Should return medication inventory data
   - Shows stock levels, batch numbers, locations

2. **"Check inventory for Morphine"**
   - Returns all Morphine batches
   - Displays storage requirements

3. **"Show me controlled substances"**
   - Lists medications marked as controlled

## What You'll See

When you send a medication query, the AI will respond with:

### Text Answer
A natural language summary of the results (from the API's `answer` field)

### Medication Cards
Visual cards showing for each batch:
- ✓ **Stock Status** (In Stock / Low Stock / Out of Stock)
- 📦 **Current Quantity** and reorder level
- 🔒 **Controlled Substance** indicator
- 📍 **Location** in warehouse
- ❄️ **Storage Requirements** (Refrigerated, Room temp, etc.)
- 📅 **Expiry Date** and last audit date
- 💰 **Pricing** and supplier information
- 🏷️ **Batch Number** and NDC code

## Switching Back to Mock Data

To use the built-in mock data instead of the real API:

In `.env`, set:
```env
VITE_ENABLE_REAL_API=false
```

Or simply don't create a `.env` file (app defaults to mock mode).

## Troubleshooting

### "Sorry, I encountered an error"

**Problem:** API is not accessible

**Solutions:**
- Check that `VITE_AGENT_API_URL` matches your API endpoint
- Verify the API server is running
- Check browser console for detailed error messages
- Test the API directly: `curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -d '{"query":"test"}'`

### No medication cards showing

**Problem:** API response format mismatch

**Solutions:**
- Verify API returns `grounding_metadata` array
- Check that `agent` field equals `"pharmacy"`
- Inspect the full API response in browser console
- See `GOOGLE_AGENTS_INTEGRATION.md` for expected format

### API working but using mock data

**Problem:** Environment variable not set correctly

**Solutions:**
- Ensure `.env` file exists in project root
- Variable must be exactly `VITE_ENABLE_REAL_API=true`
- Restart the dev server after changing `.env`
- Check with: `console.log(import.meta.env.VITE_ENABLE_REAL_API)`

## API Endpoint Requirements

Your Google Agents API should accept:

**POST `/query`**

Request:
```json
{
  "query": "do we have Oxycodone available?",
  "conversation_id": "optional-id-for-context",
  "language": "en"
}
```

Response: See example in `GOOGLE_AGENTS_INTEGRATION.md`

## Next Steps

- Read [`GOOGLE_AGENTS_INTEGRATION.md`](./GOOGLE_AGENTS_INTEGRATION.md) for detailed documentation
- Customize the medication display in `src/components/chat/MedicationPanel.tsx`
- Add support for other agent types (patient, scheduling, etc.)
- Implement error boundaries for better error handling
- Add loading states and animations

## Example Queries to Try

### Medication Availability
- "Do we have aspirin?"
- "Check stock for ibuprofen"
- "What pain medications are available?"

### Specific Information
- "Show me all refrigerated medications"
- "List controlled substances"
- "Find medications expiring soon"

### Quantity Checks
- "How many units of Oxycodone do we have?"
- "Is our Morphine stock low?"
- "Check reorder levels for pain meds"

## Support

For issues or questions:
1. Check the [Integration Guide](./GOOGLE_AGENTS_INTEGRATION.md)
2. Review browser console for errors
3. Inspect network tab for API responses
4. Check the API server logs

Happy coding! 🚀
