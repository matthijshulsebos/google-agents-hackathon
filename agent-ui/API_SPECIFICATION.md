# MedAssist Nursing Assistant - API Specification

This document describes the expected API endpoints and response bodies needed to wire up the MedAssist Nursing Assistant application with a real backend.

## Base URL
```
https://api.medassist.com/v1
```

## Authentication
All API requests should include an authentication token in the header:
```
Authorization: Bearer {token}
```

---

## Endpoints

### 1. Get Current User Profile

**Endpoint:** `GET /user/profile`

**Description:** Retrieve the currently logged-in user's profile information.

**Response:**
```json
{
  "name": "Sarah Johnson",
  "title": "RN, ICU Department",
  "department": "ICU",
  "avatar": "https://cdn.medassist.com/avatars/sarah-johnson.jpg"
}
```

**TypeScript Type:** `User`

---

### 2. Get Active Alerts

**Endpoint:** `GET /alerts/active`

**Description:** Retrieve all active alerts for the current user.

**Response:**
```json
{
  "alerts": [
    {
      "id": "alert-001",
      "title": "Baby A - Vitals Alert",
      "description": "Heart rate elevated - Check in 15 min",
      "severity": "critical",
      "action": "Check in 15 min"
    },
    {
      "id": "alert-002",
      "title": "Medication Due",
      "description": "Baby C - Antibiotics at 3:00 PM",
      "severity": "warning"
    }
  ]
}
```

**Query Parameters:**
- `severity` (optional): Filter by severity (`critical`, `warning`, `info`)

**TypeScript Type:** `Alert[]`

**Severity Levels:**
- `critical` - Urgent, requires immediate attention
- `warning` - Important, requires attention soon
- `info` - Informational

---

### 3. Get Today's Schedule

**Endpoint:** `GET /schedule/today`

**Description:** Retrieve the user's schedule for today, including upcoming tasks.

**Response:**
```json
{
  "schedule": [
    {
      "id": "schedule-001",
      "title": "Next Feeding Round",
      "time": "3:00 PM",
      "icon": "Milk",
      "iconColor": "text-blue-600",
      "description": "All patients"
    },
    {
      "id": "schedule-002",
      "title": "Vitals Check",
      "time": "4:00 PM",
      "icon": "Heart",
      "iconColor": "text-purple-600",
      "description": "Critical patients"
    },
    {
      "id": "schedule-003",
      "title": "Shift Change",
      "time": "7:00 PM",
      "icon": "ArrowRightLeft",
      "iconColor": "text-green-600",
      "description": "Report handoff"
    }
  ]
}
```

**TypeScript Type:** `ScheduleItem[]`

**Icon Options:**
- `Milk`, `Heart`, `ArrowRightLeft`, `Calendar`, `Clock`, `Activity`, `Baby`, etc. (Lucide React icons)

**Color Classes (Tailwind):**
- `text-blue-600`, `text-purple-600`, `text-green-600`, `text-orange-600`, `text-red-600`

---

### 4. Get Shift Details

**Endpoint:** `GET /schedule/shift`

**Description:** Get detailed information about the current or next shift.

**Query Parameters:**
- `date` (optional): ISO 8601 date string (defaults to today)

**Response:**
```json
{
  "date": "December 27, 2024",
  "shiftTime": "7:00 AM - 7:00 PM",
  "shiftDuration": "Day Shift - 12 hours",
  "assignedUnit": "NICU",
  "unitDescription": "Newborn Intensive Care",
  "patients": {
    "total": 6,
    "critical": 2,
    "stable": 4
  },
  "procedures": [
    {
      "id": "proc-001",
      "title": "Feeding Schedule",
      "description": "Every 3 hours: 6 AM, 9 AM, 12 PM, 3 PM, 6 PM",
      "color": "text-green-700",
      "bgColor": "bg-green-50",
      "icon": "Clock"
    },
    {
      "id": "proc-002",
      "title": "Vital Signs Monitoring",
      "description": "Every 2 hours for critical patients, every 4 hours for stable",
      "color": "text-purple-700",
      "bgColor": "bg-purple-50",
      "icon": "Activity"
    },
    {
      "id": "proc-003",
      "title": "Developmental Care",
      "description": "Kangaroo care sessions at 10 AM and 2 PM",
      "color": "text-orange-700",
      "bgColor": "bg-orange-50",
      "icon": "Baby"
    }
  ]
}
```

