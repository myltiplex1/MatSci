import streamlit as st
import pandas as pd
from extraction.llm_extractor import LLMExtractor
from pdf_utils import extract_text_from_pdf
from logger import setup_logger
from search import search_papers
import os
import json
import csv
import tempfile
import io
import requests

logger = setup_logger('nanomaterial_extraction')

def save_to_json(data, output_path):
    """Save extracted data to a JSON file."""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        if not data:
            logger.warning("No data to save to JSON")
            return "No synthesis parameters extracted for the chosen category"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logger.info(f"Saved extracted parameters to {output_path}")
        return f"Extracted {len(data)} synthesis entries"
    except Exception as e:
        logger.error(f"Error saving JSON: {str(e)}")
        return f"Error saving JSON: {str(e)}"

def save_to_csv(data, output_path):
    """Save extracted data to a CSV file."""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        if not data:
            logger.warning("No data to save to CSV")
            return "No synthesis parameters extracted for the chosen category"
        keys = data[0].keys()
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
        logger.info(f"Saved extracted parameters to {output_path}")
        return f"Extracted {len(data)} synthesis entries"
    except Exception as e:
        logger.error(f"Error saving CSV: {str(e)}")
        return f"Error saving CSV: {str(e)}"

def extract_parameters(category, output_format, pdf_file):
    """Extract synthesis parameters from an uploaded PDF file."""
    try:
        # Validate inputs
        categories = [
            "Metal Oxides",
            "Metal Sulfides",
            "Metal-Organic Frameworks",
            "Carbon-based",
            "Polymeric Nanomaterials",
            "Pure Metals / Alloys"
        ]
        if category not in categories:
            logger.error(f"Invalid category: {category}")
            return f"Invalid category: {category}", None, None, None
        
        if output_format not in ["JSON", "CSV"]:
            logger.error(f"Invalid output format: {output_format}")
            return f"Invalid output format: {output_format}", None, None, None
        
        # Validate PDF file
        if pdf_file is None:
            logger.error("No PDF file uploaded")
            return "Error: No PDF file uploaded", None, None, None
        
        if not pdf_file.name.lower().endswith('.pdf'):
            logger.error(f"Invalid file type: {pdf_file.name}")
            return "Error: Uploaded file must be a PDF", None, None, None
        
        # Save uploaded PDF to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(pdf_file.read())
            temp_pdf_path = temp_pdf.name
        
        # Extract text from PDF
        logger.info(f"Extracting text from uploaded PDF")
        pdf_text = extract_text_from_pdf(temp_pdf_path)
        logger.info("PDF text extraction completed")
        
        # Clean up temporary file
        os.unlink(temp_pdf_path)
        
        # Initialize LLM extractor
        logger.info(f"Initializing LLM extractor for {category}")
        extractor = LLMExtractor(category=category)
        
        # Extract parameters
        logger.info("Starting parameter extraction")
        synthesis_entries = extractor.extract_parameters(pdf_text)
        logger.info("Extraction completed")
        
        # Save results
        output_path = f"output/extracted_parameters.{output_format.lower()}"
        save_result = save_to_json(synthesis_entries, output_path) if output_format == "JSON" else save_to_csv(synthesis_entries, output_path)
        
        # Prepare output for display
        if output_format == "JSON":
            if not synthesis_entries:
                output_display = None
                display_data = None
            else:
                output_display = json.dumps(synthesis_entries, indent=4, ensure_ascii=False)
                display_data = synthesis_entries
        else:
            if not synthesis_entries:
                output_display = None
                display_data = None
            else:
                display_data = pd.DataFrame(synthesis_entries)
                output_display = display_data.to_csv(index=False, encoding='utf-8')
        
        # Read file for download (if data exists)
        file_content = None
        if synthesis_entries:
            with open(output_path, 'rb') as f:
                file_content = f.read()
        
        return save_result, output_display, file_content, display_data
    
    except Exception as e:
        logger.error(f"Error in extraction: {str(e)}")
        return f"Error: {str(e)}", None, None, None

# Streamlit interface
st.title("Nanomaterial Synthesis Parameter Extractor")
st.markdown("Extract synthesis parameters from a PDF (left) or search for papers online (right).")

# Initialize session state
if 'output_text' not in st.session_state:
    st.session_state.output_text = None
if 'save_status' not in st.session_state:
    st.session_state.save_status = ""
if 'file_content' not in st.session_state:
    st.session_state.file_content = None
if 'output_format' not in st.session_state:
    st.session_state.output_format = "JSON"
if 'display_data' not in st.session_state:
    st.session_state.display_data = None
if 'pdf_uploaded' not in st.session_state:
    st.session_state.pdf_uploaded = False
if 'extract_triggered' not in st.session_state:
    st.session_state.extract_triggered = False
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'num_results' not in st.session_state:
    st.session_state.num_results = 5

# Two-column layout with increased spacing
col_extract, col_search = st.columns([1, 1], gap="large")

