# Smart Recruitment Assistant

This project is an NLP and LLM-based platform designed to assist recruiters and candidates in analyzing, comparing, and understanding CVs and job offers.

## Key Features:

### Recruiter Side:
*   Upload CVs and job offers.
*   Get a match score.
*   Skill gap analysis.
*   Profile summaries.
*   Ask questions about a CV (RAG).

### Candidate Side:
*   Upload a CV and a job offer.
*   Receive a suitability score.
*   Missing skills analysis.
*   Suggestions for improvement.

## Technology Stack:

*   **Application Framework & UI:** Streamlit
*   **Core Language:** Python
*   **LLM and Embeddings:** Google Gemini (via Google AI SDK)
*   **Vector Store:** ChromaDB
*   **RAG Orchestration:** LangChain / LlamaIndex
*   **Document Parsing:** PyPDF2, python-docx

## Setup and Installation:

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd SmartRecru
    ```

2.  **Create a virtual environment (recommended):
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # On Windows
    source venv/bin/activate # On macOS/Linux
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure your Gemini API Key:**
    Create a `.env` file in the root directory of the project and add your Gemini API key:
    ```
    GEMINI_API_KEY="YOUR_API_KEY"
    ```
    Replace `YOUR_API_KEY` with your actual Gemini API key.

5.  **Run the Streamlit application:**
    ```bash
    streamlit run app.py
    ```

## Project Structure:

```
.
├── .env
├── app.py
├── config.py
├── GEMINI.md
├── README.md
├── requirements.txt
├── data/
│   ├── cvs/
│   └── job_offers/
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── matching.py
│   │   ├── summarization.py
│   │   └── qa.py
│   ├── pipelines/
│   │   ├── __init__.py
│   │   ├── extraction.py
│   │   ├── preprocessing.py
│   │   └── ner.py
│   └── utils/
│       ├── __init__.py
│       ├── document_parser.py
│       ├── embedding_generator.py
│       └── rag_pipeline.py
└── notebooks/
```

## File Explanations

*   **`app.py`**: The main entry point for the Streamlit web application.
*   **`config.py`**: Stores configuration variables for the project.
*   **`requirements.txt`**: Lists the Python dependencies for the project.
*   **`.env`**: Holds environment variables, such as API keys.
*   **`data/`**: Directory for storing data, with subdirectories for CVs and job offers.
*   **`src/`**: Contains the main source code for the project.
    *   **`src/core/`**: Core application logic.
        *   `matching.py`: Handles semantic matching and skill gap analysis.
        *   `summarization.py`: Generates summaries of CVs.
        *   `qa.py`: Implements the RAG-based Q&A functionality.
    *   **`src/pipelines/`**: Contains data processing pipelines.
        *   `extraction.py`: Extracts text from documents.
        *   `preprocessing.py`: Cleans and preprocesses text data.
        *   `ner.py`: Performs Named Entity Recognition.
    *   **`src/utils/`**: Contains utility functions.
        *   `document_parser.py`: Parses text from different file formats (PDF, DOCX).
        *   `embedding_generator.py`: Generates text embeddings.
        *   `rag_pipeline.py`: Implements the Retrieval-Augmented Generation pipeline.
*   **`notebooks/`**: Contains Jupyter notebooks for experimentation and analysis.
*   **`README.md`**: This file, providing an overview of the project.
