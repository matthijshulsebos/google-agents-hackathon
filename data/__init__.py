"""
Data module for hospital multi-agent system
Contains patient records and other data structures
"""
from .patient_data import (
    get_patient_details,
    get_all_patients,
    get_patient_count,
    PATIENTS
)

__all__ = [
    'get_patient_details',
    'get_all_patients',
    'get_patient_count',
    'PATIENTS'
]
