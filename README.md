# Rulebook QA Assistant

## Overview
The Rulebook QA Assistant is an intelligent Retrieval-Augmented Generation (RAG) service designed to answer questions based strictly on a university rulebook corpus. Unlike standard LLM chatbots, this system does not blindly generate confident answers or hallucinate facts. It strictly adheres to the provided knowledge base and exposes the exact evidence used to construct its responses.

The system deterministically returns one of three possible response types:
- **`ANSWERED`**: The corpus contains sufficient evidence, and a grounded answer is provided.
- **`NOT_COVERED`**: The corpus lacks the necessary information. The system safely refuses to invent an answer.
- **`CONFLICT`**: The corpus contains explicitly contradictory rules. Both conflicting provisions are highlighted for manual resolution.

## Assignment Requirements
This project fulfills the core requirements of an AI Developer assignment by providing:
- A `POST /ask` endpoint built with FastAPI.
- A comprehensive rulebook corpus consisting of over 7,216 words.
- Multi-format data ingestion including Markdown, PDF, and CSV sources.
- 3 intentionally planted rule contradictions accurately detected.
- 25 intentionally unanswered questions safely identified as out-of-scope.
- High-fidelity passage-level citations and evidence extraction.
- Granular section, page, and row references.
- Normalized semantic similarity scores for transparency.
- A clean, vanilla HTML/CSS/JavaScript web UI.

## Architecture
The system operates on a linear RAG orchestration pipeline:
1. **User Question**: Input from the frontend or direct API request.
2. **FastAPI**: Validates the input using Pydantic schemas.
3. **RAG Orchestrator**: Manages the flow of the request.
4. **ChromaDB Retrieval**: Extracts the top 5 most semantically relevant chunks using Gemini embeddings.
5. **Conflict Detection**: Scans the retrieved context against known contradictions before hitting the LLM.
6. **Grounded Gemini Generation**: If no conflict exists, the LLM evaluates the context. If insufficient, it aborts. Otherwise, it synthesizes the final answer.
7. **Structured Response**: Packages the status, text, and rich source metadata.
8. **Frontend**: Dynamically renders the response and metadata.

## Technology Stack
- **Python 3.11.9**
- **uv**: Lightning-fast Python package and project manager
- **FastAPI & Pydantic**: Robust API framework and data validation
- **LangChain**: RAG tooling and chunking
- **Gemini Embedding 2**: State-of-the-art semantic embedding model
- **Gemini 3.5 Flash-Lite**: Fast, cost-efficient generative model for grounded synthesis
- **ChromaDB**: Persistent, local vector database
- **HTML / CSS / Vanilla JavaScript**: Minimalist frontend without heavy framework dependencies

## Project Structure
```text
rulebook-qa-system/
├── .env.example
├── README.md
├── pyproject.toml
├── uv.lock
├── app/
│   ├── main.py
│   ├── api/
│   ├── models/
│   ├── services/
│   └── utils/
├── data/
│   └── rulebook/
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
└── tests/
    └── unanswered_questions.md
```

## Corpus
The knowledge base comprises exactly six source files, totaling approximately 7,216 words:
- `academic_regulations.md`
- `attendance_policy.md`
- `examination_rules.md`
- `hostel_rules.md`
- `scholarship_policy.pdf`
- `fee_deadlines.csv`

*(Note: The `conflicts.json` file located in the rulebook directory acts strictly as metadata configuration for the conflict detector and is **not** treated as a knowledge source).*

## Retrieval and Similarity Scores
The local ChromaDB instance uses the configured distance metric internally. To ensure an intuitive user experience, the system converts this distance into a normalized **similarity score**, where a higher score indicates a better semantic match.

The retrieved evidence exposes precise metadata, including:
- Source filename (e.g., `attendance_policy.md`)
- Hierarchical section/header (e.g., `2. Attendance Policy > 2.2 Attendance Calculation`)
- Page number (for PDFs when available)
- Row number (for CSVs when available)
- Similarity score
- The exact retrieved passage

## Conflict Detection
The system is engineered to detect explicitly planted anomalies. Rather than silently choosing one rule over another, it explicitly highlights the contradiction. 

There are 3 intentionally planted conflicts:
- **Attendance**: One provision mandates a 75% minimum attendance, while another allows a 60% medical exemption.
- **Fee Deadline**: One provision states March 10, 2027, while another states March 15, 2027.
- **Hostel Curfew**: One section mandates a 10:00 PM curfew, while another allows entry up to 11:00 PM without penalty.

## NOT_COVERED Behavior
Hallucination prevention is a critical feature. When a user asks a question whose answer is not fully present within the ingested corpus, the system explicitly refuses to guess and returns `NOT_COVERED`. A suite of 25 intentionally unanswered questions has been prepared in `tests/unanswered_questions.md` to validate this constraint.

## API Usage
**Endpoint**: `POST /ask`

**Example Request**:
```json
{
  "question": "How is attendance percentage calculated?"
}
```

**Example Response Structure**:
```json
{
  "status": "ANSWERED",
  "answer": "Attendance percentage for a course is calculated as...",
  "sources": [
    {
      "source": "attendance_policy.md",
      "section": "2. Attendance Policy > 2.2 Attendance Calculation",
      "similarity_score": 0.7241,
      "content": "Attendance percentage for a course is calculated as..."
    }
  ]
}
```

---

## Prerequisites
Before you begin, ensure you have the following installed:
- **Git**: For downloading the repository.
- **Python 3.11.9**: This is the recommended version for this project. Verify your installation by running `python --version` in your terminal.
- **uv**: `uv` is the lightning-fast Python package and project manager used by this project. Please follow the official `uv` installation documentation: [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/). Verify your installation by running `uv --version`.
- **Gemini API Key**: A free-tier Google AI Studio API key.

