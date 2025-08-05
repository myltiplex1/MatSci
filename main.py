from extraction.llm_extractor import LLMExtractor
from pdf_utils import extract_text_from_pdf
from logger import setup_logger
import os
import json
import csv

logger = setup_logger('nanomaterial_extraction')

def save_to_json(data, output_path):
    """Save extracted data to a JSON file."""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logger.info(f"Saved extracted parameters to {output_path}")
    except Exception as e:
        logger.error(f"Error saving JSON: {str(e)}")
        raise

def save_to_csv(data, output_path):
    """Save extracted data to a CSV file."""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        if not data:
            logger.warning("No data to save to CSV")
            return
        keys = data[0].keys()
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
        logger.info(f"Saved extracted parameters to {output_path}")
    except Exception as e:
        logger.error(f"Error saving CSV: {str(e)}")
        raise

def main():
    try:
        # Define available categories
        categories = [
            "Metal Oxides",
            "Metal Sulfides",
            "Metal-Organic Frameworks",
            "Carbon-based",
            "Polymeric Nanomaterials",
            "Pure Metals / Alloys"
        ]
        
        # Prompt user to select a category
        print("Available categories:")
        for i, category in enumerate(categories, 1):
            print(f"{i}. {category}")
        category_choice = int(input("Enter the number of the category (1-6): "))
        if category_choice < 1 or category_choice > len(categories):
            raise ValueError("Invalid category choice")
        selected_category = categories[category_choice - 1]
        logger.info(f"Selected category: {selected_category}")
        
        # Prompt user to select output format
        print("Available output formats:")
        print("1. JSON")
        print("2. CSV")
        format_choice = int(input("Enter the number of the output format (1-2): "))
        if format_choice not in [1, 2]:
            raise ValueError("Invalid output format choice")
        output_format = "json" if format_choice == 1 else "csv"
        logger.info(f"Selected output format: {output_format}")
        
        # Extract text from PDF
        pdf_path = "data/my_paper.pdf"
        logger.info(f"Extracting text from {pdf_path}")
        pdf_text = extract_text_from_pdf(pdf_path)
        logger.info("PDF text extraction completed")
        
        # Initialize LLM extractor
        logger.info(f"Initializing LLM extractor for {selected_category}")
        extractor = LLMExtractor(category=selected_category)
        
        # Extract parameters
        logger.info("Starting parameter extraction")
        synthesis_entries = extractor.extract_parameters(pdf_text)
        logger.info("Extraction completed")
        
        # Save results
        output_path = f"output/extracted_parameters.{output_format}"
        if output_format == "json":
            save_to_json(synthesis_entries, output_path)
        else:
            save_to_csv(synthesis_entries, output_path)
        
        # Print extracted parameters
        print("Extracted Parameters:")
        print(json.dumps(synthesis_entries, indent=4, ensure_ascii=False))
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    main()