/**
 * Google Agents API Service
 * Integration with the pharmacy/medication inventory system
 */

import { AgentAPIResponse, MedicationInventoryItem } from '../types/api';

const API_BASE_URL = import.meta.env.VITE_AGENT_API_URL || 'http://localhost:8000';

/**
 * Parse the agent API response and convert grounding metadata to medication items
 */
export function parseMedicationData(response: AgentAPIResponse): MedicationInventoryItem[] {
  return response.grounding_metadata.map((meta) => {
    const data = meta.document.data;
    const quantity = parseInt(data.quantity);
    const reorderLevel = parseInt(data.reorder_level);

    // Determine stock status
    let status: 'in-stock' | 'low-stock' | 'out-of-stock' = 'in-stock';
    if (quantity === 0) {
      status = 'out-of-stock';
    } else if (quantity <= reorderLevel) {
      status = 'low-stock';
    }

    return {
      id: meta.id,
      drugName: data.drug_name,
      strength: data.drug_name.match(/\d+mg/)?.[0] || '',
      quantity: quantity,
      status: status,
      reorderLevel: reorderLevel,
      batchNumber: data.batch_number,
      expiryDate: data.expiry_date,
      location: data.location,
      storageRequirement: data.storage_requirement,
      controlledSubstance: data.controlled_substance.toLowerCase() === 'yes',
      lastUpdated: data.last_audit_date,
      supplier: data.supplier,
      unitPrice: parseFloat(data.unit_price_eur),
      ndc: data.ndc,
    };
  });
}

/**
 * Send a query to the agent API
 *
 * First call: No conversation_id (will create new session)
 * Follow-up calls: Include conversation_id from previous response
 */
export async function queryAgent(
  message: string,
  conversationId?: string,
  userRole: string = 'employee'
): Promise<AgentAPIResponse> {
  // Build request body
  const requestBody: Record<string, string> = {
    query: message,
    user_role: userRole,
  };

  // Only include conversation_id if it exists (not first message)
  if (conversationId) {
    requestBody.conversation_id = conversationId;
  }

  const response = await fetch(`${API_BASE_URL}/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(requestBody),
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Send a research query to the agent API (uses multi-agent orchestration)
 * This endpoint performs deeper research with multiple tool calls
 *
 * First call: No conversation_id (will create new session)
 * Follow-up calls: Include conversation_id from previous response
 */
export async function researchAgent(
  message: string,
  conversationId?: string
): Promise<AgentAPIResponse> {
  // Build request body
  const requestBody: Record<string, string> = {
    query: message,
  };

  // Only include conversation_id if it exists (not first message)
  if (conversationId) {
    requestBody.conversation_id = conversationId;
  }

  const response = await fetch(`${API_BASE_URL}/research`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(requestBody),
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Check if the response contains medication/pharmacy data
 */
export function isMedicationResponse(response: AgentAPIResponse): boolean {
  return (
    response.agent === 'pharmacy' &&
    response.grounding_metadata &&
    response.grounding_metadata.length > 0
  );
}

/**
 * Example usage:
 *
 * // First message - no conversation_id
 * const response1 = await queryAgent("Do we have Oxycodone?");
 * const conversationId = response1.conversation_id;
 *
 * // Follow-up message - include conversation_id for context
 * const response2 = await queryAgent("Is it audited?", conversationId);
 *
 * if (isMedicationResponse(response1)) {
 *   const medications = parseMedicationData(response1);
 *   // Use medications in UI
 * }
 */
