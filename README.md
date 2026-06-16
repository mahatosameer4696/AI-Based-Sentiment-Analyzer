# 🧠 AI Sentiment Analyzer

> A professional AI-powered web application that detects the **sentiment** (Positive, Negative, or Neutral) of any text — reviews, comments, tweets, or feedback — using **Hugging Face Transformers** and **Flask**.

---

## 📸 Features

| Feature | Description |
|---|---|
| 🔍 **Sentiment Analysis** | Powered by `distilbert-base-uncased-finetuned-sst-2-english` |
| 📊 **Confidence Score** | Visual progress bar showing model certainty |
| 🗃️ **SQLite Database** | Auto-created; stores all analyses with timestamps |
| 📜 **History Page** | Browse all previous analyses in a searchable table |
| 🔎 **Live Search** | Filter history by text or sentiment in real time |
| 🗑️ **Delete Records** | Remove individual analyses with confirmation |
| 📥 **CSV Export** | Download all (or filtered) results as a CSV file |
| 💡 **Sample Texts** | One-click sample inputs to try the analyzer |
| ⌨️ **Keyboard Shortcut** | `Ctrl + Enter` to run analysis instantly |
| 📱 **Fully Responsive** | Works perfectly on desktop, tablet, and mobile |

---

## 🗂️ Project Structure

```
sentiment-analyzer/
│
├── app.py                  # Flask backend — routes, model, DB logic
├── requirements.txt        # Python dependencies
├── database.db             # SQLite DB (auto-created on first run)
│
├── static/
│   └── style.css           # Custom CSS (glassmorphism dark theme)
│
├── templates/
│   ├── index.html          # Home page — analysis form + results
│   └── history.html        # History page — table, search, export
│
└── README.md               # This file
```

---

## ⚙️ Installation & Setup

### Prerequisites
- Python **3.9+**
- pip (Python package manager)
- Internet connection (first run downloads the ML model ~268 MB)

---

### Step 1 — Clone / Download the Project

```bash
# If using git:
git clone https://github.com/yourusername/sentiment-analyzer.git
cd sentiment-analyzer

# OR simply navigate to the project folder:
cd sentiment-analyzer
```

---

### Step 2 — Create a Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

---

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

> ⏳ **Note:** PyTorch and Transformers are large packages. Installation may take a few minutes.

---

### Step 4 — Run the Application

```bash
python app.py
```

You should see:

```
[DB]    Database initialized successfully.
[MODEL] Loading sentiment analysis model... (this may take a moment)
[MODEL] Model loaded successfully.
[APP]   Starting Sentiment Analyzer at http://127.0.0.1:5000
```

> 🌐 Open your browser and go to: **http://127.0.0.1:5000**

---

## 🚀 Usage

1. **Home Page** → Enter any text in the text area and click **Analyze Sentiment**.
2. **Result** → See the sentiment (Positive/Negative/Neutral) with a confidence score.
3. **History** → Click "History" in the navbar to see all previous analyses.
4. **Search** → Type in the search box to filter records by text or sentiment.
5. **Export** → Click **Export CSV** to download results as a spreadsheet.
6. **Delete** → Click the 🗑️ icon to remove any record permanently.

---

## 🧬 Model Information

| Property | Value |
|---|---|
| **Model Name** | `distilbert-base-uncased-finetuned-sst-2-english` |
| **Source** | [Hugging Face Hub](https://huggingface.co/distilbert-base-uncased-finetuned-sst-2-english) |
| **Task** | Text Classification (Sentiment Analysis) |
| **Size** | ~268 MB |
| **Languages** | English |
| **Labels** | POSITIVE, NEGATIVE (NEUTRAL derived from low confidence) |

---

## 🗃️ Database Schema

```sql
CREATE TABLE analyses (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    text        TEXT    NOT NULL,       -- Input text (up to 5000 chars)
    sentiment   TEXT    NOT NULL,       -- 'Positive', 'Negative', 'Neutral'
    confidence  REAL    NOT NULL,       -- Confidence score (0.00 – 100.00)
    created_at  TEXT    NOT NULL        -- 'YYYY-MM-DD HH:MM:SS'
);
```

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Home page |
| `POST` | `/analyze` | Run sentiment analysis (JSON) |
| `GET` | `/history` | History page (optional `?q=search`) |
| `POST` | `/delete/<id>` | Delete a record |
| `GET` | `/export` | Download CSV (optional `?q=search`) |
| `GET` | `/stats` | Summary statistics (JSON) |

### `/analyze` Request Format
```json
POST /analyze
Content-Type: application/json

{ "text": "Your text here..." }
```

### `/analyze` Response Format
```json
{
  "id": 42,
  "text": "Your text here...",
  "sentiment": "Positive",
  "confidence": 98.76,
  "timestamp": "2024-06-15 11:30:00"
}
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | HTML5, CSS3 (Glassmorphism), Bootstrap 5, Font Awesome 6 |
| **Backend** | Python 3, Flask 3 |
| **AI / ML** | Hugging Face Transformers, DistilBERT |
| **Database** | SQLite3 (built-in Python) |
| **Fonts** | Google Fonts — Inter, Poppins |

---

## ❗ Troubleshooting

**Model download fails?**
```bash
# Manually cache the model
python -c "from transformers import pipeline; pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')"
```

**Port 5000 already in use?**
```bash
# Change port in app.py (last line):
app.run(debug=True, host="0.0.0.0", port=5001)
```

**ModuleNotFoundError?**
```bash
# Make sure virtual environment is activated, then:
pip install -r requirements.txt
```

---

## 📄 License

This project is open-source and available under the **MIT License**.

---

## 👤 Author

Developed as a professional internship submission project demonstrating:
- RESTful Flask API design
- NLP / Deep Learning integration
- Full-stack web development
- Database design and management

---

> ⭐ If you found this project helpful, give it a star!
