# NetSage-AI-Troubleshooter

A Unified Web Application built with Streamlit and Python designed for automated Cisco network configuration troubleshooting, structured LLM-based diagnostics, and human-in-the-loop verification logging.

---

## 🚀 Key Features

* **Interactive Troubleshooting Interface**: Switch between different network anomaly cases (e.g., Guest Wi-Fi issues, WAN link configuration errors) and review raw symptoms and IOS config outputs.
* **Deterministic Rule Checker**: Instant rule-based checks written in Python that identify obvious errors—such as `/32` host masks and administratively down interfaces—before invoking the AI.
* **NetSage AI Diagnosis**: Integration with the Anthropic Claude API via a structured system prompt (`diagnose_prompt.md`), returning a predictable JSON payload detailing the root cause, OSI layer, confidence level, evidence line, next test command, and exact fix steps. Includes a robust fallback mechanism to simulated diagnosis configurations.
* **Human-in-the-Loop Oversight**: A review form for human network operators to accept, reject, or edit the AI-generated recommendations, recording verification notes in real-time.
* **Responsible AI Metrics Dashboard**: Interactive analytics and charts (powered by Plotly) displaying running AI agreement rates, status distributions (Donut charts), timeline trends, and a fully searchable audit log.
* **Modern Zinc Design System**: A responsive dashboard interface following modern web standards, featuring light/dark theme toggles, KPI metric cards, and clean typography.

---

## 📂 File Structure

* **`app.py`**: The core Streamlit web application orchestrating the UI tabs, forms, charts, and pages.
* **`checker.py`**: Contains deterministic, string-matching, and regex-based configuration checkers.
* **`database.py`**: Handles SQLite database connections for the human audit logging system (`reviews.db`), pre-seeded with initial telemetry reviews to populate dashboard visuals.
* **`cases.csv`**: A structured database of Cisco network troubleshooting cases, configurations, symptoms, and fallback mock AI responses.
* **`diagnose_prompt.md`**: The system instructions forcing the AI engine to output predictable JSON formats.
* **`requirements.txt`**: Lists all project dependencies.
* **`.gitignore`**: Excludes local virtual environments and database states.

---

## 🛠️ Setup & Running Locally

### 1. Prerequisites
Ensure you have **Python 3.10+** installed on your system.

### 2. Create Virtual Environment
Initialize a Python virtual environment to manage dependencies cleanly:
```bash
python -m venv .venv
```

Activate the environment:
* **Windows (PowerShell)**: `.venv\Scripts\activate.ps1`
* **Windows (CMD)**: `.venv\Scripts\activate.bat`
* **macOS / Linux**: `source .venv/bin/activate`

### 3. Install Dependencies
Install all required libraries, including Streamlit, Plotly, Pandas, and the Anthropic API client:
```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit Application
Start the server:
```bash
streamlit run app.py
```
Open your browser and navigate to the local URL (usually `http://localhost:8501`).
