from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_community.vectorstores import FAISS
from logger import setup_logger
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = setup_logger('llm_extractor')

class LLMExtractor:
    def __init__(self, api_key=None, category=None, faiss_index_path="rag/example_index.faiss"):
        self.category = category
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.error("GEMINI_API_KEY not found in .env file or environment variables")
            raise ValueError("GEMINI_API_KEY not found in .env file or environment variables")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=self.api_key,
            temperature=0.3
        )
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=self.api_key)
        self.vector_store = self.load_vector_store(faiss_index_path)
        self.prompt_template = self.load_prompt_template()
    
    def load_vector_store(self, faiss_index_path):
        """Load precomputed FAISS index for RAG examples."""
        try:
            vector_store = FAISS.load_local(faiss_index_path, self.embeddings, allow_dangerous_deserialization=True)
            logger.info("Loaded FAISS vector store")
            return vector_store
        except Exception as e:
            logger.error(f"Error loading FAISS index: {str(e)}")
            raise
    
    def load_prompt_template(self):
        """Load and customize the prompt template based on category."""
        try:
            with open("rag/prompt.txt", "r") as f:
                base_template = f.read()
            
            # Log raw prompt template for debugging
            logger.info(f"Raw prompt template: {base_template[:500]}...")  # Truncate for brevity
            
            category_instructions = {
                "Metal Oxides": "Focus on parameters like precursor (e.g., zinc nitrate, ammonium carbonate, aluminum nitrate), temperature (e.g., 100-240°C), pH (e.g., 6-8 or null), solvent (e.g., deionized water), and methods like hydrothermal, sol-gel, or calcination.",
                "Metal Sulfides": "Focus on parameters like sulfur source (e.g., thiourea), temperature (e.g., 150-300°C), solvent, and methods like chemical vapor deposition, solvothermal, or precipitation.",
                "Metal-Organic Frameworks": "Focus on parameters like metal ion (e.g., zinc, copper), organic linker (e.g., terephthalic acid), solvent (e.g., DMF), temperature (e.g., 100-150°C), and methods like solvothermal or microwave-assisted synthesis.",
                "Carbon-based": "Focus on parameters like carbon source (e.g., methane, glucose), temperature (e.g., 700-1000°C), catalyst, and methods like chemical vapor deposition, arc discharge, or pyrolysis.",
                "Polymeric Nanomaterials": "Focus on parameters like monomer (e.g., styrene), initiator (e.g., AIBN), solvent, temperature (e.g., 60-80°C), and methods like emulsion polymerization or electrospinning.",
                "Pure Metals / Alloys": "Focus on parameters like metal precursor (e.g., gold chloride), reduction agent (e.g., sodium borohydride), temperature (e.g., 20-100°C), and methods like chemical reduction or electrodeposition."
            }
            
            instruction = category_instructions.get(self.category, "Extract relevant synthesis parameters.")
            template = base_template + "\nCategory-specific instructions: " + instruction
            logger.info(f"Loaded prompt template for {self.category}")
            
            return PromptTemplate(
                input_variables=["category", "text", "examples"],
                template=template
            )
        except Exception as e:
            logger.error(f"Error loading prompt template: {str(e)}")
            raise
    
    def extract_parameters(self, text):
        """Extract synthesis parameters using the LLM and RAG."""
        try:
            # Retrieve relevant examples using FAISS
            docs = self.vector_store.similarity_search(text, k=3)
            examples = "\n".join([doc.page_content for doc in docs])
            logger.info("Retrieved relevant examples for RAG")
            
            # Create a runnable sequence
            chain = RunnableSequence(self.prompt_template | self.llm)
            
            # Run the chain
            inputs = {"category": self.category, "text": text, "examples": examples}
            try:
                formatted_prompt = self.prompt_template.format(**inputs)
                logger.info(f"Formatted prompt: {formatted_prompt[:500]}...")  # Truncate for brevity
            except Exception as e:
                logger.error(f"Failed to format prompt: {str(e)}")
                raise
            
            response = chain.invoke(inputs)
            
            # Log raw response for debugging
            logger.info(f"Raw LLM response: {response.content[:500]}...")  # Truncate for brevity
            logger.info(f"Full LLM response: {response.content}")  # Log full response
            
            # Strip Markdown code block markers if present
            response_content = response.content.strip()
            if response_content.startswith("```json") and response_content.endswith("```"):
                response_content = response_content[7:-3].strip()
            elif response_content.startswith("```") and response_content.endswith("```"):
                response_content = response_content[3:-3].strip()
            
            # Parse the response (assuming JSON-like output)
            try:
                entries = json.loads(response_content)
                if not isinstance(entries, list):
                    entries = [entries]
                # Ensure category is set correctly and handle Unicode characters
                for entry in entries:
                    entry["category"] = self.category
                    # Process string fields to handle Unicode escapes and special characters
                    for key in ["precursor", "temperature", "method", "solvent", "reaction_time", "text_snippet"]:
                        if isinstance(entry.get(key), str):
                            try:
                                # Replace common Unicode escape sequences with literal characters
                                value = entry[key]
                                value = value.replace("\\u00b0", "°").replace("\\u22c5", "⋅")
                                # Handle potential double-encoded UTF-8 (e.g., \u00c2\u00b0)
                                if "Â" in value or "â" in value:
                                    value = value.encode('latin1', errors='ignore').decode('utf-8', errors='ignore')
                                entry[key] = value
                            except Exception as e:
                                logger.warning(f"Failed to decode Unicode for {key}: {str(e)}")
                                entry[key] = entry[key]  # Keep original value if decoding fails
                logger.info(f"Extracted {len(entries)} synthesis entries")
                return entries
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
                logger.error(f"Full response: {response_content}")
                return [{"error": "Invalid response format"}]
        except Exception as e:
            logger.error(f"Error during parameter extraction: {str(e)}")
            raise