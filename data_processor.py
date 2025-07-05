import pandas as pd
import ast
import re
from typing import List, Dict, Any
import streamlit as st

class DataProcessor:
    """Handles data processing for diagnosis CSV files"""
    
    def __init__(self):
        self.supported_formats = ['csv']
    
    def load_csv(self, uploaded_file) -> pd.DataFrame:
        """Load and validate CSV file"""
        try:
            # Read the CSV file
            df = pd.read_csv(uploaded_file)
            
            # Validate structure
            if 'Diagnoses_list' not in df.columns:
                raise ValueError("CSV must contain 'Diagnoses_list' column")
            
            # Remove empty rows
            df = df.dropna(subset=['Diagnoses_list'])
            
            # Reset index
            df = df.reset_index(drop=True)
            
            return df
            
        except Exception as e:
            raise Exception(f"Error loading CSV file: {str(e)}")
    
    def parse_diagnoses(self, diagnoses_text: str) -> List[str]:
        """Parse diagnoses from text format (list string or delimited text)"""
        if pd.isna(diagnoses_text):
            return []
        
        diagnoses_text = str(diagnoses_text).strip()
        
        # Try to parse as Python list literal
        try:
            if diagnoses_text.startswith('[') and diagnoses_text.endswith(']'):
                parsed = ast.literal_eval(diagnoses_text)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]
        except (ValueError, SyntaxError):
            pass
        
        # Try to parse as delimited text
        diagnoses = []
        
        # Split by common delimiters
        for delimiter in [';', ',', '\n', '|']:
            if delimiter in diagnoses_text:
                parts = diagnoses_text.split(delimiter)
                diagnoses = [part.strip() for part in parts if part.strip()]
                break
        
        # If no delimiters found, treat as single diagnosis
        if not diagnoses:
            diagnoses = [diagnoses_text]
        
        # Clean up diagnoses
        cleaned_diagnoses = []
        for diagnosis in diagnoses:
            cleaned = self._clean_diagnosis_text(diagnosis)
            if cleaned:
                cleaned_diagnoses.append(cleaned)
        
        return cleaned_diagnoses
    
    def _clean_diagnosis_text(self, diagnosis: str) -> str:
        """Clean individual diagnosis text"""
        if not diagnosis:
            return ""
        
        # Remove quotes and extra whitespace
        cleaned = diagnosis.strip('\'"').strip()
        
        # Remove common prefixes/suffixes that don't add medical value
        prefixes_to_remove = [
            'diagnosis:', 'dx:', 'condition:', 'history of', 'h/o', 'hx of'
        ]
        
        cleaned_lower = cleaned.lower()
        for prefix in prefixes_to_remove:
            if cleaned_lower.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
                break
        
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Filter out very short or non-meaningful diagnoses
        if len(cleaned) < 3:
            return ""
        
        # Filter out common non-diagnoses
        non_diagnoses = [
            'none', 'n/a', 'na', 'nil', 'no diagnosis', 'unknown', 'unclear',
            'pending', 'tbd', 'to be determined', 'see notes'
        ]
        
        if cleaned.lower() in non_diagnoses:
            return ""
        
        return cleaned
    
    def validate_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate the loaded data and return statistics"""
        stats = {
            'total_rows': len(df),
            'valid_rows': 0,
            'total_diagnoses': 0,
            'empty_diagnoses': 0,
            'validation_errors': []
        }
        
        for idx, row in df.iterrows():
            try:
                diagnoses = self.parse_diagnoses(row['Diagnoses_list'])
                if diagnoses:
                    stats['valid_rows'] += 1
                    stats['total_diagnoses'] += len(diagnoses)
                else:
                    stats['empty_diagnoses'] += 1
                    stats['validation_errors'].append(f"Row {idx + 1}: No valid diagnoses found")
            except Exception as e:
                stats['validation_errors'].append(f"Row {idx + 1}: {str(e)}")
        
        return stats
    
    def get_sample_diagnoses(self, df: pd.DataFrame, n_samples: int = 5) -> List[str]:
        """Get sample diagnoses for preview"""
        samples = []
        
        for _, row in df.head(n_samples).iterrows():
            diagnoses = self.parse_diagnoses(row['Diagnoses_list'])
            if diagnoses:
                samples.extend(diagnoses[:2])  # Take first 2 diagnoses per row
        
        return samples[:n_samples]
    
    def export_results(self, results: List[Dict], format: str = 'csv') -> str:
        """Export mapping results to specified format"""
        if format == 'csv':
            return self._export_to_csv(results)
        elif format == 'json':
            return self._export_to_json(results)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_to_csv(self, results: List[Dict]) -> str:
        """Export results to CSV format"""
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
                    'Alternative_Codes': self._format_alternatives(mapping['alternatives'])
                }
                rows.append(row)
        
        df = pd.DataFrame(rows)
        return df.to_csv(index=False)
    
    def _export_to_json(self, results: List[Dict]) -> str:
        """Export results to JSON format"""
        import json
        return json.dumps(results, indent=2)
    
    def _format_alternatives(self, alternatives: List[Dict]) -> str:
        """Format alternative suggestions as string"""
        if not alternatives:
            return ""
        
        formatted = []
        for alt in alternatives:
            formatted.append(f"{alt['icd10_code']}: {alt['description']} (Score: {alt['confidence']:.2f})")
        
        return "; ".join(formatted)
