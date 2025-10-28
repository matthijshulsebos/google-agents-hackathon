# Expandable Answers Feature

## Overview

The MedAssist application now supports **expandable answers** that display a concise summary by default with an option to expand to see the full detailed response.

## How It Works

### API Response Fields

The Google Agents API now returns three answer fields:

```json
{
  "answer": "Full answer text (fallback)",
  "answer_summary": "Short, concise summary",
  "answer_detailed": "Complete detailed answer with all information"
}
```

### Display Logic

1. **If both `answer_summary` and `answer_detailed` exist:**
   - Shows `answer_summary` by default
   - Displays "Show more details" button
   - Clicking expands to show `answer_detailed`
   - Button changes to "Show less" with collapse icon

2. **If only one or neither exists:**
   - Shows `answer` (fallback)
   - No expand/collapse button

3. **If summary equals detailed:**
   - Shows the text without expand button (no difference to show)

## Visual Design

### Collapsed State (Default)
```
┌─────────────────────────────────────────┐
│ Bot Avatar                              │
│  🤖                                     │
│     ┌───────────────────────────────┐  │
│     │ Summary text here...          │  │
│     │                               │  │
│     │ ▼ Show more details           │  │
│     └───────────────────────────────┘  │
└─────────────────────────────────────────┘
```

### Expanded State
```
┌─────────────────────────────────────────┐
│ Bot Avatar                              │
│  🤖                                     │
│     ┌───────────────────────────────┐  │
│     │ Detailed answer text here...  │  │
│     │ With full information...      │  │
│     │ All policy details...         │  │
│     │ Complete references...        │  │
│     │                               │  │
│     │ ▲ Show less                   │  │
│     └───────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## Example Responses

### Example 1: Medication Query

**Summary:**
> "Yes, Oxycodone is currently in stock, with several batches available from different suppliers. These batches vary in quantity, storage requirements (refrigerated or room temperature), expiry dates, and whether they are classified as controlled substances."

**Detailed:**
> "Yes, we do have Oxycodone in stock.
>
> **Policy Details**: Our inventory records indicate that we have several batches...
>
> **Specific Information**:
> - **From HealthLine Suppliers (ITEM-00111)**:
>   - Drug Name: Oxycodone 5mg
>   - Quantity: 642 units
>   - Storage: Refrigerated
>   - Controlled: No
>   - Expires: 2026-03-16
>   - Location: A19-E-18
> ..."

**User Experience:**
1. User asks: "Do we have Oxycodone?"
2. AI shows summary (quick answer)
3. User clicks "Show more details" if needed
4. Full information appears
5. User can click "Show less" to collapse

## Implementation Details

### Components

**`ExpandableAnswer.tsx`**
- Takes `summary`, `detailed`, and `fallback` props
- Manages expand/collapse state
- Renders appropriate content based on availability
- Shows/hides expand button intelligently

**`BotMessage.tsx`**
- Uses `ExpandableAnswer` for all bot responses
- Passes summary/detailed fields from ChatMessage
- Falls back to `content` if summary/detailed unavailable

### TypeScript Types

**`AgentAPIResponse`** (API response):
```typescript
{
  answer: string;
  answer_summary?: string;
  answer_detailed?: string;
  // ... other fields
}
```

**`ChatMessage`** (UI state):
```typescript
{
  content: string;
  contentSummary?: string;
  contentDetailed?: string;
  // ... other fields
}
```

### State Management

```typescript
const [isExpanded, setIsExpanded] = useState(false);

// Determines what to show
const displayText = isExpanded
  ? (detailed || fallback)
  : (summary || fallback);
```

## Benefits

### For Users

✅ **Faster Scanning**
- Quick summary lets users get immediate answers
- No need to read through long responses

✅ **On-Demand Details**
- Full information available when needed
- User controls information density

✅ **Better UX**
- Less scrolling for quick queries
- More details for complex questions

### For the System

✅ **Reduced Cognitive Load**
- Summary first, details on demand
- Progressive disclosure pattern

✅ **Responsive Layout**
- Keeps interface clean
- Better use of screen space

✅ **Flexible Content**
- Works with any content length
- Graceful degradation (fallback to full answer)

## Testing

### Test Cases

1. **With summary and detailed:**
   - ✅ Summary shows by default
   - ✅ Expand button appears
   - ✅ Click shows detailed version
   - ✅ Collapse button works

2. **With only answer:**
   - ✅ Shows full answer
   - ✅ No expand button

3. **With identical summary/detailed:**
   - ✅ Shows text once
   - ✅ No expand button

### Manual Testing

Ask the API:
```
"Do we have Oxycodone?"
```

**Expected:**
- Summary appears first
- "Show more details" button visible
- Click to expand
- Full detailed answer appears
- "Show less" button visible
- Click to collapse back to summary

## Styling

### Button Styles
- Small text (`text-xs`)
- Primary color
- Hover effect (darker blue)
- Chevron icons (up/down)
- Smooth transitions

### Text Formatting
- Summary: Concise, single paragraph typically
- Detailed: Multi-line with formatting preserved (`whitespace-pre-line`)
- Both use same bubble styling for consistency

## Future Enhancements

Possible improvements:

- 🔄 Smooth expand/collapse animation
- 📊 Show character count or reading time
- 🎨 Different styling for expanded state
- 💾 Remember user preference (always expanded/collapsed)
- 📱 Mobile-optimized touch targets
- ⌨️ Keyboard accessibility (space/enter to toggle)

## API Integration

The feature automatically works when the API returns `answer_summary` and `answer_detailed`. No configuration needed!

**Request:** Standard query
```json
{
  "query": "Do we have Oxycodone?",
  "user_role": "employee"
}
```

**Response:** With summary and detailed fields
```json
{
  "answer": "Yes, we do have Oxycodone...",
  "answer_summary": "Yes, Oxycodone is in stock with several batches...",
  "answer_detailed": "Yes, we do have Oxycodone in stock.\n\n**Policy Details**:..."
}
```

**Result:** Expandable answer in UI!

---

**Status:** 🟢 Fully Implemented and Working

The expandable answers feature provides a better user experience by showing concise information first with the option to view full details on demand!
