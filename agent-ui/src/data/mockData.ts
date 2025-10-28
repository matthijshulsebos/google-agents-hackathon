import { NavItem, User, QuickAction, Alert, ScheduleItem, Reference, ScheduleData, ProtocolData } from '../types';

export const navItems: NavItem[] = [
  { id: 'dashboard', label: 'Dashboard', icon: 'LayoutDashboard', path: '/dashboard' },
  { id: 'hr', label: 'HR Information', icon: 'Users', path: '/hr' },
  { id: 'procedures', label: 'Nursing Procedures', icon: 'BookOpen', path: '/procedures' },
  { id: 'inventory', label: 'Inventory', icon: 'Package', path: '/inventory' },
  { id: 'patient-care', label: 'Patient Care', icon: 'Heart', path: '/patient-care' },
  { id: 'training', label: 'Training & Guidance', icon: 'GraduationCap', path: '/training' },
];

export const currentUser: User = {
  name: 'Sarah Johnson',
  title: 'RN, ICU Department',
  department: 'ICU',
  avatar: 'https://ui-avatars.com/api/?name=Sarah+Johnson&background=2563EB&color=fff',
};

export const quickActions: QuickAction[] = [
  { id: 'schedule', label: 'Schedule Info', icon: 'Calendar', bgColor: 'bg-blue-50', iconColor: 'text-blue-600' },
  { id: 'medication', label: 'Medication Guide', icon: 'Pill', bgColor: 'bg-green-50', iconColor: 'text-green-600' },
  { id: 'supply', label: 'Supply Check', icon: 'ClipboardList', bgColor: 'bg-purple-50', iconColor: 'text-purple-600' },
  { id: 'patient', label: 'Patient Status', icon: 'Activity', bgColor: 'bg-orange-50', iconColor: 'text-orange-600' },
  { id: 'emergency', label: 'Emergency Protocols', icon: 'AlertTriangle', bgColor: 'bg-red-50', iconColor: 'text-red-600' },
];

export const alerts: Alert[] = [
  {
    id: 'alert-1',
    title: 'Baby A - Vitals Alert',
    description: 'Heart rate elevated - Check in 15 min',
    severity: 'critical',
    action: 'Check in 15 min',
  },
  {
    id: 'alert-2',
    title: 'Medication Due',
    description: 'Baby C - Antibiotics at 3:00 PM',
    severity: 'warning',
  },
];

export const todaySchedule: ScheduleItem[] = [
  {
    id: 'schedule-1',
    title: 'Next Feeding Round',
    time: '3:00 PM',
    icon: 'Milk',
    iconColor: 'text-blue-600',
    description: 'All patients',
  },
  {
    id: 'schedule-2',
    title: 'Vitals Check',
    time: '4:00 PM',
    icon: 'Heart',
    iconColor: 'text-purple-600',
    description: 'Critical patients',
  },
  {
    id: 'schedule-3',
    title: 'Shift Change',
    time: '7:00 PM',
    icon: 'ArrowRightLeft',
    iconColor: 'text-green-600',
    description: 'Report handoff',
  },
];

export const quickReferences: Reference[] = [
  { id: 'ref-1', title: 'Normal Vital Ranges', icon: 'Thermometer', iconColor: 'text-red-600' },
  { id: 'ref-2', title: 'Dosage Calculator', icon: 'Calculator', iconColor: 'text-blue-600' },
  { id: 'ref-3', title: 'Emergency Numbers', icon: 'Phone', iconColor: 'text-green-600' },
];

export const scheduleDataMock: ScheduleData = {
  date: 'December 27, 2024',
  shiftTime: '7:00 AM - 7:00 PM',
  shiftDuration: 'Day Shift - 12 hours',
  assignedUnit: 'NICU',
  unitDescription: 'Newborn Intensive Care',
  patients: {
    total: 6,
    critical: 2,
    stable: 4,
  },
  procedures: [
    {
      id: 'proc-1',
      title: 'Feeding Schedule',
      description: 'Every 3 hours: 6 AM, 9 AM, 12 PM, 3 PM, 6 PM',
      color: 'text-green-700',
      bgColor: 'bg-green-50',
      icon: 'Clock',
    },
    {
      id: 'proc-2',
      title: 'Vital Signs Monitoring',
      description: 'Every 2 hours for critical patients, every 4 hours for stable',
      color: 'text-purple-700',
      bgColor: 'bg-purple-50',
      icon: 'Activity',
    },
    {
      id: 'proc-3',
      title: 'Developmental Care',
      description: 'Kangaroo care sessions at 10 AM and 2 PM',
      color: 'text-orange-700',
      bgColor: 'bg-orange-50',
      icon: 'Baby',
    },
  ],
};

export const protocolDataMock: ProtocolData = {
  title: 'NICU Emergency Protocols',
  protocols: [
    {
      id: 'protocol-1',
      title: 'Code Blue - Infant Cardiac Arrest',
      description: '1. Call 2222 immediately 2. Begin CPR 3. Prepare resuscitation equipment 4. Notify attending physician',
      severity: 'high',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-300',
    },
    {
      id: 'protocol-2',
      title: 'Respiratory Distress',
      description: 'Check oxygen saturation, adjust ventilator settings, notify respiratory therapist',
      severity: 'medium',
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-300',
    },
    {
      id: 'protocol-3',
      title: 'Equipment Malfunction',
      description: 'Switch to backup equipment, document incident, notify biomedical engineering',
      severity: 'low',
      bgColor: 'bg-orange-50',
      borderColor: 'border-orange-300',
    },
  ],
};
