# Markdown Rendering in Chat

## Overview

All chat messages from the AI now support **full markdown formatting**, allowing rich text display with headings, lists, bold/italic text, code blocks, tables, and more!

## Features

The chat bubbles can now render:

### Text Formatting
- **Bold text** using `**text**` or `__text__`
- *Italic text* using `*text*` or `_text_`
- `Inline code` using backticks
- ~~Strikethrough~~ using `~~text~~` (via GFM)

### Headings
```markdown
# Heading 1
## Heading 2
### Heading 3
#### Heading 4
```

### Lists
**Unordered:**
```markdown
- Item 1
- Item 2
  - Nested item 2.1
  - Nested item 2.2
- Item 3
```

**Ordered:**
```markdown
1. First item
2. Second item
3. Third item
```

### Code Blocks
**Inline code:**
```markdown
Use the `query()` function
```

**Code blocks:**
````markdown
```python
def hello():
    print("Hello, World!")
```
````

### Links
```markdown
[Link text](https://example.com)
```
- Links automatically open in new tabs
- Styled with primary color and underline

### Blockquotes
```markdown
> This is a blockquote
> It can span multiple lines
```

### Horizontal Rules
```markdown
---
```

### Tables (via GitHub Flavored Markdown)
```markdown
| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Cell 1   | Cell 2   | Cell 3   |
| Cell 4   | Cell 5   | Cell 6   |
```

## Implementation

### Libraries Used

- **react-markdown** - Core markdown renderer
- **remark-gfm** - GitHub Flavored Markdown support (tables, strikethrough, etc.)

### Components

**`MarkdownContent.tsx`**
- Renders markdown with custom styling
- Customizes all markdown elements for chat bubble display
- Ensures consistent sizing and spacing

**`ExpandableAnswer.tsx`**
- Uses `MarkdownContent` for both summary and detailed views
- Markdown works seamlessly with expand/collapse

### Styling

Custom styles ensure markdown looks great in chat bubbles:

**Headings:** Bold, properly sized, good spacing
**Lists:** Indented with bullets/numbers, nested support
**Code:** Gray background, monospace font, inline and block support
**Tables:** Bordered, scrollable, proper spacing
**Links:** Primary color, underline, opens in new tab

## Example API Response with Markdown

```json
{
  "answer_summary": "Yes, **Oxycodone** is in stock with _several batches_ available.",
  "answer_detailed": "Yes, we do have **Oxycodone** in stock.\n\n**Policy Details**: Our inventory records indicate...\n\n**Specific Information**:\n- **From HealthLine Suppliers**:\n  - Drug: Oxycodone 5mg\n  - Quantity: 642 units\n  - Storage: `Refrigerated`\n\n**Important Notes**:\nPlease note the different storage requirements...\n\n**Next Steps**:\nContact the [Pharmacy Department](mailto:pharmacy@example.com) for access."
}
```

**Renders as:**

Summary view shows bold "Oxycodone" and italic "several batches"

Detailed view displays:
- Bold section headers
- Formatted bullet lists
- Inline code for storage requirements
- Clickable links to pharmacy department

## Custom Component Styling

Each markdown element has custom styling:

```typescript
// Headings
h1: "text-lg font-bold text-gray-900"
h2: "text-base font-bold text-gray-900"
h3: "text-sm font-semibold text-gray-900"

// Text
p: "text-sm text-gray-800 mb-2"
strong: "font-bold text-gray-900"
em: "italic text-gray-700"

// Code
inline: "bg-gray-200 px-1.5 py-0.5 rounded"
block: "bg-gray-200 p-2 rounded font-mono"

// Lists
ul: "ml-4 list-disc space-y-1"
ol: "ml-4 list-decimal space-y-1"

// Links
a: "text-primary underline"
```

## Usage Examples

### 1. Medication Information
```markdown
**Medication**: Oxycodone 5mg
**Quantity**: 642 units
**Storage**: Refrigerated ❄️

*Status*: ✓ In Stock
```

### 2. Policy Details
```markdown
## Storage Requirements

Please note:
1. **Refrigerated** items must be stored at 2-8°C
2. **Frozen** items must be stored at -20°C
3. **Room temperature** items at 15-25°C

> ⚠️ Controlled substances require special handling
```

### 3. Procedural Steps
```markdown
### Emergency Protocol: Code Blue

**Immediate Actions**:
1. Call `2222` immediately
2. Begin CPR
3. Prepare resuscitation equipment
4. Notify attending physician

**Equipment Needed**:
- Defibrillator
- Oxygen
- Emergency medications
```

### 4. Reference Information
```markdown
For more information, see:
- [Normal Vital Ranges](http://example.com/vitals)
- [Dosage Calculator](http://example.com/dosage)
- [Emergency Contacts](http://example.com/emergency)

---

*Last updated: 2024-12-27*
```

## Benefits

✅ **Rich Formatting** - Full markdown support for complex content
✅ **Better Readability** - Proper structure with headings and lists
✅ **Professional Look** - Styled to match application design
✅ **Semantic HTML** - Proper HTML elements for accessibility
✅ **GFM Support** - Tables, strikethrough, and more
✅ **Safe Rendering** - Sanitized to prevent XSS attacks

## Technical Details

### Security

- react-markdown automatically sanitizes input
- No raw HTML allowed by default
- Links open in new tabs with `rel="noopener noreferrer"`

### Performance

- Lightweight renderer (minimal bundle size)
- Fast parsing and rendering
- Works seamlessly with React hooks

### Accessibility

- Semantic HTML elements
- Proper heading hierarchy
- Screen reader friendly
- Keyboard navigation for links

## Testing

Open the application and send markdown-formatted queries:

**Test 1: Basic formatting**
```
Query: "Do we have **Oxycodone** in _stock_?"
```

**Test 2: Lists and headings**
```
Query: "Show me:\n1. Medication name\n2. Quantity\n3. Location"
```

**Test 3: Code and links**
```
Query: "Use `queryInventory()` function or visit [Pharmacy](http://example.com)"
```

## Troubleshooting

**Issue:** Markdown not rendering
- Check that `react-markdown` is installed
- Verify `MarkdownContent` component is used
- Check browser console for errors

**Issue:** Styling looks off
- Ensure Tailwind CSS is loaded
- Check that prose classes are applied
- Verify custom CSS in `index.css`

**Issue:** Links not clickable
- Ensure component has `target="_blank"`
- Check that links are properly formatted in markdown

---

**Status:** 🟢 Fully Implemented and Working

All chat messages now support rich markdown formatting for a better user experience!
