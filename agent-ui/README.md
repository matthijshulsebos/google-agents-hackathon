# MedAssist Nursing Assistant

<p align="center">
  <img src="../assets/agent_tool_gui.png" alt="GUI of the tool" width="70%">
</p>

---

A comprehensive nursing assistant dashboard built with React, TypeScript, and Tailwind CSS. This application provides nurses with quick access to schedules, patient information, emergency protocols, medication inventory, and interactive AI assistance.

## Features

- **Interactive Dashboard**: Three-column layout with navigation, main content, and quick reference sidebars
- **AI Chat Assistant**: Integrated with Google Agents API for intelligent responses to queries about medications, schedules, procedures, and protocols
- **Medication Inventory**: Real-time medication stock checking with detailed batch information, storage requirements, and controlled substance tracking
- **Quick Actions**: Fast access to schedule info, medication guides, supply checks, patient status, and emergency protocols
- **Active Alerts**: Real-time critical and warning alerts displayed prominently
- **Schedule Management**: Today's schedule with upcoming tasks and shift information
- **Quick References**: Easy access to vital ranges, dosage calculators, and emergency numbers
- **Responsive Design**: Clean, modern UI with Material Design-inspired components

## 🆕 Google Agents Integration

The application now supports integration with **Google Agents API** for pharmacy and medication inventory queries!

**See [`GOOGLE_AGENTS_INTEGRATION.md`](./GOOGLE_AGENTS_INTEGRATION.md) for complete integration guide.**

Key capabilities:
- Query medication availability in real-time
- View detailed batch information (NDC, expiry dates, locations)
- Check stock levels and reorder thresholds
- See storage requirements and controlled substance status
- Maintain conversation context across queries

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Icon library
- **Context API** - State management

## Project Structure

```
src/
├── components/
│   ├── layout/          # Main layout components
│   ├── navigation/      # Nav menu and user profile
│   ├── dashboard/       # Dashboard-specific components
│   ├── chat/           # Chat message and data panels
│   └── sidebar/        # Right sidebar components
├── context/            # React Context for state management
├── hooks/              # Custom React hooks
├── types/              # TypeScript type definitions
└── data/               # Mock data
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open your browser and navigate to:
```
http://localhost:5173
```

### Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Usage

### Quick Actions

Click any of the five quick action cards to simulate interaction:

- **Schedule Info**: View today's nursery schedule and procedures
- **Medication Guide**: Access medication information
- **Supply Check**: Check inventory levels
- **Patient Status**: View patient information
- **Emergency Protocols**: Access emergency procedures

### Chat Interface

The chat interface features:
- **Text Input Box**: Type and send custom messages to the AI assistant
- **Bot Messages**: AI responses with detailed information panels
- **User Messages**: Your queries displayed in blue bubbles
- **Schedule Data**: Shift details and key procedures
- **Emergency Protocols**: Color-coded protocol cards with severity levels
- **Auto-scroll**: Automatically scrolls to the latest message

Type messages like:
- "Show me my schedule"
- "What are the emergency protocols?"
- "I need help with procedures"

### Navigation

Use the left sidebar to navigate between sections:
- Dashboard (active by default)
- HR Information
- Nursing Procedures
- Inventory
- Patient Care
- Training & Guidance

## Customization

### Colors

The color scheme is defined in `tailwind.config.js`:

- Primary Blue: `#2563EB`
- Critical Red: `#FEE2E2` (background), `#DC2626` (text)
- Warning Yellow: `#FEF3C7` (background), `#D97706` (text)
- Success Green: `#D1FAE5` (background), `#059669` (text)
- Info Purple: `#EDE9FE` (background), `#7C3AED` (text)

### Mock Data

Edit `src/data/mockData.ts` to customize:
- Navigation items
- User information
- Alerts
- Schedule items
- Quick references
- Schedule and protocol data

## Components

### Key Components

- **DashboardLayout**: Main three-column layout
- **LeftSidebar**: Navigation and user profile
- **MainContent**: Header, quick actions, and chat display
- **RightSidebar**: Alerts, schedule, and quick references
- **InteractiveDisplay**: Chat message container
- **SchedulePanel**: Detailed schedule information display
- **ProtocolPanel**: Emergency protocol cards

## API Integration

The application currently uses mock data. To integrate with a real backend:

### 1. Review API Specification

See `API_SPECIFICATION.md` for complete API documentation including:
- All required endpoints
- Request/response formats
- Authentication requirements
- WebSocket support for real-time updates

### 2. Configure Environment

Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
```

Edit `.env`:
```env
VITE_API_BASE_URL=https://your-api.com/v1
VITE_WS_URL=wss://your-api.com/v1/ws
VITE_ENABLE_REAL_API=true
```

### 3. Implement API Service

See `src/services/api.example.ts` for a complete implementation example.

Replace mock data in:
- `src/context/AppContext.tsx` - Use API calls instead of mock data
- `src/hooks/useChatMessages.ts` - Call real AI endpoint

### Expected API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/user/profile` | GET | Get current user info |
| `/alerts/active` | GET | Get active alerts |
| `/schedule/today` | GET | Get today's schedule |
| `/schedule/shift` | GET | Get shift details |
| `/protocols/emergency` | GET | Get emergency protocols |
| `/assistant/chat` | POST | Send chat message to AI |
| `/references/quick` | GET | Get quick references |
| `/navigation/menu` | GET | Get navigation items |

## Future Enhancements

- Real AI integration (replace mock chat responses)
- Backend API integration for live data
- User authentication and authorization
- Real-time notifications via WebSocket
- Mobile responsive design
- Patient detail pages
- Medication tracking system
- Shift handoff features
- Push notifications
- Offline support

## License

MIT