**TypeScript Type:** `ScheduleData`

---

### 5. Get Emergency Protocols

**Endpoint:** `GET /protocols/emergency`

**Description:** Retrieve emergency protocols for the user's assigned unit.

**Query Parameters:**
- `unit` (optional): Filter by unit (e.g., "NICU", "ICU")
- `severity` (optional): Filter by severity (`high`, `medium`, `low`)

**Response:**
```json
{
  "title": "NICU Emergency Protocols",
  "protocols": [
    {
      "id": "protocol-001",
      "title": "Code Blue - Infant Cardiac Arrest",
      "description": "1. Call 2222 immediately 2. Begin CPR 3. Prepare resuscitation equipment 4. Notify attending physician",
      "severity": "high",
      "bgColor": "bg-red-50",
      "borderColor": "border-red-300"
    },
    {
      "id": "protocol-002",
      "title": "Respiratory Distress",
      "description": "Check oxygen saturation, adjust ventilator settings, notify respiratory therapist",
      "severity": "medium",
      "bgColor": "bg-yellow-50",
      "borderColor": "border-yellow-300"
    },
    {
      "id": "protocol-003",
      "title": "Equipment Malfunction",
      "description": "Switch to backup equipment, document incident, notify biomedical engineering",
      "severity": "low",
      "bgColor": "bg-orange-50",
      "borderColor": "border-orange-300"
    }
  ]
}
```

**TypeScript Type:** `ProtocolData`

**Severity Mapping:**
- `high`: Red colors (`bg-red-50`, `border-red-300`)
- `medium`: Yellow colors (`bg-yellow-50`, `border-yellow-300`)
- `low`: Orange colors (`bg-orange-50`, `border-orange-300`)

---

### 6. Chat/AI Assistant

**Endpoint:** `POST /assistant/chat`

**Description:** Send a message to the AI assistant and receive a response.

**Request Body:**
```json
{
  "message": "Show me my schedule for today",
  "conversationId": "conv-12345",
  "context": {
    "userId": "user-001",
    "department": "ICU",
    "unit": "NICU"
  }
}
```

**Response:**
```json
{
  "id": "msg-12345",
  "type": "bot",
  "content": "Today's Nursery Schedule - December 27, 2024",
  "timestamp": "2024-12-27T14:30:00Z",
  "scheduleData": {
    "date": "December 27, 2024",
    "shiftTime": "7:00 AM - 7:00 PM",
    "shiftDuration": "Day Shift - 12 hours",
    "assignedUnit": "NICU",
    "unitDescription": "Newborn Intensive Care",
    "patients": {
      "total": 6,
      "critical": 2,
      "stable": 4
    },
    "procedures": [...]
  },
  "protocolData": null
}
```

**TypeScript Type:** `ChatMessage`

**Response Variants:**

1. **Text-only response:**
```json
{
  "id": "msg-12346",
  "type": "bot",
  "content": "I can help you with schedule information, nursing procedures, emergency protocols, and patient status. What would you like to know?",
  "timestamp": "2024-12-27T14:30:05Z"
}
```

2. **Schedule response:**
```json
{
  "id": "msg-12347",
  "type": "bot",
  "content": "Today's Nursery Schedule - December 27, 2024",
  "timestamp": "2024-12-27T14:30:10Z",
  "scheduleData": { ... }
}
```

3. **Protocol response:**
```json
{
  "id": "msg-12348",
  "type": "bot",
  "content": "NICU Emergency Protocols",
  "timestamp": "2024-12-27T14:30:15Z",
  "protocolData": { ... }
}
```

---

### 7. Get Quick References

**Endpoint:** `GET /references/quick`

**Description:** Retrieve quick reference links/resources for the user.

