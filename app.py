import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO
import json
from icd10_mapper import ICD10Mapper
from data_processor import DataProcessor
from utils import format_confidence_score, export_to_csv

# Configure page
st.set_page_config(
    page_title="ICD-10 Diagnosis Mapper",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'mapping_results' not in st.session_state:
    st.session_state.mapping_results = None
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'mapper' not in st.session_state:
    st.session_state.mapper = None

def main():
    st.title("🏥 ICD-10 Diagnosis Mapper")
    st.markdown("An AI-powered system to map patient diagnoses to ICD-10 codes with justifications")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        confidence_threshold = st.slider(
            "Confidence Threshold", 
            min_value=0.0, 
            max_value=1.0, 
            value=0.7, 
            step=0.05,
            help="Minimum confidence score for automatic mapping"
        )
        
        max_suggestions = st.selectbox(
            "Max Alternative Suggestions",
            [1, 2, 3, 4, 5],
            index=2,
            help="Maximum number of alternative suggestions for ambiguous cases"
        )
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This system uses:
        - Fuzzy string matching
        - Semantic similarity analysis
        - Multiple ICD-10 data sources
        - AI-powered mapping decisions
        """)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📁 Data Loading")
        
        # Auto-load the CSV file from attached assets
        csv_path = "attached_assets/Diagnoses_list - Sheet1 (1)_1751711430219.csv"
        
        try:
            # Process the CSV file
            processor = DataProcessor()
            df = processor.load_csv_from_path(csv_path)
            
            st.success(f"✅ File loaded successfully! Found {len(df)} patient records.")
            st.info(f"📁 Using file: {csv_path}")
            
            # Display sample data
            st.subheader("📊 Data Preview")
            st.dataframe(df.head(), use_container_width=True)
            
            # Initialize mapper if not already done
            if st.session_state.mapper is None:
                with st.spinner("🔄 Initializing ICD-10 mapper..."):
                    st.session_state.mapper = ICD10Mapper()
            
            # Process diagnoses
            if st.button("🚀 Start Mapping", type="primary"):
                with st.spinner("🔍 Mapping diagnoses to ICD-10 codes..."):
                    progress_bar = st.progress(0)
                    
                    # Process each row
                    results = []
                    for i, (idx, row) in enumerate(df.iterrows()):
                        diagnoses = processor.parse_diagnoses(str(row['Diagnoses_list']))
                        
                        patient_results = []
                        for diagnosis in diagnoses:
                            mapping = st.session_state.mapper.map_diagnosis(
                                diagnosis, 
                                confidence_threshold,
                                max_suggestions
                            )
                            patient_results.append(mapping)
                        
                        results.append({
                            'patient_id': i + 1,
                            'original_diagnoses': diagnoses,
                            'mappings': patient_results
                        })
                        
                        # Update progress
                        progress_bar.progress((i + 1) / len(df))
                    
                    st.session_state.mapping_results = results
                    st.session_state.processed_data = df
                    
                    # Generate and save consolidated output CSV
                    csv_output = export_results_to_csv()
                    with open("output.csv", "w", encoding="utf-8") as f:
                        f.write(csv_output)
                    
                    st.success("✅ Mapping completed!")
                    st.success("📁 Consolidated results saved to output.csv")
                    st.rerun()
                    
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.info("Make sure the CSV file exists in the attached_assets folder.")
    
    with col2:
        st.header("📋 Instructions")
        st.markdown("""
        1. **Upload CSV**: Select your diagnoses file
        2. **Configure**: Adjust settings in sidebar
        3. **Map**: Click 'Start Mapping' to begin
        4. **Review**: Check results and confidence scores
        5. **Export**: Download final dataset
        """)
        
        if st.session_state.mapping_results:
            st.markdown("---")
            st.markdown("### 📈 Quick Stats")
            total_diagnoses = sum(len(r['mappings']) for r in st.session_state.mapping_results)
            high_confidence = sum(
                1 for r in st.session_state.mapping_results 
                for m in r['mappings'] 
                if m['confidence'] >= confidence_threshold
            )
            
            st.metric("Total Diagnoses", total_diagnoses)
            st.metric("High Confidence", high_confidence)
            st.metric("Accuracy Rate", f"{(high_confidence/total_diagnoses)*100:.1f}%")
            
            # Check if output.csv exists
            import os
            if os.path.exists("output.csv"):
                file_size = os.path.getsize("output.csv") / 1024  # KB
                st.markdown("---")
                st.markdown("### 📁 Output File")
                st.success(f"✅ output.csv ready ({file_size:.1f} KB)")
                st.info("Scroll down to the Export section to download")
    
    # Display mapping results
    if st.session_state.mapping_results:
        st.header("🎯 Mapping Results")
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["📊 Overview", "🔍 Detailed Results", "⚠️ Review Required"])
        
        with tab1:
            display_overview()
        
        with tab2:
            display_detailed_results(confidence_threshold)
        
        with tab3:
            display_review_required(confidence_threshold)
        
        # Export functionality
        st.header("📥 Export Results")
        
        # Main consolidated output file
        st.subheader("📁 Consolidated Output")
        csv_data = export_results_to_csv()
        
        # Show preview of CSV content
        if st.checkbox("📋 Preview CSV Content", help="Show a preview of the output.csv file"):
            try:
                preview_df = pd.read_csv(StringIO(csv_data))
                st.dataframe(preview_df.head(10), use_container_width=True)
                st.info(f"Showing first 10 rows of {len(preview_df)} total records")
            except Exception as e:
                st.error(f"Error previewing CSV: {str(e)}")
        
        st.download_button(
            label="💾 Download output.csv",
            data=csv_data,
            file_name="output.csv",
            mime="text/csv",
            type="primary",
            help="Download the complete mapping results in CSV format"
        )
        
        # Additional export options
        st.subheader("📋 Additional Formats")
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="📊 Custom CSV Export",
                data=csv_data,
                file_name="icd10_mappings.csv",
                mime="text/csv",
                help="Download with custom filename"
            )
        
        with col2:
            json_data = json.dumps(st.session_state.mapping_results, indent=2)
            st.download_button(
                label="📋 JSON Export",
                data=json_data,
                file_name="icd10_mappings.json",
                mime="application/json",
                help="Download in JSON format"
            )

def display_overview():
    """Display overview of mapping results"""
    if not st.session_state.mapping_results:
        return
    
    # Aggregate statistics
    all_mappings = []
    for result in st.session_state.mapping_results:
        all_mappings.extend(result['mappings'])
    
    if not all_mappings:
        st.warning("No mappings found.")
        return
    
    # Confidence distribution
    confidences = [m['confidence'] for m in all_mappings]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Confidence Distribution")
        confidence_df = pd.DataFrame({
            'Confidence': confidences,
            'Range': pd.cut(confidences, bins=[0, 0.3, 0.6, 0.8, 1.0], labels=['Low', 'Medium', 'High', 'Very High'])
        })
        st.bar_chart(confidence_df['Range'].value_counts())
    
    with col2:
        st.subheader("🏆 Top ICD-10 Codes")
        codes = [m['icd10_code'] for m in all_mappings if m['icd10_code'] != 'UNKNOWN']
        if codes:
            code_counts = pd.Series(codes).value_counts().head(10)
            st.bar_chart(code_counts)
        else:
            st.info("No valid ICD-10 codes found.")

def display_detailed_results(confidence_threshold):
    """Display detailed mapping results"""
    if not st.session_state.mapping_results:
        return
    
    for result in st.session_state.mapping_results:
        with st.expander(f"Patient {result['patient_id']} - {len(result['mappings'])} diagnoses"):
            for i, mapping in enumerate(result['mappings']):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Original Diagnosis:** {mapping['original_diagnosis']}")
                    st.write(f"**ICD-10 Code:** {mapping['icd10_code']}")
                    st.write(f"**Description:** {mapping['description']}")
                    st.write(f"**Justification:** {mapping['justification']}")
                    
                    # Alternative suggestions
                    if mapping['alternatives']:
                        st.write("**Alternative Suggestions:**")
                        for alt in mapping['alternatives']:
                            st.write(f"  - {alt['icd10_code']}: {alt['description']} (Score: {alt['confidence']:.2f})")
                
                with col2:
                    confidence_color = "green" if mapping['confidence'] >= confidence_threshold else "red"
                    st.markdown(f"**Confidence**")
                    st.markdown(f"<span style='color: {confidence_color}; font-size: 24px; font-weight: bold;'>{mapping['confidence']:.2f}</span>", unsafe_allow_html=True)
                
                if i < len(result['mappings']) - 1:
                    st.divider()

def display_review_required(confidence_threshold):
    """Display mappings that require manual review"""
    if not st.session_state.mapping_results:
        return
    
    review_needed = []
    for result in st.session_state.mapping_results:
        for mapping in result['mappings']:
            if mapping['confidence'] < confidence_threshold:
                review_needed.append({
                    'patient_id': result['patient_id'],
                    'mapping': mapping
                })
    
    if not review_needed:
        st.success("🎉 All mappings meet the confidence threshold!")
        return
    
    st.warning(f"⚠️ {len(review_needed)} mappings require manual review")
    
    for item in review_needed:
        mapping = item['mapping']
        
        st.subheader(f"Patient {item['patient_id']}")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write(f"**Original:** {mapping['original_diagnosis']}")
            st.write(f"**Suggested:** {mapping['icd10_code']} - {mapping['description']}")
            st.write(f"**Reasoning:** {mapping['justification']}")
            
            if mapping['alternatives']:
                st.write("**Consider these alternatives:**")
                for alt in mapping['alternatives']:
                    st.write(f"  • {alt['icd10_code']}: {alt['description']} (Score: {alt['confidence']:.2f})")
        
        with col2:
            st.metric("Confidence", f"{mapping['confidence']:.2f}")
            if st.button(f"✅ Accept", key=f"accept_{item['patient_id']}_{mapping['original_diagnosis']}"):
                st.success("Mapping accepted!")
        
        st.divider()

def export_results_to_csv():
    """Export mapping results to CSV format"""
    if not st.session_state.mapping_results:
        return ""
    
    rows = []
    for result in st.session_state.mapping_results:
        for mapping in result['mappings']:
            rows.append({
                'Patient_ID': result['patient_id'],
                'Original_Diagnosis': mapping['original_diagnosis'],
                'ICD10_Code': mapping['icd10_code'],
                'ICD10_Description': mapping['description'],
                'Confidence_Score': mapping['confidence'],
                'Justification': mapping['justification'],
                'Alternative_Codes': '; '.join([f"{alt['icd10_code']}: {alt['description']}" for alt in mapping['alternatives']])
            })
    
    df = pd.DataFrame(rows)
    return df.to_csv(index=False)

if __name__ == "__main__":
    main()
