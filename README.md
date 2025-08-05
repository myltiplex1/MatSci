# 🧪 Nanomaterial Synthesis Parameter Extractor

Extracts synthesis parameters from PDF documents for various nanomaterial categories and saves them in JSON or CSV format.

---

## 📖 Overview

This project provides a tool to extract synthesis parameters from nanomaterial-related PDFs and search for relevant papers online. The extraction process uses advanced natural language processing (NLP) with embeddings to identify and extract synthesis parameters, while the search functionality leverages the Serper Google Search API to find relevant papers.

---

## 📦 Embedding Process

The extraction workflow (`extraction/llm_extractor.py`) uses **LangChain** and **langchain-google-genai** for text processing and LLM-based extraction.

- PDFs are processed using `pdf_utils.py`.
- Text is converted into **vector embeddings** using **Google Generative AI**.
- Embeddings are indexed using **faiss-cpu** for efficient similarity search.
- Extracted synthesis parameters are structured into JSON or CSV.
- Special characters like `°` and `⋅` are handled using UTF-8 encoding.

---

## ⚙️ Setup

### Create Virtual Environment:

```bash
python -m venv your-venev
.\your-venev\Scripts\Activate.ps1
```

### Install Dependencies:

```bash
pip install -r requirements.txt
```

### Set Environment Variables:

Create a `.env` file in the project root:

```
GOOGLE_API_KEY=your_google_api_key
SERPER_API_KEY=your_serper_api_key
```

### Embed the sample examples
```bash
python embed_examples.py
```

---

## 🚀 Usage

### 🔧 Command-Line Interface

Run the CLI interface:

```bash
python main.py
```

- Follow prompts to select a nanomaterial category and output format (JSON or CSV).
- The script processes `data/my_paper.pdf` and saves results to `output/extracted_parameters.json` or `.csv`.

---

### 🌐 Streamlit Web Interface

Run the web app:

```bash
streamlit run app.py
```

- Open [http://127.0.0.1:8501](http://127.0.0.1:8501) in your browser.

#### Interface Features:

**Left Column (Extract Parameters):**
- Select a category and output format.
- Upload a PDF.
- Click **"Extract Parameters"**.
- Results appear as a JSON text box (height 200) or CSV table.
- Includes a status message and download button.

**Right Column (Search Papers Online):**
- Select a category and number of results (1–10).
- Click **"Search Papers"** to use the Serper Google Search API.
- Results show titles, URLs, and PDF download buttons.
- Click **"Clear Search Results"** to reset.

#### Additional UI Behavior:
- **"Clear" button** (left column) resets extraction and search states.
- **No PDF uploaded:** Shows `"Please upload a PDF file"` under **Status**.
- **Non-PDF uploaded:** Shows `"Error: Uploaded file must be a PDF"`.
- **No parameters found:** Shows `"No synthesis parameters extracted for the chosen category"`.

---

## 📁 Project Structure

```
main.py                      # CLI script for parameter extraction
sreamlit_app.py                       # Streamlit web interface
search.py                    # Paper search logic using Serper API
extraction/
  └── llm_extractor.py       # LLM-based embedding + extraction logic
pdf_utils.py                 # PDF text extraction
embed_examples.py            # performs embedding
logger.py                    # Logging setup
rag/
   └── promppt.txt           # System Intruction
   └── sample_example.txt    # embedded sample answers
data/                        # Folder for input PDFs
output/                      # Folder for extracted results
```

---

## 📦 Dependencies

- Python 3.8+
- Key packages:
  - streamlit==1.38.0
  - requests==2.32.3
  - langchain==0.2.12
  - langchain-google-genai==1.0.8
  - faiss-cpu==1.8.0

See `requirements.txt` for full list.

---

---