# Extraction column (left)
with col_extract:
    st.subheader("Extract Parameters")
    category = st.selectbox(
        "Select Category",
        [
            "Metal Oxides",
            "Metal Sulfides",
            "Metal-Organic Frameworks",
            "Carbon-based",
            "Polymeric Nanomaterials",
            "Pure Metals / Alloys"
        ],
        index=0,
        key="extract_category"
    )
    output_format = st.selectbox(
        "Select Output Format",
        ["JSON", "CSV"],
        index=0,
        key="extract_format"
    )
    pdf_file = st.file_uploader("Upload PDF File", type=["pdf"], accept_multiple_files=False)

    # Buttons
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        extract_button = st.button("Extract Parameters")
    with col_btn2:
        clear_button = st.button("Clear")

    # Handle clear button
    if clear_button:
        st.session_state.output_text = None
        st.session_state.save_status = ""
        st.session_state.file_content = None
        st.session_state.output_format = "JSON"
        st.session_state.display_data = None
        st.session_state.pdf_uploaded = False
        st.session_state.extract_triggered = False
        st.session_state.search_results = []
        st.rerun()

    # Handle extract button
    if extract_button:
        st.session_state.extract_triggered = True
        if pdf_file is not None:
            with st.spinner("Extracting parameters..."):
                st.session_state.save_status, st.session_state.output_text, st.session_state.file_content, st.session_state.display_data = extract_parameters(category, output_format, pdf_file)
                st.session_state.output_format = output_format
        else:
            st.session_state.save_status = "Please upload a PDF file."
            st.session_state.output_text = None
            st.session_state.display_data = None
            st.session_state.file_content = None

    # Display extraction outputs
    if st.session_state.extract_triggered and (st.session_state.output_text is not None or st.session_state.display_data is not None):
        st.subheader("Extracted Parameters")
        if st.session_state.output_format == "JSON" and st.session_state.output_text:
            st.text_area("", st.session_state.output_text, height=200)
        elif st.session_state.output_format == "CSV" and st.session_state.display_data is not None:
            st.dataframe(st.session_state.display_data, use_container_width=True)

    if st.session_state.extract_triggered and st.session_state.save_status:
        st.subheader("Status")
        st.write(st.session_state.save_status)

    # Download button
    if st.session_state.file_content is not None:
        st.download_button(
            label="Download Extracted Parameters",
            data=st.session_state.file_content,
            file_name=f"extracted_parameters.{st.session_state.output_format.lower()}",
            mime="application/json" if st.session_state.output_format == "JSON" else "text/csv"
        )

# Search column (right)
with col_search:
    st.subheader("Search Papers Online")
    search_category = st.selectbox(
        "Select Category for Search",
        [
            "Metal Oxides",
            "Metal Sulfides",
            "Metal-Organic Frameworks",
            "Carbon-based",
            "Polymeric Nanomaterials",
            "Pure Metals / Alloys"
        ],
        index=0,
        key="search_category"
    )
    st.session_state.num_results = st.number_input(
        "Number of Search Results (max 10)",
        min_value=1,
        max_value=10,
        value=st.session_state.num_results,
        step=1
    )
    col_search_btn1, col_search_btn2 = st.columns(2)
    with col_search_btn1:
        if st.button("Search Papers"):
            with st.spinner("Searching papers..."):
                st.session_state.search_results = search_papers(search_category, st.session_state.num_results)
    with col_search_btn2:
        if st.button("Clear Search Results"):
            st.session_state.search_results = []
    
    if st.session_state.search_results:
        st.subheader("Search Results")
        # Format search results for text box
        search_text = "\n".join(
            f"{i+1}. {result['title']} ({result['url']})"
            for i, result in enumerate(st.session_state.search_results)
        )
        st.text_area("", search_text, height=200, key="search_results_text")
        
        # Download buttons for PDFs
        for i, result in enumerate(st.session_state.search_results):
            try:
                response = requests.get(result['url'], timeout=5)
                if response.status_code == 200 and 'application/pdf' in response.headers.get('Content-Type', ''):
                    st.download_button(
                        label=f"Download {result['title']}",
                        data=response.content,
                        file_name=f"{result['title']}.pdf",
                        mime="application/pdf",
                        key=f"download_{i}"
                    )
                else:
                    st.write(f"PDF not available for: {result['title']}")
            except Exception as e:
                st.write(f"Error fetching PDF for {result['title']}: {str(e)}")

# Reset outputs when a new PDF is uploaded
if pdf_file is not None and not st.session_state.pdf_uploaded:
    st.session_state.output_text = None
    st.session_state.save_status = ""
    st.session_state.file_content = None
    st.session_state.display_data = None
    st.session_state.pdf_uploaded = True
    st.session_state.extract_triggered = False
elif pdf_file is None:
    st.session_state.pdf_uploaded = False
    st.session_state.extract_triggered = False
    st.session_state.output_text = None
    st.session_state.save_status = ""
    st.session_state.file_content = None
    st.session_state.display_data = None