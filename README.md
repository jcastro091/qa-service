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

---

### Alternative Approaches Considered

#### 1. Vector Search (Embeddings + FAISS)
**Pros:**
- Handles semantically similar phrasing (“trip to London” ≈ “travel plans for London”)  
- Scales efficiently for large datasets with cosine similarity search  
- No manual rules needed for every phrasing  

**Cons:**
- Requires embedding generation and storage overhead  
- Less interpretable; results not always explainable  
- Performance depends on embedding model quality  

#### 2. RAG (Retrieval-Augmented Generation)
**Pros:**
- Combines retrieval with LLM reasoning for natural answers  
- Extremely flexible for unseen or complex question types  
- Can summarize multi-sentence responses  

**Cons:**
- Expensive (LLM API or GPU inference cost)  
- Prone to hallucination if retrieval isn’t filtered  
- Requires guardrails and caching for production  

#### 3. spaCy + Duckling IE Pipeline
**Pros:**
- Great for extracting structured entities (dates, names, cities)  
- Lightweight and deterministic  
- Integrates easily into rule-based systems  

**Cons:**
- Requires tuning custom entity patterns for new data  
- Limited contextual understanding beyond token patterns  

#### 4. Fine-tuned Intent + Slot Model
**Pros:**
- Very accurate for repetitive, domain-specific intents  
- Predictable inference cost, easy to host  
- Excellent for fixed template questions  

**Cons:**
- Needs labeled training data  
- Poor generalization to new phrasings  
- Slower to evolve as schema or domain changes  

✅ **Chosen Approach:**  
Rule-based and fuzzy retrieval offered the **best interpretability, speed, and reliability** for a small dataset — ideal for a short take-home challenge with real-time inference.

---

## 📊 Data Insights (Bonus 2)

| Observation | Detail |
|--------------|---------|
| Redirect behavior | `/messages` endpoint returned 302/307 redirects handled with `follow_redirects=True` |
| Schema inconsistency | Some fields use `message` vs `text`, or `user_name` vs `member_name` |
| Temporal inconsistencies | Mixed timestamp formats normalized internally |
| Sparse facts | Missing or incomplete facts gracefully return confidence `0.0` |
| Lexical ambiguity | Fuzzy matching resolves minor spelling/name variations |

Run locally to inspect data insights:
```bash
python scripts/evaluate.py
```

---

## 🌍 Deployment (Render)

The app is publicly deployed via **Render**:  
👉 [https://qa-service-ij3z.onrender.com/ui/](https://qa-service-ij3z.onrender.com/ui/)

Steps to replicate:

1. Create a **new Web Service** on [Render](https://render.com/).  
2. **Runtime:** Python 3.x  
3. **Build Command:** `pip install -r requirements.txt`  
4. **Start Command:** `gunicorn -k uvicorn.workers.UvicornWorker app.main:app`  
5. Add environment variable:  
   ```
   MESSAGES_API_URL=https://november7-730026606190.europe-west1.run.app/messages
   ```  
6. Deploy and visit your public URL!

---

## 🧱 Stack

- **Backend:** Python 3.11 + FastAPI + Uvicorn  
- **Frontend:** Vanilla HTML/CSS/JS  
- **Libraries:** httpx, rapidfuzz, dateparser, gunicorn  
- **Infra:** Render (Free Tier)

---

## 🚀 Future Improvements

| Enhancement | Description |
|--------------|-------------|
| **LLM Summary Mode** | Add optional `mode=llm` flag to generate contextual summaries via GPT/OpenAI API |
| **Vector Search (FAISS)** | Enable semantic retrieval across similar phrasing or context |
| **Advanced NER (Duckling + spaCy)** | Extract richer entity types (e.g., restaurant names, dates, flights) |
| **/metrics Endpoint** | Return dataset stats and latency metrics for observability |
| **Conversational Memory** | Maintain session context to support follow-up questions |
| **CI/CD + Dockerization** | Add GitHub Actions for automated test & deploy to Render |

These additions would evolve this app into a **production-grade retrieval-augmented agent**, ready for Aurora-scale internal knowledge systems.

---

## 👤 Author

**John Castro**  
GitHub: [@jcastro091](https://github.com/jcastro091)  
Email: [JCastro091@gmail.com](mailto:JCastro091@gmail.com)
