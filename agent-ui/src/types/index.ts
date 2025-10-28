export type NavItem = {
  id: string;
  label: string;
  icon: string;
  path: string;
};

export type User = {
  name: string;
  title: string;
  department: string;
  avatar: string;
};

export type QuickAction = {
  id: string;
  label: string;
  icon: string;
  bgColor: string;
  iconColor: string;
};

export type AlertSeverity = 'critical' | 'warning' | 'info';

export type Alert = {
  id: string;
  title: string;
  description: string;
  severity: AlertSeverity;
  action?: string;
};

export type ScheduleItem = {
  id: string;
  title: string;
  time: string;
  icon: string;
  iconColor: string;
  description?: string;
};

export type Reference = {
  id: string;
  title: string;
  icon: string;
  iconColor: string;
};

export type MessageType = 'bot' | 'user';

export type ProcedureItem = {
  id: string;
  title: string;
  description: string;
  color: string;
  bgColor: string;
  icon: string;
};

export type ProtocolItem = {
  id: string;
  title: string;
  description: string;
  severity: 'high' | 'medium' | 'low';
  bgColor: string;
  borderColor: string;
};

export type ScheduleData = {
  date: string;
  shiftTime: string;
  shiftDuration: string;
  assignedUnit: string;
  unitDescription: string;
  patients: {
    total: number;
    critical: number;
    stable: number;
  };
  procedures: ProcedureItem[];
};

export type ProtocolData = {
  title: string;
  protocols: ProtocolItem[];
};

export type ChatMessage = {
  id: string;
  type: MessageType;
  content: string;
  contentSummary?: string;
  contentDetailed?: string;
  timestamp: Date;
  scheduleData?: ScheduleData;
  protocolData?: ProtocolData;
  medicationData?: import('./api').MedicationInventoryItem[];
};
