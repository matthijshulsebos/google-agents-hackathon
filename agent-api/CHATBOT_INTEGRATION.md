# Chatbot Integration Guide - Research Agent

## Overview

The `/research` endpoint now returns **dual response formats** optimized for chatbot integration:
- **`answer_summary`**: Concise 2-3 sentence summary for chatbot display
- **`answer_detailed`**: Full comprehensive answer with all details

This allows your chatbot to:
1. Display quick summary in the chat interface
2. Provide "Show more details" option to expand full answer
3. Maintain conversational flow while preserving detailed information

---

## Response Format

### API Response Structure

```json
{
  "query": "What do I need to do today with patient Juan de Marco?",
  "answer": "Full detailed answer...",           // Same as answer_detailed (backward compatibility)
  "answer_summary": "Concise 2-3 sentence summary...",  // NEW: For chatbot display
  "answer_detailed": "Full detailed answer...",  // NEW: Complete information
  "agent": "research",
  "iterations": 4,
  "tool_calls": 3,
  "tool_call_history": [...],
  "timestamp": "2025-10-28T00:05:48.489289"
}
```

### Field Descriptions

| Field | Purpose | Use Case | Character Length |
|-------|---------|----------|------------------|
| `answer_summary` | Chatbot conversation | Initial response in chat | ~150-300 chars |
| `answer_detailed` | Full information | "Show more" / email / reports | ~500-2000 chars |
| `answer` | Backward compatibility | Legacy systems | Same as answer_detailed |

---

## Chatbot Integration Examples

### Example 1: React Chatbot Component

```jsx
import React, { useState } from 'react';

function ResearchChatMessage({ response }) {
  const [showDetails, setShowDetails] = useState(false);

  return (
    <div className="chat-message">
      {/* Show summary by default */}
      <div className="message-summary">
        {response.answer_summary}
      </div>

      {/* Toggle button */}
      <button
        onClick={() => setShowDetails(!showDetails)}
        className="details-toggle"
      >
        {showDetails ? 'Hide details' : 'Show more details'}
      </button>

      {/* Expandable detailed answer */}
      {showDetails && (
        <div className="message-detailed">
          {response.answer_detailed}
        </div>
      )}

      {/* Optional: Show metadata */}
      <div className="message-metadata">
        {response.iterations} iterations | {response.tool_calls} tool calls
      </div>
    </div>
  );
}

export default ResearchChatMessage;
```

---

### Example 2: Slack Bot Integration

```python
from slack_bolt import App
import requests

app = App(token="your-slack-token")

@app.message("research")
def handle_research(message, say):
    query = message['text'].replace('research', '').strip()

    # Call research endpoint
    response = requests.post(
        "http://localhost:8000/research",
        json={"query": query}
    ).json()

    # Send summary as main message
    say(
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Research Results*\n\n{response['answer_summary']}"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Show Full Details"},
                        "action_id": "show_details",
                        "value": response['answer_detailed']
                    }
                ]
            }
        ]
    )

@app.action("show_details")
def show_details(ack, body, say):
    ack()
    detailed_answer = body['actions'][0]['value']
    say(f"*Full Details:*\n\n{detailed_answer}")
```

---

### Example 3: Discord Bot

```python
import discord
from discord.ext import commands
import requests

bot = commands.Bot(command_prefix='!')

@bot.command(name='research')
async def research(ctx, *, query):
    # Call research endpoint
    response = requests.post(
        "http://localhost:8000/research",
        json={"query": query}
    ).json()

    # Create embed with summary
    embed = discord.Embed(
        title="Research Results",
        description=response['answer_summary'],
        color=discord.Color.blue()
    )

    embed.add_field(
        name="Iterations",
        value=response['iterations'],
        inline=True
    )
    embed.add_field(
        name="Tool Calls",
        value=response['tool_calls'],
        inline=True
    )

    # Send summary
    message = await ctx.send(embed=embed)

    # Add reaction for details
    await message.add_reaction('📋')

    # Store detailed answer for reaction handler
    bot.detailed_answers[message.id] = response['answer_detailed']

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    if str(reaction.emoji) == '📋':
        # Send detailed answer as DM or thread
        detailed = bot.detailed_answers.get(reaction.message.id)
        if detailed:
            await user.send(f"**Full Details:**\n\n{detailed}")
```

