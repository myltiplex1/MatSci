import os
import json
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from logger import setup_logger
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = setup_logger('embed_examples')

def embed_examples():
    """Generate and save FAISS embeddings for RAG examples."""
    try:
        # Load Gemini API key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY not found in .env file or environment variables")
            raise ValueError("GEMINI_API_KEY not found in .env file or environment variables")
        
        # Initialize embeddings
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
        logger.info("Initialized Gemini embeddings")
        
        # Load examples from sample_example.txt
        with open("rag/sample_example.txt", "r") as f:
            examples = json.load(f)
        
        # Prepare texts for embedding (use text_snippet field)
        texts = [example["text_snippet"] for example in examples]
        logger.info(f"Loaded {len(texts)} examples for embedding")
        
        # Create FAISS index
        vector_store = FAISS.from_texts(texts, embeddings)
        logger.info("Created FAISS index")
        
        # Save FAISS index
        vector_store.save_local("rag/example_index.faiss")
        logger.info("Saved FAISS index to rag/example_index.faiss")
        
    except Exception as e:
        logger.error(f"Error generating embeddings: {str(e)}")
        raise

if __name__ == "__main__":
    embed_examples()