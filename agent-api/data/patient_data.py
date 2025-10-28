"""
Patient Data Module
Contains patient records for research agent demo
"""
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Patient database (hardcoded for demo purposes)
PATIENTS = {
    "juan de marco": {
        "name": "Juan de Marco",
        "age": 65,
        "date_of_birth": "1960-03-15",
        "medical_record_number": "MRN-789456",
        "last_audit_at": "2024-06-15",  # Over 6 months ago - overdue!
        "scheduled_medications_today": [
            {
                "medication": "Oxycodone",
                "strength": "5mg",
                "scheduled_time": "09:00 AM",
                "route": "Oral",
                "reason": "Post-surgical pain management"
            },
            {
                "medication": "Metformin",
                "strength": "500mg",
                "scheduled_time": "08:00 AM, 08:00 PM",
                "route": "Oral",
                "reason": "Type 2 Diabetes"
            },
            {
                "medication": "Lisinopril",
                "strength": "10mg",
                "scheduled_time": "08:00 AM",
                "route": "Oral",
                "reason": "Hypertension"
            }
        ],
        "medical_history": [
            "Type 2 Diabetes (diagnosed 2015)",
            "Hypertension (diagnosed 2018)",
            "Total knee replacement surgery (January 20, 2025)"
        ],
        "allergies": ["Penicillin (rash)"],
        "current_location": "Room 302, Orthopedic Ward",
        "attending_physician": "Dr. Sarah Thompson"
    },
    "maria silva": {
        "name": "Maria Silva",
        "age": 45,
        "date_of_birth": "1980-07-22",
        "medical_record_number": "MRN-456123",
        "last_audit_at": "2025-01-10",  # Recent - compliant
        "scheduled_medications_today": [
            {
                "medication": "Ibuprofen",
                "strength": "400mg",
                "scheduled_time": "10:00 AM, 06:00 PM",
                "route": "Oral",
                "reason": "Chronic back pain"
            },
            {
                "medication": "Omeprazole",
                "strength": "20mg",
                "scheduled_time": "08:00 AM",
                "route": "Oral",
                "reason": "GERD"
            }
        ],
        "medical_history": [
            "Chronic lower back pain (diagnosed 2019)",
            "GERD (diagnosed 2020)"
        ],
        "allergies": ["None"],
        "current_location": "Room 215, General Medicine",
        "attending_physician": "Dr. Michael Chen"
    },
    "robert johnson": {
        "name": "Robert Johnson",
        "age": 72,
        "date_of_birth": "1953-11-08",
        "medical_record_number": "MRN-321654",
        "last_audit_at": "2024-12-20",  # Recent - compliant
        "scheduled_medications_today": [
            {
                "medication": "Morphine Sulfate",
                "strength": "10mg",
                "scheduled_time": "08:00 AM, 02:00 PM, 08:00 PM",
                "route": "Injectable",
                "reason": "Cancer pain management"
            },
            {
                "medication": "Warfarin",
                "strength": "5mg",
                "scheduled_time": "06:00 PM",
                "route": "Oral",
                "reason": "Atrial fibrillation"
            }
        ],
        "medical_history": [
            "Stage IV lung cancer (diagnosed 2024)",
            "Atrial fibrillation (diagnosed 2021)",
            "History of deep vein thrombosis"
        ],
        "allergies": ["Sulfa drugs (severe reaction)"],
        "current_location": "Room 410, Oncology",
        "attending_physician": "Dr. Jennifer Lee"
    },
    "emily zhang": {
        "name": "Emily Zhang",
        "age": 28,
        "date_of_birth": "1997-05-12",
        "medical_record_number": "MRN-892341",
        "last_audit_at": "2025-01-22",  # Recent - compliant
        "scheduled_medications_today": [
            {
                "medication": "Insulin Aspart",
                "strength": "100 units/mL",
                "scheduled_time": "07:30 AM, 12:30 PM, 06:30 PM",
                "route": "Subcutaneous",
                "reason": "Type 1 Diabetes"
            },
            {
                "medication": "Levothyroxine",
                "strength": "75mcg",
                "scheduled_time": "07:00 AM",
                "route": "Oral",
                "reason": "Hypothyroidism"
            }
        ],
        "medical_history": [
            "Type 1 Diabetes (diagnosed 2005)",
            "Hypothyroidism (diagnosed 2020)",
            "Appendectomy (2015)"
        ],
        "allergies": ["Latex (contact dermatitis)"],
        "current_location": "Room 118, Endocrinology",
        "attending_physician": "Dr. Aisha Patel"
    },
    "david martinez": {
        "name": "David Martinez",
        "age": 58,
        "date_of_birth": "1967-09-03",
        "medical_record_number": "MRN-567890",
        "last_audit_at": "2024-05-20",  # Over 6 months ago - overdue!
        "scheduled_medications_today": [
            {
                "medication": "Hydrocodone",
                "strength": "10mg",
                "scheduled_time": "08:00 AM, 08:00 PM",
                "route": "Oral",
                "reason": "Chronic pain from spinal stenosis"
            },
            {
                "medication": "Gabapentin",
                "strength": "300mg",
                "scheduled_time": "08:00 AM, 02:00 PM, 08:00 PM",
                "route": "Oral",
                "reason": "Neuropathic pain"
            },
            {
                "medication": "Atorvastatin",
                "strength": "20mg",
                "scheduled_time": "08:00 PM",
                "route": "Oral",
                "reason": "High cholesterol"
            }
        ],
        "medical_history": [
            "Lumbar spinal stenosis (diagnosed 2018)",
            "Neuropathic pain (diagnosed 2019)",
            "Hyperlipidemia (diagnosed 2016)",
            "Hypertension (diagnosed 2014)"
        ],
        "allergies": ["Codeine (nausea, vomiting)"],
        "current_location": "Room 225, Pain Management",
        "attending_physician": "Dr. Robert Kim"
    },
    "sarah o'connor": {
        "name": "Sarah O'Connor",
        "age": 39,
        "date_of_birth": "1986-11-28",
        "medical_record_number": "MRN-234567",
        "last_audit_at": "2025-01-15",  # Recent - compliant
        "scheduled_medications_today": [
            {
                "medication": "Sertraline",
                "strength": "100mg",
                "scheduled_time": "08:00 AM",
                "route": "Oral",
                "reason": "Depression"
            },
            {
                "medication": "Lorazepam",
                "strength": "1mg",
                "scheduled_time": "08:00 AM, 08:00 PM",
                "route": "Oral",
                "reason": "Anxiety disorder"
            },
            {
                "medication": "Amlodipine",
                "strength": "5mg",
                "scheduled_time": "08:00 AM",
                "route": "Oral",
                "reason": "Hypertension"
            }
        ],
        "medical_history": [
            "Major depressive disorder (diagnosed 2018)",
            "Generalized anxiety disorder (diagnosed 2017)",
            "Hypertension (diagnosed 2022)"
        ],
        "allergies": ["None"],
        "current_location": "Room 305, Psychiatric Ward",
        "attending_physician": "Dr. Lisa Wang"
    },
    "thomas anderson": {
        "name": "Thomas Anderson",
        "age": 81,
        "date_of_birth": "1944-02-14",
        "medical_record_number": "MRN-678901",
        "last_audit_at": "2024-07-30",  # Over 6 months ago - overdue!
        "scheduled_medications_today": [
            {
                "medication": "Fentanyl Patch",
                "strength": "25mcg/hour",
                "scheduled_time": "Change every 72 hours",
                "route": "Transdermal",
                "reason": "Severe osteoarthritis pain"
            },
            {
                "medication": "Donepezil",
                "strength": "10mg",
                "scheduled_time": "08:00 PM",
                "route": "Oral",
                "reason": "Alzheimer's disease"
            },
            {
                "medication": "Metoprolol",
                "strength": "50mg",
                "scheduled_time": "08:00 AM, 08:00 PM",
                "route": "Oral",
                "reason": "Atrial fibrillation"
            },
            {
                "medication": "Furosemide",
                "strength": "40mg",
                "scheduled_time": "08:00 AM",
                "route": "Oral",
                "reason": "Congestive heart failure"
            }
        ],
        "medical_history": [
            "Alzheimer's disease (diagnosed 2020)",
            "Severe osteoarthritis (diagnosed 2015)",
            "Atrial fibrillation (diagnosed 2018)",
            "Congestive heart failure (diagnosed 2019)",
            "Total hip replacement (2016)"
        ],
        "allergies": ["Aspirin (gastrointestinal bleeding)"],
        "current_location": "Room 412, Geriatric Care",
        "attending_physician": "Dr. Margaret Sullivan"
    },
    "lisa rodriguez": {
        "name": "Lisa Rodriguez",
        "age": 52,
        "date_of_birth": "1973-04-19",
        "medical_record_number": "MRN-345678",
        "last_audit_at": "2025-01-05",  # Recent - compliant
        "scheduled_medications_today": [
            {
                "medication": "Prednisone",
                "strength": "20mg",
                "scheduled_time": "08:00 AM",
                "route": "Oral",
                "reason": "Rheumatoid arthritis"
            },
            {
                "medication": "Methotrexate",
                "strength": "15mg",
                "scheduled_time": "Weekly - Sundays",
                "route": "Oral",
                "reason": "Rheumatoid arthritis"
            },
            {
                "medication": "Tramadol",
                "strength": "50mg",
                "scheduled_time": "As needed (PRN) for pain",
                "route": "Oral",
                "reason": "Breakthrough pain"
            }
        ],
        "medical_history": [
            "Rheumatoid arthritis (diagnosed 2010)",
            "Osteoporosis (diagnosed 2021)",
            "Hypertension (diagnosed 2019)"
        ],
        "allergies": ["Iodine contrast (anaphylaxis)"],
        "current_location": "Room 208, Rheumatology",
        "attending_physician": "Dr. Carlos Mendez"
    }
}


def get_patient_details(patient_name: str) -> Dict[str, Any]:
    """
    Get patient details by name

    Args:
        patient_name: Patient name (case-insensitive)

    Returns:
        Dict with patient information or error
    """
    # Normalize patient name for lookup
    normalized_name = patient_name.lower().strip()

    if normalized_name in PATIENTS:
        patient_data = PATIENTS[normalized_name]
        logger.info(f"Found patient: {patient_data['name']}, age {patient_data['age']}, last audit: {patient_data['last_audit_at']}")
        return patient_data
    else:
        available_patients = ', '.join([p['name'] for p in PATIENTS.values()])
        logger.warning(f"Patient '{patient_name}' not found")
        return {
            "error": True,
            "message": f"Patient '{patient_name}' not found in system. Available patients: {available_patients}"
        }


def get_all_patients() -> Dict[str, Dict[str, Any]]:
    """
    Get all patient records

    Returns:
        Dict of all patients
    """
    return PATIENTS


def get_patient_count() -> int:
    """
    Get total number of patients in database

    Returns:
        Number of patients
    """
    return len(PATIENTS)