---

### Example 4: Simple Python CLI Chatbot

```python
import requests

def chat_research(query):
    """Simple chatbot function for research queries"""

    response = requests.post(
        "http://localhost:8000/research",
        json={"query": query}
    ).json()

    # Display summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(response['answer_summary'])

    # Ask if user wants details
    show_more = input("\n\nShow full details? (y/n): ").lower()

    if show_more == 'y':
        print("\n" + "="*60)
        print("DETAILED ANSWER")
        print("="*60)
        print(response['answer_detailed'])

        # Show metadata
        print(f"\n[Iterations: {response['iterations']}, Tool Calls: {response['tool_calls']}]")

# Usage
if __name__ == "__main__":
    while True:
        query = input("\nAsk a question (or 'quit' to exit): ")
        if query.lower() == 'quit':
            break
        chat_research(query)
```

---

## Sample Outputs

### Query: "What do I need to do today with patient Juan de Marco?"

#### Summary (answer_summary):
```
Juan de Marco (65) is scheduled for Oxycodone 5mg at 09:00 AM, Metformin 500mg (08:00 AM, 08:00 PM), and Lisinopril 10mg (08:00 AM). CRITICAL: Before giving Oxycodone, you MUST check the pharmacy audit system—if the audit is overdue (>6 months), HOLD the medication and notify the physician, pain management team, and pharmacy immediately.
```

**Character count**: ~306 chars
**Reading time**: ~12 seconds
**Use case**: Quick chatbot response, notification, alert

---

#### Detailed (answer_detailed):
```
Here is a summary of what needs to be done today for patient Juan de Marco, based on the information gathered:

**Patient Details:**
*   **Name:** Juan de Marco
*   **Age:** 65 years old
*   **Medical History:** Type 2 Diabetes, Hypertension, Total knee replacement surgery (January 20, 2025).
*   **Allergies:** Penicillin (rash)
*   **Current Location:** Room 302, Orthopedic Ward

**Scheduled Medications for Today:**

1.  **Oxycodone 5mg (Oral) - Scheduled for 09:00 AM**
    *   **Reason:** Post-surgical pain management.
    *   **Critical Nursing Protocol Requirements (for Geriatric Patients >60 years):**
        *   **Mandatory Pharmacy Audit Check:** Before administering, you **MUST** check...
        [... full detailed protocol continues ...]

**Actionable Steps for Today:**
1. Immediately check the Pharmacy Audit System...
2. Verify the controlled substance classification...
[... continues with all 6 steps ...]
```

**Character count**: ~2000+ chars
**Reading time**: ~2-3 minutes
**Use case**: Full review, documentation, handoff notes, email

---

## Summary Generation Details

### How It Works

1. **Research agent completes** ReAct loop with tool calls
2. **Generates detailed answer** with all information
3. **Calls Gemini again** with summary prompt:
   ```
   Given the detailed research answer below, create a concise 2-3 sentence summary
   suitable for a chatbot conversation.

   The summary should:
   - Capture the most critical information and actions needed
   - Be conversational and easy to understand
   - Highlight any urgent safety concerns or compliance issues
   - Be suitable for displaying in a chat interface
   ```
4. **Returns both versions** in the response

### Summary Characteristics

✅ **Concise**: 2-3 sentences (~150-300 chars)
✅ **Actionable**: Focuses on what to do
✅ **Safety-first**: Highlights critical issues
✅ **Conversational**: Natural chatbot language
✅ **Complete**: Includes key patient/medication details

### Fallback Behavior

If summary generation fails:
- Falls back to first 200 characters of detailed answer + "..."
- Ensures chatbot always has something to display
- Logged as warning for monitoring

