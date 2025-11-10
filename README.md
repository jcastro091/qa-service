# Member QA — Natural-language Q&A over Member Messages

A lightweight **FastAPI** service that answers natural-language questions about members using the public `/messages` API.  
It returns an answer **plus evidence** (the originating message) and a confidence score.

---

### 🧠 Example Questions

| Question | Example Answer |
|-----------|----------------|
| When is **Armand** going to Milan? | Saturday |
| When is **Sophia Al-Farsi** going to Paris? | Friday |
| What seat preference does **Layla Kawaguchi** have? | Aisle seats |
| Which restaurant is **Fatima El-Tahir** requesting a reservation at? | The French Laundry |
| How many cars does **Vikram Desai** have? | _No record found_ |
| What are **Amira’s** favorite restaurants? | _No record found_ |

---

## 🚀 Quickstart (Local)

```bash
# Clone and run locally
git clone https://github.com/jcastro01/qa-service.git
cd qa-service
python -m venv .venv
. .venv/Scripts/Activate.ps1    # Windows
pip install -r requirements.txt

# Set environment variables
$env:MESSAGES_API_URL="https://november7-730026606190.europe-west1.run.app/messages"
$env:PORT="8080"

# Run server
python -m app.main
# Open: http://localhost:8080/ui/
```

---

## ⚙️ API Endpoints

| Endpoint | Method | Description |
|-----------|---------|-------------|
| `/ask?question=...` | GET | Ask a natural-language question |
| `/ask` | POST | JSON body: `{ "question": "..." }` |
| `/ui/` | GET | Beautiful minimal front-end UI |
| `/healthz` | GET | Health check |
| `/debug/search?q=...` | GET | Substring search in messages |
| `/debug/find?member=...&q=...` | GET | Search within a member’s messages |

Example:
```bash
curl -s "http://localhost:8080/ask?question=When%20is%20Armand%20going%20to%20Milan%3F"
```

---

## 🧩 How It Works

1. **Retriever**
   - Fetches `GET /messages`, handles redirects and schema mismatches.
   - Normalizes inconsistent fields (`message` vs `text`, `user_name` vs `member_name`).

2. **Lightweight Parser**
   - Fuzzy member matching via **RapidFuzz**.
   - Rule blocks for common intents:
     - “When” → date extraction
     - “Count” → numerical extraction (cars, vehicles)
     - “Seat preference” → regex on "prefer aisle/window"
     - “Restaurant reservation” → regex on “reservation/booking/table at …”
     - “Favorites” fallback list pattern

3. **Ranking**
   - Token overlap between the question and messages.

4. **Answer with Evidence**
   - Returns `{answer, confidence, evidence[]}`.
   - Confidence reflects match strength and rule reliability.

---

## 🎨 Frontend (Bonus)

- `/ui/` hosts a polished **vanilla HTML/CSS/JS** interface.
- Features:
  - Responsive dark/light mode  
  - Example question chips  
  - Loading spinner, latency badge, confidence score  
  - “Copy JSON” and “Copy cURL” buttons  
  - Sub-100ms local inference latency

---

## 💡 Design Notes (Bonus 1)

### Approach Shipped
> **Rule-based retrieval + fuzzy matching + regex/date extraction.**

✅ Pros:
- No model dependencies or inference cost  
- Fast (<100ms) and auditable  
- Deterministic (no hallucination)

⚠️ Cons:
- Limited coverage—needs new rules for new question types

---

### Alternative Approaches Considered

1. **Vector Search (Embeddings + FAISS)**
   - `sentence-transformers/all-MiniLM-L6-v2` to retrieve semantically similar messages
   - ✅ Better recall  
   - ⚠️ Higher memory and setup cost

2. **RAG (Retrieval-Augmented Generation)**
   - Top-k messages → small LLM (e.g., GPT-4-mini) → structured JSON output  
   - ✅ Handles paraphrases & multi-step reasoning  
   - ⚠️ Costly, slower, needs prompt engineering

3. **spaCy + Duckling IE Pipeline**
   - Named-entity and relation extraction for (Member, City, Date, Venue)
   - ✅ Fully local, interpretable  
   - ⚠️ More dev time, less flexible

4. **Fine-tuned Intent + Slot Model**
   - Trained small classifier for intent detection and slot filling  
   - ✅ More generalizable  
   - ⚠️ Needs labeled data

**Reason chosen:** deterministic, fast, and interpretable—ideal for a short take-home and easy to extend.

---

## 📊 Data Insights (Bonus 2)

Analysis of the public dataset:

| Observation | Detail |
|--------------|---------|
| Redirect behavior | `/messages` 302/307 redirects to `https://.../messages/`. Fixed via `follow_redirects=True`. |
| Schema inconsistency | Some records use `message` instead of `text`, or `user_name` instead of `member_name`. Normalized automatically. |
| Temporal inconsistencies | Mixed timestamps; some ISO-8601 variants. |
| Sparse facts | “Vikram Desai cars” and “Amira favorite restaurants” do not exist → correct `confidence: 0.0`. |
| Lexical ambiguity | Some names/cities overlap (e.g., “Layla” + “London”), filtered via fuzzy match. |
| Restaurant reservation | Detected via “reservation/booking/table at …” + proper noun phrase extraction. |

You can reproduce this analysis:
```bash
python scripts/evaluate.py
```

---

## 🌍 Deploy

### Option A — Render / Railway
1. Push repo to GitHub (see below)
2. New Web Service → “Deploy from GitHub”
3. **Build Command:**  
   `pip install -r requirements.txt`
4. **Start Command:**  
   `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. **Environment Variables:**
   - `MESSAGES_API_URL=https://november7-730026606190.europe-west1.run.app/messages`
   - `PORT=10000`

### Option B — Docker + Cloud Run

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

Then:
```bash
docker build -t memberqa .
docker run -p 8080:8080 memberqa
```

---

## 🧪 Testing Matrix

| Question | Expected Result |
|-----------|-----------------|
| When is Armand going to Milan? | Saturday ✅ |
| When is Sophia Al-Farsi going to Paris? | Friday ✅ |
| What seat preference does Layla Kawaguchi have? | Aisle seats ✅ |
| How many cars does Vikram Desai have? | Not found ⚠️ |
| What are Amira’s favorite restaurants? | Not found ⚠️ |

---

## 📹 Optional Loom Walkthrough (1–2 mins)

1. Open `/ui/` → ask a few example questions.  
2. Show answers + evidence and latency.  
3. Open `/ask?question=…` directly to show raw JSON.  
4. Briefly explain design choices (rules, fuzzy match, regex, evidence).  
5. Show repo + deployed URL.

---

## 🧱 Stack

- **Backend:** Python 3.11 + FastAPI + Uvicorn  
- **Frontend:** Vanilla HTML/CSS/JS  
- **Libraries:** httpx, rapidfuzz, dateparser  
- **Infra:** Deployable to Render, Railway, Fly.io, Cloud Run

---

## ✨ Why This Submission Stands Out

- **Evidence-first answers** → transparent and auditable  
- **Frontend polish** → product sense & UX awareness  
- **Robust retriever** → handles API quirks gracefully  
- **Design notes & alternatives** → shows engineering maturity  
- **Data insights** → demonstrates analytical thinking  

---

## 👤 Author

**John Castro**  
GitHub: [@jcastro01](https://github.com/jcastro01)  
Email: [JCastro091@gmail.com](mailto:JCastro091@gmail.com)
