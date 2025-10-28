import React from 'react';
import { MedicationInventoryItem } from '../../types/api';
import { Package, AlertTriangle, CheckCircle, MapPin, Calendar } from 'lucide-react';

interface MedicationPanelProps {
  medications: MedicationInventoryItem[];
  query: string;
}

const MedicationPanel: React.FC<MedicationPanelProps> = ({ medications, query }) => {
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'in-stock':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 text-xs font-semibold rounded">
            <CheckCircle className="w-3 h-3" />
            In Stock
          </span>
        );
      case 'low-stock':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 bg-yellow-100 text-yellow-700 text-xs font-semibold rounded">
            <AlertTriangle className="w-3 h-3" />
            Low Stock
          </span>
        );
      case 'out-of-stock':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 bg-red-100 text-red-700 text-xs font-semibold rounded">
            <AlertTriangle className="w-3 h-3" />
            Out of Stock
          </span>
        );
      default:
        return null;
    }
  };

  const getStorageIcon = (requirement: string) => {
    const lower = requirement.toLowerCase();
    if (lower.includes('refrigerated') || lower.includes('frozen')) {
      return '❄️';
    } else if (lower.includes('room')) {
      return '🌡️';
    }
    return '📦';
  };

  return (
    <div className="bg-gray-50 border border-gray-200 rounded-xl p-5 max-w-3xl">
      {/* Header */}
      <div className="flex items-start gap-3 mb-4">
        <Package className="w-5 h-5 text-primary flex-shrink-0 mt-1" />
        <div className="flex-1">
          <h3 className="text-base font-semibold text-gray-900">
            Medication Inventory Results
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            Query: <span className="font-medium">{query}</span>
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Found {medications.length} batch{medications.length !== 1 ? 'es' : ''}
          </p>
        </div>
      </div>

      {/* Medication Items */}
      <div className="space-y-3">
        {medications.map((med) => (
          <div
            key={med.id}
            className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            {/* Header Row */}
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <h4 className="text-sm font-bold text-gray-900 flex items-center gap-2">
                  {med.drugName}
                  {med.controlledSubstance && (
                    <span className="text-xs px-2 py-0.5 bg-red-100 text-red-700 rounded font-semibold">
                      🔒 Controlled
                    </span>
                  )}
                </h4>
                <p className="text-xs text-gray-500 mt-1">
                  Batch: {med.batchNumber} | NDC: {med.ndc}
                </p>
              </div>
              {getStatusBadge(med.status)}
            </div>

            {/* Details Grid */}
            <div className="grid grid-cols-2 gap-3 mb-3">
              <div>
                <p className="text-xs text-gray-500 mb-0.5">Current Stock</p>
                <p className="text-sm font-semibold text-gray-900">
                  {med.quantity.toLocaleString()} units
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-0.5">Reorder Level</p>
                <p className="text-sm font-semibold text-gray-900">
                  {med.reorderLevel.toLocaleString()} units
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-0.5">Supplier</p>
                <p className="text-sm font-medium text-gray-700">
                  {med.supplier}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-0.5">Unit Price</p>
                <p className="text-sm font-medium text-gray-700">
                  €{med.unitPrice.toFixed(2)}
                </p>
              </div>
            </div>

            {/* Additional Info */}
            <div className="flex flex-wrap gap-3 text-xs text-gray-600 pt-3 border-t border-gray-100">
              <div className="flex items-center gap-1">
                <MapPin className="w-3 h-3" />
                <span>Location: {med.location}</span>
              </div>
              <div className="flex items-center gap-1">
                <span>{getStorageIcon(med.storageRequirement)}</span>
                <span>{med.storageRequirement}</span>
              </div>
              <div className="flex items-center gap-1">
                <Calendar className="w-3 h-3" />
                <span>Expires: {new Date(med.expiryDate).toLocaleDateString()}</span>
              </div>
              <div className="flex items-center gap-1">
                <span>Updated: {new Date(med.lastUpdated).toLocaleDateString()}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MedicationPanel;