---

## Best Practices

### 1. Display Summary First
```javascript
// ✅ Good: Show summary by default
<ChatMessage>
  {response.answer_summary}
  <ShowMoreButton />
</ChatMessage>

// ❌ Bad: Show full answer in chat
<ChatMessage>
  {response.answer_detailed}  // Too long for chat
</ChatMessage>
```

### 2. Progressive Disclosure
```javascript
// ✅ Good: Let user expand if interested
const [expanded, setExpanded] = useState(false);

return (
  <>
    <Summary>{answer_summary}</Summary>
    {expanded ? <Details>{answer_detailed}</Details> : <ExpandButton />}
  </>
);
```

### 3. Context-Aware Display
```javascript
// ✅ Good: Adapt based on context
if (isCriticalAlert) {
  // Show both summary AND details immediately
  return <><Summary /><Details /></>;
} else {
  // Normal flow: summary with expand option
  return <><Summary /><ExpandButton /></>;
}
```

### 4. Use Metadata
```javascript
// ✅ Good: Show processing metadata for transparency
<MessageFooter>
  Generated in {iterations} iterations using {tool_calls} data sources
</MessageFooter>
```

---

## Use Cases by Platform

| Platform | Recommended Display | Reasoning |
|----------|---------------------|-----------|
| **Slack** | Summary + button | Limited screen space, threaded details work well |
| **Discord** | Summary + reaction | Embed limits, reactions for optional details |
| **Web Chat** | Summary + expand | Progressive disclosure, better UX |
| **Mobile App** | Summary + modal | Small screen, modal for details on tap |
| **SMS/WhatsApp** | Summary only | Character limits, send details as follow-up if requested |
| **Voice Assistant** | Summary only | Spoken responses need to be concise |
| **Email Report** | Both versions | Email can include both for reference |
| **CLI/Terminal** | Ask user preference | Terminal users may want full control |

---

## Testing the Feature

### Quick Test (Python)
```python
import requests

response = requests.post(
    "http://localhost:8000/research",
    json={"query": "What do I need to do today with patient Juan de Marco?"}
).json()

print("SUMMARY:")
print(response['answer_summary'])
print("\n" + "="*80 + "\n")
print("DETAILED:")
print(response['answer_detailed'])
```

### Quick Test (curl)
```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"query": "What do I need to do today with patient Juan de Marco?"}' \
  | jq '.answer_summary, .answer_detailed'
```

---

## Performance Considerations

### Summary Generation Cost
- **Additional API call**: 1 extra Gemini call per research query
- **Latency**: +0.5-1.5 seconds
- **Tokens**: ~200-500 input tokens, ~50-150 output tokens

### Optimization Tips
1. **Cache summaries**: Store generated summaries in your database
2. **Async generation**: Generate summary in background if latency is concern
3. **Fallback fast**: Use first 200 chars if summary generation is slow
4. **Monitor**: Track summary generation failures and latency

---

## Future Enhancements

Potential improvements for chatbot integration:

1. **Multiple summary levels**:
   - `answer_summary_ultra_short`: 1 sentence (~50 chars)
   - `answer_summary`: 2-3 sentences (~200 chars)
   - `answer_summary_expanded`: 1 paragraph (~500 chars)

2. **Structured summary**:
   ```json
   "answer_summary_structured": {
     "patient": "Juan de Marco (65)",
     "critical_action": "Check audit before giving Oxycodone",
     "medications": ["Oxycodone 5mg", "Metformin 500mg", "Lisinopril 10mg"]
   }
   ```

3. **Audio-optimized summary**: Formatted for text-to-speech

4. **Language-specific summaries**: Different summary styles for different languages

---

## Support & Questions

For implementation questions or issues:
- Check FastAPI docs at `/docs` for interactive API testing
- Review example responses in this guide
- Test with `demo_research.py` to see full flow

The dual response format ensures your chatbot can provide both **quick, conversational responses** and **comprehensive detailed information** when needed! 🤖💬
