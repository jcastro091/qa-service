# Member QA — Natural-language Q&A over Member Messages

A lightweight **FastAPI** service that answers natural-language questions about members using the public `/messages` API.  
It returns an answer **plus evidence** (the originating message) and a confidence score.

🌐 **Live Demo:** [https://qa-service-ij3z.onrender.com/ui/](https://qa-service-ij3z.onrender.com/ui/)

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
git clone https://github.com/jcastro091/qa-service.git
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

Example:
```bash
curl -s "https://qa-service-ij3z.onrender.com/ask?question=When%20is%20Armand%20going%20to%20Milan%3F"
```

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

### Alternative Approaches Considered

1. **Vector Search (Embeddings + FAISS)**
2. **RAG (Retrieval-Augmented Generation)**
3. **spaCy + Duckling IE Pipeline**
4. **Fine-tuned Intent + Slot Model**

**Reason chosen:** deterministic, fast, and interpretable—ideal for a short take-home and easy to extend.

---

## 📊 Data Insights (Bonus 2)

| Observation | Detail |
|--------------|---------|
| Redirect behavior | `/messages` 302 redirects handled with `follow_redirects=True`. |
| Schema inconsistency | Some use `message` instead of `text`, or `user_name` instead of `member_name`. |
| Temporal inconsistencies | Mixed timestamp formats; normalized internally. |
| Sparse facts | Missing facts correctly yield confidence `0.0`. |
| Lexical ambiguity | “Layla” + “London” handled via fuzzy matching. |

Run analysis locally:
```bash
python scripts/evaluate.py
```

---

## 🌍 Deploy (Render)

The live deployment is hosted on Render’s free tier.  
Follow these steps to reproduce:

1. Fork or clone this repo.  
2. Create a new Web Service on [Render](https://render.com/).  
3. **Runtime:** Python 3.x  
4. **Build Command:**  
   ```bash
   pip install -r requirements.txt
   ```  
5. **Start Command:**  
   ```bash
   gunicorn -k uvicorn.workers.UvicornWorker app.main:app
   ```  
6. **Environment Variables:**
   ```
   MESSAGES_API_URL=https://november7-730026606190.europe-west1.run.app/messages
   ```
7. Wait for build → visit your public URL, e.g.:  
   [https://qa-service-ij3z.onrender.com/ui/](https://qa-service-ij3z.onrender.com/ui/)

---

## 🧱 Stack

- **Backend:** Python 3.11 + FastAPI + Uvicorn  
- **Frontend:** Vanilla HTML/CSS/JS  
- **Libraries:** httpx, rapidfuzz, dateparser, gunicorn  
- **Infra:** Render (Free Tier)

---

## ✨ Why This Submission Stands Out

- **Publicly hosted + working demo**
- **Evidence-first answers** → transparent and auditable  
- **Polished frontend** → product sense & UX awareness  
- **Robust retriever** → handles API quirks gracefully  
- **Design notes & data insights** → clear engineering reasoning  

---

## 👤 Author

**John Castro**  
GitHub: [@jcastro091](https://github.com/jcastro091)  
Email: [JCastro091@gmail.com](mailto:JCastro091@gmail.com)
