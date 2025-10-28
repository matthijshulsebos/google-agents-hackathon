/**
 * API Service Example
 *
 * This file demonstrates how to integrate the MedAssist application with a real backend API.
 * Replace the mock data in AppContext and useChatMessages hook with these API calls.
 */

import {
  User,
  Alert,
  ScheduleItem,
  Reference,
  NavItem,
  ScheduleData,
  ProtocolData,
  ChatMessage
} from '../types';

const API_BASE_URL = process.env.VITE_API_BASE_URL || 'https://api.medassist.com/v1';

// Helper function to get auth token
const getAuthToken = (): string => {
  // Replace with your actual auth token retrieval logic
  return localStorage.getItem('authToken') || '';
};

// Helper function for API calls
const apiCall = async <T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> => {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getAuthToken()}`,
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error?.message || 'API request failed');
  }

  return response.json();
};

// API Service
export const apiService = {
  // User
  async getCurrentUser(): Promise<User> {
    return apiCall<User>('/user/profile');
  },

  // Alerts
  async getActiveAlerts(severity?: 'critical' | 'warning' | 'info'): Promise<Alert[]> {
    const params = severity ? `?severity=${severity}` : '';
    const data = await apiCall<{ alerts: Alert[] }>(`/alerts/active${params}`);
    return data.alerts;
  },

  // Schedule
  async getTodaySchedule(): Promise<ScheduleItem[]> {
    const data = await apiCall<{ schedule: ScheduleItem[] }>('/schedule/today');
    return data.schedule;
  },

  async getShiftDetails(date?: string): Promise<ScheduleData> {
    const params = date ? `?date=${date}` : '';
    return apiCall<ScheduleData>(`/schedule/shift${params}`);
  },

  // Protocols
  async getEmergencyProtocols(
    unit?: string,
    severity?: 'high' | 'medium' | 'low'
  ): Promise<ProtocolData> {
    const params = new URLSearchParams();
    if (unit) params.append('unit', unit);
    if (severity) params.append('severity', severity);
    const queryString = params.toString() ? `?${params.toString()}` : '';
    return apiCall<ProtocolData>(`/protocols/emergency${queryString}`);
  },

  // Chat/Assistant
  async sendChatMessage(
    message: string,
    conversationId?: string,
    context?: {
      userId?: string;
      department?: string;
      unit?: string;
    }
  ): Promise<ChatMessage> {
    return apiCall<ChatMessage>('/assistant/chat', {
      method: 'POST',
      body: JSON.stringify({
        message,
        conversationId,
        context,
      }),
    });
  },

  // Quick References
  async getQuickReferences(): Promise<Reference[]> {
    const data = await apiCall<{ references: Reference[] }>('/references/quick');
    return data.references;
  },

  // Navigation
  async getNavigationItems(): Promise<NavItem[]> {
    const data = await apiCall<{ items: NavItem[] }>('/navigation/menu');
    return data.items;
  },
};

// WebSocket Service for real-time updates (optional)
export class WebSocketService {
  private ws: WebSocket | null = null;
  private listeners: Map<string, Set<Function>> = new Map();

  connect() {
    const wsUrl = process.env.VITE_WS_URL || 'wss://api.medassist.com/v1/ws';
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      // Send authentication
      this.ws?.send(JSON.stringify({
        type: 'AUTH',
        token: getAuthToken(),
      }));
    };

    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        this.emit(message.type, message.data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      // Attempt to reconnect after 5 seconds
      setTimeout(() => this.connect(), 5000);
    };
  }

  disconnect() {
    this.ws?.close();
    this.ws = null;
  }

  on(eventType: string, callback: Function) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set());
    }
    this.listeners.get(eventType)?.add(callback);
  }

  off(eventType: string, callback: Function) {
    this.listeners.get(eventType)?.delete(callback);
  }

  private emit(eventType: string, data: any) {
    this.listeners.get(eventType)?.forEach(callback => callback(data));
  }
}

// Singleton instance
export const wsService = new WebSocketService();

// Example usage in a React component:
/*
import { useEffect, useState } from 'react';
import { apiService, wsService } from './services/api';
import { Alert } from './types';

function MyComponent() {
  const [alerts, setAlerts] = useState<Alert[]>([]);

  useEffect(() => {
    // Fetch initial data
    apiService.getActiveAlerts().then(setAlerts);

    // Connect to WebSocket for real-time updates
    wsService.connect();
    wsService.on('ALERT_UPDATE', (newAlert: Alert) => {
      setAlerts(prev => [...prev, newAlert]);
    });

    return () => {
      wsService.disconnect();
    };
  }, []);

  return (
    <div>
      {alerts.map(alert => (
        <div key={alert.id}>{alert.title}</div>
      ))}
    </div>
  );
}
*/