## Download the Project
You can download the project to your local machine using either Git or by downloading the ZIP file directly.

**Option 1 — Git:**
1. Open a terminal.
2. Clone the public repository:
   ```bash
   git clone <YOUR_PUBLIC_GITHUB_URL>
   ```
3. Enter the project directory:
   ```bash
   cd rulebook-qa-system
   ```

**Option 2 — ZIP:**
1. Open the GitHub repository in a browser (`<YOUR_PUBLIC_GITHUB_URL>`).
2. Click **Code** → **Download ZIP**.
3. Extract the ZIP file to your preferred location.
4. Open a terminal inside the extracted `rulebook-qa-system` folder.

## Verify Project Directory
Ensure you are in the correct directory. Run `dir` on Windows or `ls` on macOS/Linux. 
You should see files and folders such as:
- `app`
- `data`
- `frontend`
- `tests`
- `pyproject.toml`
- `README.md`
- `uv.lock`

**Important**: All of the following commands must be run from this exact project root (`rulebook-qa-system/`).

## Configure the Gemini API Key
The application requires a valid Google AI Studio key to generate text embeddings and answers.
1. Make a copy of the `.env.example` file located in the project root.
2. Name the copied file `.env`.
3. Open `.env` in a text editor.
4. Replace the placeholder with your actual Gemini API key:
   ```env
   GEMINI_API_KEY=your_actual_key_here
   ```

*Security Note: Never commit the `.env` file or upload your real API key to GitHub. The `.env` file is already safely ignored by the `.gitignore` configuration.*

## Install Dependencies
From the project root terminal, run:
```bash
uv sync
```
*Note: `uv sync` creates and updates the project's virtual environment and perfectly installs the exact dependencies defined by `pyproject.toml` and locked by `uv.lock`.*

## Start the Backend
Keep your terminal open at the project root and run the following command to start the API:
```bash
uv run uvicorn app.main:app --reload
```
- The FastAPI application is now running at `http://127.0.0.1:8000`.
- The interactive Swagger API documentation is available at `http://127.0.0.1:8000/docs`.

**Keep this terminal running.**

## Start the Frontend
Open a **SECOND terminal** window.
Navigate to the exact project root and then enter the frontend directory:
```bash
cd rulebook-qa-system
cd frontend
```
Then, start the frontend server by running:
```bash
python -m http.server 8080
```
*Note: The frontend is a static HTML/CSS/JavaScript application, so Python's built-in HTTP server is perfectly sufficient to serve it locally.*

**Keep this second terminal running.**

## Running the Application
With your two-terminal setup active:
- **Terminal 1**: Running the FastAPI backend from the project root.
- **Terminal 2**: Serving the Python HTTP server from the frontend directory.

1. Open your browser and navigate to `http://127.0.0.1:8080`.
2. Enter a question regarding the university rulebook into the text area.
3. Click **Ask**.
4. The frontend will send a `POST /ask` request to the running FastAPI backend.
5. The application will process your request and dynamically display:
   - The status badge (`ANSWERED`, `CONFLICT`, or `NOT_COVERED`).
   - The generated textual answer.
   - The exact source files used.
   - Granular section, page, or row metadata.
   - The normalized similarity score.
   - The verbatim retrieved passage.

## Troubleshooting

- **`uv is not recognized`**
  → `uv` is not installed or your terminal needs to be restarted to recognize path changes. Follow the official `uv` installation documentation linked in Prerequisites.
- **`python is not recognized`**
  → Python is not installed or not available in your system PATH.
- **Gemini Authentication Error**
  → Check your `.env` file and confirm `GEMINI_API_KEY` is correct. Ensure there are no quotation marks or spaces around the key. Never paste the API key directly into the source code.
- **Port 8000 already in use**
  → Stop the existing FastAPI process taking up port 8000 in your background tasks, or use another port consistently across the frontend configuration.
- **Frontend cannot reach API**
  → Confirm FastAPI is actively running on `http://127.0.0.1:8000`. Confirm the frontend is being served from `http://127.0.0.1:8080`. Ensure CORS configuration remains enabled in `app/main.py`.

---

## Example Questions
Test the capabilities of the system using these representative questions:

- **ANSWERED**: *"How is attendance percentage calculated?"*
- **CONFLICT**: *"What is the hostel curfew?"*
- **NOT_COVERED**: *"What is the university's policy for credit transfer from another university?"*

## Testing
Extensive manual and automated verification has been performed throughout development:
- **Vector Storage**: 92 distinct chunks embedded and permanently persisted in ChromaDB.
- **Retrieval Engine**: Verified mapping of source names, similarity scores, and strict metadata isolation.
- **Conflict Handling**: Verified deterministic resolution bypassing the LLM.
- **LLM Safety**: Grounded generation verification utilizing the 25 unanswered questions logged in `tests/unanswered_questions.md`.
- **Integration**: Full end-to-end FastAPI endpoint and frontend UI HTTP tests.

## Security
- The `GEMINI_API_KEY` is loaded dynamically via environment variables (`os.getenv`).
- The `.env` file is gitignored to prevent accidental exposure.
- `.env.example` contains only a placeholder.
- API keys must never be committed to source control.

## Limitations
- **Generation Quotas**: The system relies on Google's Gemini API free tier. Intensive usage may trigger `429 RESOURCE_EXHAUSTED` or `503 UNAVAILABLE` errors. The application gracefully catches these limits, returning them as `status: ERROR`.
- **Embeddings**: Unlike the generation model, the initial corpus embeddings are pre-calculated and stored locally in ChromaDB, preventing redundant ingestion API costs on startup.
