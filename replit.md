# ICD-10 Diagnosis Mapper

## Overview

This is an AI-powered Streamlit application that maps patient diagnoses to ICD-10 codes with justifications. The system processes CSV files containing patient diagnosis data and provides automated mapping with confidence scores, alternative suggestions, and detailed justifications for each mapping decision.

## System Architecture

The application follows a modular architecture with clear separation of concerns:

**Frontend**: Streamlit-based web interface providing an intuitive user experience
**Backend**: Python-based processing engine with multiple specialized modules
**Data Layer**: CSV file processing with support for various diagnosis formats
**AI/ML Layer**: Fuzzy matching algorithms combined with semantic analysis for intelligent code mapping

## Key Components

### 1. Main Application (`app.py`)
- **Purpose**: Entry point and UI controller
- **Technology**: Streamlit framework
- **Key Features**:
  - File upload interface
  - Configuration sidebar with confidence threshold and suggestion controls
  - Results display with interactive tables
  - Export functionality

### 2. ICD-10 Mapper (`icd10_mapper.py`)
- **Purpose**: Core mapping logic and AI-powered diagnosis analysis
- **Technology**: FuzzyWuzzy for string matching, custom semantic analysis
- **Key Features**:
  - Loads ICD-10 code database from multiple sources
  - Implements fuzzy matching for diagnosis-to-code mapping
  - Provides confidence scoring and alternative suggestions
  - Generates justifications for mapping decisions

### 3. Data Processor (`data_processor.py`)
- **Purpose**: Handles input data parsing and validation
- **Technology**: Pandas for data manipulation
- **Key Features**:
  - CSV file loading and validation
  - Multiple diagnosis format parsing (list strings, delimited text)
  - Data cleaning and normalization

### 4. Utilities (`utils.py`)
- **Purpose**: Common utility functions and formatting
- **Key Features**:
  - Confidence score formatting with visual indicators
  - CSV export functionality
  - Statistics calculation
  - Alternative suggestion formatting

## Data Flow

1. **Input**: User uploads CSV file with patient diagnoses
2. **Processing**: Data processor validates and parses diagnosis data
3. **Mapping**: ICD-10 mapper analyzes each diagnosis using fuzzy matching and semantic analysis
4. **Scoring**: System calculates confidence scores and generates alternatives
5. **Output**: Results displayed in interactive interface with export options

## External Dependencies

### Core Libraries
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **FuzzyWuzzy**: String matching algorithms

### Optional Enhancements
- **Requests**: For potential API integrations
- **JSON**: Data serialization
- **AST**: Safe evaluation of literal expressions

## Deployment Strategy

The application is designed for Replit deployment with:
- **Environment**: Python 3.x runtime
- **Dependencies**: Managed via requirements.txt or similar
- **Scaling**: Single-instance deployment suitable for moderate workloads
- **Data Storage**: File-based processing (no persistent database required)

## Changelog

- July 05, 2025. Initial setup
- July 05, 2025. Modified application to auto-load CSV from attached assets, added comprehensive README documentation

## User Preferences

Preferred communication style: Simple, everyday language.