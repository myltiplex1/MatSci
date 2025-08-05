from pathlib import Path

def define_project_structure():
    """Define the project directory structure."""
    structure = {
        "main.py": "Main script for local execution",
        "logger.py": "Logging configuration",
        "gradio_app.py": "Gradio UI for deployment",
        "requirements.txt": "Project dependencies",
        "README.md": "Project documentation",
        "embed_examples.py": "Script to generate FAISS embeddings for RAG examples",
        "data/": "Folder for input PDFs",
        "extraction/llm_extractor.py": "LLM-based parameter extraction",
        "extraction/confidence.py": "Confidence score calculation",
        "rag/prompt.txt": "LLM prompt template",
        "rag/sample_example.txt": "RAG example data for extraction",
        "output/": "Folder for extracted parameters"
    }
    return structure

def create_project_structure(base_path=".", structure=None):
    """Create directories and files based on the project structure."""
    if structure is None:
        structure = define_project_structure()
    
    base_path = Path(base_path)
    base_path.mkdir(exist_ok=True)
    
    for key, value in structure.items():
        path = base_path / key
        if key.endswith("/"):
            # Create directory only
            path.mkdir(parents=True, exist_ok=True)
            print(f"Created directory: {path}")
        elif key.endswith(".py") or key.endswith(".txt") or key.endswith(".md"):
            # Create parent directories and empty file
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                path.touch()
                print(f"Created file: {path}")
        else:
            print(f"Skipping invalid entry: {key}")

def print_structure(structure=None, prefix="", root=None):
    """Print the project structure."""
    if structure is None:
        structure = define_project_structure()
        root = "nanomaterial_extraction"
    
    for key, value in structure.items():
        print(f"{prefix}{key}: {value}")

if __name__ == "__main__":
    print("Project structure to be created:")
    print_structure()
    print("\nCreating directory structure...")
    create_project_structure()
    print("Directory structure created.")