**Response:**
```json
{
  "references": [
    {
      "id": "ref-001",
      "title": "Normal Vital Ranges",
      "icon": "Thermometer",
      "iconColor": "text-red-600",
      "url": "/references/vital-ranges"
    },
    {
      "id": "ref-002",
      "title": "Dosage Calculator",
      "icon": "Calculator",
      "iconColor": "text-blue-600",
      "url": "/tools/dosage-calculator"
    },
    {
      "id": "ref-003",
      "title": "Emergency Numbers",
      "icon": "Phone",
      "iconColor": "text-green-600",
      "url": "/references/emergency-contacts"
    }
  ]
}
```

**TypeScript Type:** `Reference[]`

---

### 8. Get Navigation Items

**Endpoint:** `GET /navigation/menu`

**Description:** Retrieve navigation menu items based on user permissions.

**Response:**
```json
{
  "items": [
    {
      "id": "dashboard",
      "label": "Dashboard",
      "icon": "LayoutDashboard",
      "path": "/dashboard"
    },
    {
      "id": "hr",
      "label": "HR Information",
      "icon": "Users",
      "path": "/hr"
    },
    {
      "id": "procedures",
      "label": "Nursing Procedures",
      "icon": "BookOpen",
      "path": "/procedures"
    },
    {
      "id": "inventory",
      "label": "Inventory",
      "icon": "Package",
      "path": "/inventory"
    },
    {
      "id": "patient-care",
      "label": "Patient Care",
      "icon": "Heart",
      "path": "/patient-care"
    },
    {
      "id": "training",
      "label": "Training & Guidance",
      "icon": "GraduationCap",
      "path": "/training"
    }
  ]
}
```

**TypeScript Type:** `NavItem[]`

---

## Error Responses

All endpoints should return consistent error responses:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {}
  }
}
```

**HTTP Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

---

## WebSocket Support (Optional)

For real-time updates (alerts, schedule changes), the application can connect to:

**WebSocket URL:** `wss://api.medassist.com/v1/ws`

**Message Format:**
```json
{
  "type": "ALERT_UPDATE",
  "data": {
    "id": "alert-new-001",
    "title": "New Alert",
    "description": "Alert description",
    "severity": "critical"
  }
}
```

**Event Types:**
- `ALERT_UPDATE` - New or updated alert
- `SCHEDULE_UPDATE` - Schedule change
- `MESSAGE_RECEIVED` - New chat message

---

## Integration Example

```typescript
// Example API service
import { User, Alert, ScheduleItem, ChatMessage } from './types';

const API_BASE_URL = 'https://api.medassist.com/v1';

export const apiService = {
  async getCurrentUser(): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/user/profile`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.json();
  },

  async getActiveAlerts(): Promise<Alert[]> {
    const response = await fetch(`${API_BASE_URL}/alerts/active`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    const data = await response.json();
    return data.alerts;
  },

  async getTodaySchedule(): Promise<ScheduleItem[]> {
    const response = await fetch(`${API_BASE_URL}/schedule/today`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    const data = await response.json();
    return data.schedule;
  },

  async sendChatMessage(message: string): Promise<ChatMessage> {
    const response = await fetch(`${API_BASE_URL}/assistant/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({ message })
    });
    return response.json();
  }
};
```

---

## Notes

1. **Icons**: All icon names reference Lucide React icons. The backend should return valid icon names.

2. **Colors**: Color classes are Tailwind CSS utilities. The backend should return valid Tailwind color classes or the frontend can map severity levels to colors.

3. **Timestamps**: All timestamps should be in ISO 8601 format (e.g., `2024-12-27T14:30:00Z`).

4. **Pagination**: For endpoints that may return large datasets, implement pagination:
   ```
   ?page=1&limit=20
   ```

5. **Filtering**: Support filtering on relevant endpoints (alerts, schedules, protocols).

6. **Caching**: Implement appropriate caching headers for static data (navigation, references).

7. **Rate Limiting**: Implement rate limiting on the chat endpoint to prevent abuse.
