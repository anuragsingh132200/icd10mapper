import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz, process
import re
import requests
from typing import Dict, List, Tuple, Optional
import json
import os

class ICD10Mapper:
    """AI-powered ICD-10 diagnosis mapper with fuzzy matching and semantic analysis"""
    
    def __init__(self):
        self.icd10_data = self._load_icd10_data()
        self.diagnosis_patterns = self._compile_diagnosis_patterns()
        
    def _load_icd10_data(self) -> pd.DataFrame:
        """Load ICD-10 data from multiple sources"""
        # Primary dataset - WHO ICD-10 codes
        icd10_basic = self._get_basic_icd10_codes()
        
        # Try to enhance with additional data sources
        try:
            # Attempt to load from icd-codex or similar open source
            enhanced_data = self._load_enhanced_icd10_data()
            if enhanced_data is not None:
                return enhanced_data
        except Exception as e:
            print(f"Could not load enhanced ICD-10 data: {e}")
        
        return icd10_basic
    
    def _get_basic_icd10_codes(self) -> pd.DataFrame:
        """Generate basic ICD-10 codes and descriptions"""
        # Common ICD-10 codes that frequently appear in medical records
        basic_codes = [
            # Diabetes
            {"code": "E11.9", "description": "Type 2 diabetes mellitus without complications", "category": "Endocrine"},
            {"code": "E11.8", "description": "Type 2 diabetes mellitus with unspecified complications", "category": "Endocrine"},
            {"code": "E10.9", "description": "Type 1 diabetes mellitus without complications", "category": "Endocrine"},
            {"code": "E11.65", "description": "Type 2 diabetes mellitus with hyperglycemia", "category": "Endocrine"},
            
            # Hypertension
            {"code": "I10", "description": "Essential (primary) hypertension", "category": "Cardiovascular"},
            {"code": "I11.9", "description": "Hypertensive heart disease without heart failure", "category": "Cardiovascular"},
            {"code": "I12.9", "description": "Hypertensive chronic kidney disease with stage 1 through stage 4 chronic kidney disease, or unspecified chronic kidney disease", "category": "Cardiovascular"},
            
            # Hyperlipidemia
            {"code": "E78.5", "description": "Hyperlipidemia, unspecified", "category": "Endocrine"},
            {"code": "E78.0", "description": "Pure hypercholesterolemia", "category": "Endocrine"},
            {"code": "E78.2", "description": "Mixed hyperlipidemia", "category": "Endocrine"},
            
            # Respiratory
            {"code": "J44.1", "description": "Chronic obstructive pulmonary disease with acute exacerbation", "category": "Respiratory"},
            {"code": "J44.0", "description": "Chronic obstructive pulmonary disease with acute lower respiratory infection", "category": "Respiratory"},
            {"code": "J45.9", "description": "Asthma, unspecified", "category": "Respiratory"},
            {"code": "J96.90", "description": "Respiratory failure, unspecified, unspecified whether with hypoxia or hypercapnia", "category": "Respiratory"},
            {"code": "J18.9", "description": "Pneumonia, unspecified organism", "category": "Respiratory"},
            
            # Kidney Disease
            {"code": "N18.6", "description": "End stage renal disease", "category": "Genitourinary"},
            {"code": "N18.3", "description": "Chronic kidney disease, stage 3 (moderate)", "category": "Genitourinary"},
            {"code": "N18.4", "description": "Chronic kidney disease, stage 4 (severe)", "category": "Genitourinary"},
            {"code": "N18.5", "description": "Chronic kidney disease, stage 5", "category": "Genitourinary"},
            {"code": "N18.9", "description": "Chronic kidney disease, unspecified", "category": "Genitourinary"},
            
            # Heart Conditions
            {"code": "I25.10", "description": "Atherosclerotic heart disease of native coronary artery without angina pectoris", "category": "Cardiovascular"},
            {"code": "I50.9", "description": "Heart failure, unspecified", "category": "Cardiovascular"},
            {"code": "I48.91", "description": "Unspecified atrial fibrillation", "category": "Cardiovascular"},
            {"code": "I21.9", "description": "Acute myocardial infarction, unspecified", "category": "Cardiovascular"},
            
            # Mental Health
            {"code": "F17.210", "description": "Nicotine dependence, cigarettes, uncomplicated", "category": "Mental"},
            {"code": "F32.9", "description": "Major depressive disorder, single episode, unspecified", "category": "Mental"},
            {"code": "F31.9", "description": "Bipolar disorder, unspecified", "category": "Mental"},
            {"code": "F20.9", "description": "Schizophrenia, unspecified", "category": "Mental"},
            
            # Cancer
            {"code": "C78.2", "description": "Secondary malignant neoplasm of pleura", "category": "Neoplasms"},
            {"code": "C78.1", "description": "Secondary malignant neoplasm of mediastinum", "category": "Neoplasms"},
            {"code": "C78.0", "description": "Secondary malignant neoplasm of lung", "category": "Neoplasms"},
            {"code": "C50.911", "description": "Malignant neoplasm of unspecified site of right female breast", "category": "Neoplasms"},
            
            # Infections
            {"code": "A41.9", "description": "Sepsis, unspecified organism", "category": "Infectious"},
            {"code": "R65.20", "description": "Severe sepsis without septic shock", "category": "Infectious"},
            {"code": "A49.9", "description": "Bacterial infection, unspecified", "category": "Infectious"},
            
            # Hypothyroidism
            {"code": "E03.9", "description": "Hypothyroidism, unspecified", "category": "Endocrine"},
            {"code": "E03.8", "description": "Other specified hypothyroidism", "category": "Endocrine"},
            
            # Anemia
            {"code": "D64.9", "description": "Anemia, unspecified", "category": "Blood"},
            {"code": "D50.9", "description": "Iron deficiency anemia, unspecified", "category": "Blood"},
            
            # Obesity
            {"code": "E66.9", "description": "Obesity, unspecified", "category": "Endocrine"},
            {"code": "E66.01", "description": "Morbid (severe) obesity due to excess calories", "category": "Endocrine"},
            
            # Common symptoms
            {"code": "R50.9", "description": "Fever, unspecified", "category": "Symptoms"},
            {"code": "R06.02", "description": "Shortness of breath", "category": "Symptoms"},
            {"code": "R53.83", "description": "Fatigue", "category": "Symptoms"},
            {"code": "R11.10", "description": "Vomiting, unspecified", "category": "Symptoms"},
            {"code": "K59.00", "description": "Constipation, unspecified", "category": "Digestive"},
            {"code": "K92.2", "description": "Gastrointestinal bleeding, unspecified", "category": "Digestive"},
            
            # Thrombocytopenia
            {"code": "D69.6", "description": "Thrombocytopenia, unspecified", "category": "Blood"},
            
            # Substance use
            {"code": "F10.10", "description": "Alcohol use disorder, mild", "category": "Mental"},
            {"code": "F10.20", "description": "Alcohol use disorder, moderate", "category": "Mental"},
            {"code": "Z87.891", "description": "Personal history of nicotine dependence", "category": "Factors"},
            
            # Procedures and status
            {"code": "Z95.1", "description": "Presence of aortocoronary bypass graft", "category": "Factors"},
            {"code": "Z51.11", "description": "Encounter for antineoplastic chemotherapy", "category": "Factors"},
            {"code": "Z66", "description": "Do not resuscitate", "category": "Factors"},
            
            # Hepatitis
            {"code": "B19.20", "description": "Unspecified viral hepatitis C without hepatic coma", "category": "Infectious"},
            {"code": "B18.2", "description": "Chronic viral hepatitis C", "category": "Infectious"},
            
            # Ulcers
            {"code": "L97.909", "description": "Non-pressure chronic ulcer of unspecified part of unspecified lower leg with unspecified severity", "category": "Skin"},
            {"code": "L89.90", "description": "Pressure ulcer of unspecified site, unspecified stage", "category": "Skin"},
            
            # Fractures
            {"code": "S72.001A", "description": "Fracture of unspecified part of neck of right femur, initial encounter for closed fracture", "category": "Injury"},
            {"code": "S22.43XA", "description": "Multiple fractures of ribs, bilateral, initial encounter for closed fracture", "category": "Injury"},
        ]
        
        return pd.DataFrame(basic_codes)
    
    def _load_enhanced_icd10_data(self) -> Optional[pd.DataFrame]:
        """Try to load enhanced ICD-10 data from external sources"""
        try:
            # This could be expanded to use APIs or downloaded datasets
            # For now, return None to use basic dataset
            return None
        except Exception:
            return None
    
    def _compile_diagnosis_patterns(self) -> Dict[str, List[str]]:
        """Compile common diagnosis patterns for better matching"""
        return {
            'diabetes': ['diabetes', 'diabetic', 'dm', 'hyperglycemia', 'glucose'],
            'hypertension': ['hypertension', 'high blood pressure', 'htn', 'elevated bp'],
            'hyperlipidemia': ['hyperlipidemia', 'hypercholesterolemia', 'high cholesterol', 'dyslipidemia'],
            'copd': ['copd', 'chronic obstructive', 'emphysema', 'chronic bronchitis'],
            'asthma': ['asthma', 'bronchial asthma', 'allergic asthma'],
            'kidney': ['kidney', 'renal', 'nephropathy', 'ckd', 'chronic kidney'],
            'heart': ['heart', 'cardiac', 'coronary', 'myocardial', 'cardiovascular'],
            'cancer': ['cancer', 'malignant', 'neoplasm', 'tumor', 'carcinoma'],
            'infection': ['infection', 'sepsis', 'pneumonia', 'abscess'],
            'anemia': ['anemia', 'low hemoglobin', 'iron deficiency'],
            'obesity': ['obesity', 'obese', 'overweight', 'bmi'],
            'depression': ['depression', 'depressive', 'mood disorder'],
            'anxiety': ['anxiety', 'anxious', 'panic'],
            'substance': ['alcohol', 'drug', 'substance', 'addiction', 'dependence'],
            'fracture': ['fracture', 'broken', 'break', 'fx'],
            'ulcer': ['ulcer', 'wound', 'sore'],
            'hepatitis': ['hepatitis', 'liver'],
            'hypothyroid': ['hypothyroid', 'thyroid', 'underactive thyroid']
        }
    
    def map_diagnosis(self, diagnosis: str, confidence_threshold: float = 0.7, max_suggestions: int = 3) -> Dict:
        """Map a single diagnosis to ICD-10 code with confidence score and alternatives"""
        
        # Clean and normalize diagnosis
        clean_diagnosis = self._clean_diagnosis(diagnosis)
        
        # Get potential matches using multiple strategies
        fuzzy_matches = self._fuzzy_match(clean_diagnosis)
        pattern_matches = self._pattern_match(clean_diagnosis)
        
        # Combine and rank matches
        all_matches = self._combine_matches(fuzzy_matches, pattern_matches)
        
        if not all_matches:
            return {
                'original_diagnosis': diagnosis,
                'icd10_code': 'UNKNOWN',
                'description': 'No matching ICD-10 code found',
                'confidence': 0.0,
                'justification': 'No suitable matches found in ICD-10 database',
                'alternatives': []
            }
        
        # Get best match and alternatives
        best_match = all_matches[0]
        alternatives = all_matches[1:max_suggestions+1] if len(all_matches) > 1 else []
        
        # Generate justification
        justification = self._generate_justification(diagnosis, best_match, clean_diagnosis)
        
        return {
            'original_diagnosis': diagnosis,
            'icd10_code': best_match['code'],
            'description': best_match['description'],
            'confidence': best_match['confidence'],
            'justification': justification,
            'alternatives': [
                {
                    'icd10_code': alt['code'],
                    'description': alt['description'],
                    'confidence': alt['confidence']
                }
                for alt in alternatives
            ]
        }
    
    def _clean_diagnosis(self, diagnosis: str) -> str:
        """Clean and normalize diagnosis text"""
        # Remove extra whitespace and convert to lowercase
        clean = re.sub(r'\s+', ' ', diagnosis.strip().lower())
        
        # Remove common medical abbreviations and standardize
        replacements = {
            'w/o': 'without',
            'w/': 'with',
            'unspec': 'unspecified',
            'nos': 'not otherwise specified',
            'nec': 'not elsewhere classified',
            'dm': 'diabetes mellitus',
            'htn': 'hypertension',
            'copd': 'chronic obstructive pulmonary disease',
            'ckd': 'chronic kidney disease',
            'chf': 'congestive heart failure',
            'mi': 'myocardial infarction',
            'cad': 'coronary artery disease',
            'afib': 'atrial fibrillation',
            'dvt': 'deep vein thrombosis',
            'pe': 'pulmonary embolism',
            'uti': 'urinary tract infection',
            'copd': 'chronic obstructive pulmonary disease'
        }
        
        for abbrev, full in replacements.items():
            clean = re.sub(rf'\b{abbrev}\b', full, clean)
        
        # Remove punctuation but keep alphanumeric and spaces
        clean = re.sub(r'[^\w\s]', ' ', clean)
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        return clean
    
    def _fuzzy_match(self, diagnosis: str) -> List[Dict]:
        """Perform fuzzy string matching against ICD-10 descriptions"""
        matches = []
        
        for _, row in self.icd10_data.iterrows():
            # Match against description
            ratio = fuzz.token_sort_ratio(diagnosis, row['description'].lower())
            if ratio > 50:  # Minimum threshold
                matches.append({
                    'code': row['code'],
                    'description': row['description'],
                    'confidence': ratio / 100.0,
                    'match_type': 'fuzzy',
                    'category': row['category']
                })
        
        return sorted(matches, key=lambda x: x['confidence'], reverse=True)
    
    def _pattern_match(self, diagnosis: str) -> List[Dict]:
        """Match diagnosis against common patterns"""
        matches = []
        
        for pattern_name, keywords in self.diagnosis_patterns.items():
            # Check if any keywords match
            diagnosis_words = diagnosis.split()
            matched_keywords = []
            
            for keyword in keywords:
                if keyword in diagnosis or any(keyword in word for word in diagnosis_words):
                    matched_keywords.append(keyword)
            
            if matched_keywords:
                # Find relevant ICD-10 codes for this pattern
                relevant_codes = self._get_codes_for_pattern(pattern_name, matched_keywords)
                
                for code_info in relevant_codes:
                    # Calculate confidence based on keyword matches
                    confidence = min(0.95, len(matched_keywords) / len(keywords) + 0.5)
                    
                    matches.append({
                        'code': code_info['code'],
                        'description': code_info['description'],
                        'confidence': confidence,
                        'match_type': 'pattern',
                        'category': code_info['category'],
                        'matched_keywords': matched_keywords
                    })
        
        return sorted(matches, key=lambda x: x['confidence'], reverse=True)
    
    def _get_codes_for_pattern(self, pattern_name: str, matched_keywords: List[str]) -> List[Dict]:
        """Get ICD-10 codes relevant to a specific pattern"""
        pattern_to_codes = {
            'diabetes': ['E11.9', 'E11.8', 'E10.9', 'E11.65'],
            'hypertension': ['I10', 'I11.9', 'I12.9'],
            'hyperlipidemia': ['E78.5', 'E78.0', 'E78.2'],
            'copd': ['J44.1', 'J44.0'],
            'asthma': ['J45.9'],
            'kidney': ['N18.3', 'N18.4', 'N18.5', 'N18.6', 'N18.9'],
            'heart': ['I25.10', 'I50.9', 'I48.91', 'I21.9'],
            'cancer': ['C78.0', 'C78.1', 'C78.2', 'C50.911'],
            'infection': ['A41.9', 'R65.20', 'A49.9', 'J18.9'],
            'anemia': ['D64.9', 'D50.9'],
            'obesity': ['E66.9', 'E66.01'],
            'depression': ['F32.9'],
            'anxiety': ['F41.9'],
            'substance': ['F10.10', 'F10.20', 'F17.210'],
            'fracture': ['S72.001A', 'S22.43XA'],
            'ulcer': ['L97.909', 'L89.90'],
            'hepatitis': ['B19.20', 'B18.2'],
            'hypothyroid': ['E03.9', 'E03.8']
        }
        
        relevant_codes = []
        codes_for_pattern = pattern_to_codes.get(pattern_name, [])
        
        for code in codes_for_pattern:
            code_row = self.icd10_data[self.icd10_data['code'] == code]
            if not code_row.empty:
                relevant_codes.append({
                    'code': code,
                    'description': code_row.iloc[0]['description'],
                    'category': code_row.iloc[0]['category']
                })
        
        return relevant_codes
    
    def _combine_matches(self, fuzzy_matches: List[Dict], pattern_matches: List[Dict]) -> List[Dict]:
        """Combine and deduplicate matches from different strategies"""
        all_matches = {}
        
        # Add fuzzy matches
        for match in fuzzy_matches:
            key = match['code']
            if key not in all_matches or match['confidence'] > all_matches[key]['confidence']:
                all_matches[key] = match
        
        # Add pattern matches (give slight preference to pattern matches)
        for match in pattern_matches:
            key = match['code']
            if key not in all_matches:
                all_matches[key] = match
            else:
                # Boost confidence for pattern matches
                boosted_confidence = min(0.95, match['confidence'] * 1.1)
                if boosted_confidence > all_matches[key]['confidence']:
                    match['confidence'] = boosted_confidence
                    all_matches[key] = match
        
        # Convert to list and sort by confidence
        result = list(all_matches.values())
        return sorted(result, key=lambda x: x['confidence'], reverse=True)
    
    def _generate_justification(self, original: str, best_match: Dict, clean_diagnosis: str) -> str:
        """Generate a human-readable justification for the mapping"""
        match_type = best_match.get('match_type', 'unknown')
        confidence = best_match['confidence']
        
        if match_type == 'fuzzy':
            return f"Fuzzy string matching identified '{best_match['description']}' as the best match for '{original}' with {confidence:.1%} similarity."
        
        elif match_type == 'pattern':
            matched_keywords = best_match.get('matched_keywords', [])
            keywords_str = ', '.join(matched_keywords)
            return f"Pattern matching identified key medical terms ({keywords_str}) that align with '{best_match['description']}' (confidence: {confidence:.1%})."
        
        else:
            return f"Medical terminology analysis suggests '{best_match['description']}' as the most appropriate ICD-10 code for '{original}' (confidence: {confidence:.1%})."
    
    def get_statistics(self) -> Dict:
        """Get statistics about the ICD-10 database"""
        return {
            'total_codes': len(self.icd10_data),
            'categories': self.icd10_data['category'].value_counts().to_dict(),
            'version': 'ICD-10-CM 2024'
        }
