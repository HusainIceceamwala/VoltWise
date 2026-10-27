# VoltWise AI

VoltWise AI is an intelligent electricity bill analysis app built with Python and Streamlit. It helps users upload electricity bills, extract key billing data using OCR, parse the information, estimate appliance usage, and receive AI-powered recommendations to reduce energy consumption.

## Why this project exists

Electricity bills often contain important information buried in PDFs or scanned images. This project turns that information into something actionable by combining:

- OCR for document extraction
- Rule-based parsing for billing fields
- Local LLM analysis for energy insights
- Analytics and charts for energy trends
- A lightweight database for bill history

## Features

- Upload electricity bill images or PDFs
- Extract text using Tesseract and Poppler
- Parse consumer number, bill date, units, and total amount
- Analyze energy usage with Ollama and local LLM models
- Compare current bill against household appliance consumption
- Identify likely high-energy appliances
- Estimate savings and reduction opportunities
- View historical bill trends and summary analytics
- Store entries in SQLite by default, with MySQL support available
- Generate downloadable reports and CSV exports

## Tech stack

- Python
- Streamlit
- OpenCV / Pillow
- Tesseract OCR
- Poppler
- Pandas / NumPy
- Plotly
- Ollama + local LLM model
- SQLAlchemy
- ReportLab

## Project structure

```text
VoltWise-AI-main/
├── app.py                  # Streamlit application
├── analytics.py            # History and summary analytics logic
├── charts.py               # Charts and visualizations
├── database.py             # SQLite/MySQL database operations
├── llm.py                 # Ollama-powered bill analysis
├── ocr.py                 # OCR and preprocessing logic
├── parser.py              # Extraction of bill fields
├── report.py              # Report generation logic
├── score.py               # Energy scoring logic
├── requirements.txt       # Python dependencies
├── .env.example           # Sample environment variables
├── .gitignore             # Git ignore rules
├── tests/
│   └── test_analytics.py
├── uploads/               # Uploaded files
└── winget_*.txt           # Windows package install helper files
```

## Prerequisites

Before running the app, make sure you have:

- Python 3.10+ installed
- A virtual environment created for the project
- Tesseract OCR installed
- Poppler installed for PDF rendering
- Ollama installed locally
- A supported local model pulled in Ollama, such as:

```bash
ollama pull gemma3:1b
```

## Setup

1. Clone the repository

```bash
git clone https://github.com/HusainIceceamwala/VoltWise.git
cd VoltWise
```

2. Create and activate a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Install OCR dependencies

On Windows, you can use the helper files in the project root for package installation if needed. For the OCR pipeline, install:

- Tesseract
- Poppler

5. Configure the database (optional)

The app defaults to SQLite and will create a local database automatically. If you want MySQL instead, copy the sample file and update it:

```bash
copy .env.example .env
```

Then edit `.env` with your database connection details.

## Run the app

```bash
streamlit run app.py
```

The app will open in your browser and allow you to upload a bill, analyze it, and review energy insights.

## Typical workflow

1. Upload an electricity bill image or PDF
2. Let OCR extract the text
3. Review parsed values such as units and total amount
4. Add household appliance details if needed
5. Run the analysis
6. Review recommendations and scoring
7. Save or export bill history

## Notes

- This project is designed for local use with Ollama and local models.
- SQLite is enabled by default for easy setup.
- The app can be expanded to include more appliance categories and richer reporting.

## License

This project is currently provided as-is for personal and educational use.

## Contributing

Contributions are welcome. If you improve parsing logic, add charts, or optimize the analysis workflow, feel free to open a pull request.
