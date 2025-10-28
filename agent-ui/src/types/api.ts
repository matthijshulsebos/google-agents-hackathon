/**
 * API Response Types for Google Agents Integration
 */

export interface MedicationDocument {
  id: string;
  name: string;
  data: {
    supplier: string;
    quantity: string;
    storage_requirement: string;
    item_id: string;
    unit_price_eur: string;
    drug_name: string;
    last_audit_date: string;
    batch_number: string;
    expiry_date: string;
    total_cost_eur: string;
    controlled_substance: string;
    ndc: string;
    reorder_level: string;
    location: string;
  };
}

export interface GroundingMetadata {
  id: string;
  document: MedicationDocument;
}

export interface RoutingInfo {
  category: string;
  confidence: string;
  method: string;
  raw_response?: string;
  user_role?: string;
}

export interface AgentAPIResponse {
  conversation_id: string;
  query: string;
  answer: string;
  answer_summary?: string;
  answer_detailed?: string;
  agent: string;
  language: string;
  total_results: number;
  sources_count: number;
  grounding_metadata: GroundingMetadata[];
  routing_info: RoutingInfo;
  timestamp: string;
}

// Parsed medication inventory item
export interface MedicationInventoryItem {
  id: string;
  drugName: string;
  strength: string;
  quantity: number;
  status: 'in-stock' | 'low-stock' | 'out-of-stock';
  reorderLevel: number;
  batchNumber: string;
  expiryDate: string;
  location: string;
  storageRequirement: string;
  controlledSubstance: boolean;
  lastUpdated: string;
  supplier: string;
  unitPrice: number;
  ndc: string;
}
