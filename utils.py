import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import re

def format_confidence_score(score: float) -> str:
    """Format confidence score for display"""
    if score >= 0.9:
        return f"🟢 {score:.2f} (Very High)"
    elif score >= 0.7:
        return f"🟡 {score:.2f} (High)"
    elif score >= 0.5:
        return f"🟠 {score:.2f} (Medium)"
    else:
        return f"🔴 {score:.2f} (Low)"

def export_to_csv(results: List[Dict]) -> str:
    """Export mapping results to CSV format"""
    rows = []
    
    for result in results:
        patient_id = result['patient_id']
        
        for mapping in result['mappings']:
            row = {
                'Patient_ID': patient_id,
                'Original_Diagnosis': mapping['original_diagnosis'],
                'ICD10_Code': mapping['icd10_code'],
                'ICD10_Description': mapping['description'],
                'Confidence_Score': mapping['confidence'],
                'Justification': mapping['justification'],
                'Alternative_Codes': format_alternatives(mapping['alternatives'])
            }
            rows.append(row)
    
    df = pd.DataFrame(rows)
    return df.to_csv(index=False)

def format_alternatives(alternatives: List[Dict]) -> str:
    """Format alternative suggestions as string"""
    if not alternatives:
        return ""
    
    formatted = []
    for alt in alternatives:
        formatted.append(f"{alt['icd10_code']}: {alt['description']} (Score: {alt['confidence']:.2f})")
    
    return "; ".join(formatted)

def calculate_mapping_statistics(results: List[Dict]) -> Dict[str, Any]:
    """Calculate statistics for mapping results"""
    if not results:
        return {}
    
    total_mappings = sum(len(result['mappings']) for result in results)
    if total_mappings == 0:
        return {}
    
    # Confidence distribution
    confidences = []
    for result in results:
        for mapping in result['mappings']:
            confidences.append(mapping['confidence'])
    
    # ICD-10 code frequency
    codes = []
    for result in results:
        for mapping in result['mappings']:
            if mapping['icd10_code'] != 'UNKNOWN':
                codes.append(mapping['icd10_code'])
    
    stats = {
        'total_patients': len(results),
        'total_mappings': total_mappings,
        'average_confidence': np.mean(confidences) if confidences else 0,
        'high_confidence_count': sum(1 for c in confidences if c >= 0.7),
        'unknown_mappings': sum(1 for result in results 
                              for mapping in result['mappings'] 
                              if mapping['icd10_code'] == 'UNKNOWN'),
        'unique_codes': len(set(codes)),
        'confidence_distribution': {
            'very_high': sum(1 for c in confidences if c >= 0.9),
            'high': sum(1 for c in confidences if 0.7 <= c < 0.9),
            'medium': sum(1 for c in confidences if 0.5 <= c < 0.7),
            'low': sum(1 for c in confidences if c < 0.5)
        }
    }
    
    return stats

def validate_icd10_code(code: str) -> bool:
    """Validate ICD-10 code format"""
    if not code or code == 'UNKNOWN':
        return False
    
    # Basic ICD-10 format validation
    # Pattern: Letter followed by 2 digits, then optional decimal and more digits
    pattern = r'^[A-Z]\d{2}(\.\d{1,4})?$'
    return bool(re.match(pattern, code))

def clean_medical_text(text: str) -> str:
    """Clean medical text for better processing"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Standardize common abbreviations
    abbreviations = {
        'w/o': 'without',
        'w/': 'with',
        'pt': 'patient',
        'hx': 'history',
        'dx': 'diagnosis',
        'tx': 'treatment',
        'rx': 'prescription',
        'sx': 'surgery',
        'fx': 'fracture',
        'ca': 'cancer',
        'mi': 'myocardial infarction',
        'dm': 'diabetes mellitus',
        'htn': 'hypertension',
        'copd': 'chronic obstructive pulmonary disease',
        'chf': 'congestive heart failure',
        'cad': 'coronary artery disease',
        'ckd': 'chronic kidney disease',
        'esrd': 'end stage renal disease',
        'afib': 'atrial fibrillation',
        'dvt': 'deep vein thrombosis',
        'pe': 'pulmonary embolism',
        'uti': 'urinary tract infection',
        'uri': 'upper respiratory infection',
        'lri': 'lower respiratory infection',
        'gi': 'gastrointestinal',
        'gerd': 'gastroesophageal reflux disease',
        'ibs': 'irritable bowel syndrome',
        'crohn': 'crohn disease',
        'uc': 'ulcerative colitis',
        'ra': 'rheumatoid arthritis',
        'oa': 'osteoarthritis',
        'osteo': 'osteoporosis',
        'bph': 'benign prostatic hyperplasia',
        'pcos': 'polycystic ovary syndrome',
        'copd': 'chronic obstructive pulmonary disease',
        'asthma': 'asthma',
        'pneumonia': 'pneumonia',
        'bronchitis': 'bronchitis',
        'emphysema': 'emphysema'
    }
    
    # Replace abbreviations
    words = text.lower().split()
    for i, word in enumerate(words):
        if word in abbreviations:
            words[i] = abbreviations[word]
    
    return ' '.join(words)

def get_category_color(category: str) -> str:
    """Get color coding for different medical categories"""
    colors = {
        'Cardiovascular': '#FF6B6B',
        'Respiratory': '#4ECDC4',
        'Endocrine': '#45B7D1',
        'Genitourinary': '#96CEB4',
        'Mental': '#FFEAA7',
        'Infectious': '#DDA0DD',
        'Neoplasms': '#FFB6C1',
        'Blood': '#F0A500',
        'Digestive': '#98D8C8',
        'Skin': '#FFCCCB',
        'Injury': '#FFE4B5',
        'Factors': '#E6E6FA',
        'Symptoms': '#F5DEB3'
    }
    
    return colors.get(category, '#CCCCCC')

def format_medical_text(text: str, max_length: int = 100) -> str:
    """Format medical text for display"""
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    # Truncate at word boundary
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    if last_space > 0:
        truncated = truncated[:last_space]
    
    return truncated + "..."

def generate_mapping_report(results: List[Dict]) -> str:
    """Generate a text report of mapping results"""
    if not results:
        return "No mapping results to report."
    
    stats = calculate_mapping_statistics(results)
    
    report = f"""
ICD-10 Mapping Report
====================

Summary:
- Total Patients: {stats['total_patients']}
- Total Diagnoses Mapped: {stats['total_mappings']}
- Average Confidence Score: {stats['average_confidence']:.2f}
- High Confidence Mappings: {stats['high_confidence_count']} ({stats['high_confidence_count']/stats['total_mappings']*100:.1f}%)
- Unknown Mappings: {stats['unknown_mappings']} ({stats['unknown_mappings']/stats['total_mappings']*100:.1f}%)
- Unique ICD-10 Codes Used: {stats['unique_codes']}

Confidence Distribution:
- Very High (≥0.9): {stats['confidence_distribution']['very_high']}
- High (0.7-0.9): {stats['confidence_distribution']['high']}
- Medium (0.5-0.7): {stats['confidence_distribution']['medium']}
- Low (<0.5): {stats['confidence_distribution']['low']}

Detailed Results:
"""
    
    for result in results:
        report += f"\nPatient {result['patient_id']}:\n"
        for mapping in result['mappings']:
            report += f"  • {mapping['original_diagnosis']}\n"
            report += f"    → {mapping['icd10_code']}: {mapping['description']}\n"
            report += f"    Confidence: {mapping['confidence']:.2f}\n"
            if mapping['alternatives']:
                report += f"    Alternatives: {len(mapping['alternatives'])} found\n"
            report += "\n"
    
    return report
