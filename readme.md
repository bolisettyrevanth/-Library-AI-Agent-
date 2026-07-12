# 📚 Library AI Agent

> An AI-powered smart library management system built with **Python Flask** and **IBM watsonx.ai** using IBM Granite foundation models. Designed to help students instantly find the most suitable books and learning resources based on their academic needs.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 Student Login | Secure session-based authentication |
| 🏠 Home Page | Project introduction with hero section and recent books |
| 📊 Student Dashboard | Personalised stats, reservations, and branch-specific picks |
| 🔍 Smart Search | Search by title, author, subject, category, or keyword |
| 🤖 AI Chat Assistant | Natural language book recommendations via IBM Granite |
| 📖 Book Details | Full info — edition, publication, shelf location |
| ✅ Real-time Availability | Live copy count and availability status |
| 🔖 Reserve Books | One-click reservation for available books |
| ⏳ Waitlist | Automatic waitlist when a book is unavailable |
| 📚 Similar Books | Curated similar book suggestions per title |
| 🌐 Online Resources | AI-suggested online learning resources |
| 📬 Contact Librarian | Direct message form for library queries |

---

## 🤖 AI Capabilities

LibraryBot (powered by **IBM Granite 3.8B Instruct**) can:

- Understand natural language queries
- Recommend books by **branch** (CSE, ECE, ME, …) and **semester**
- Suggest books for specific **syllabus topics**
- Recommend **Beginner → Intermediate → Advanced** books
- Suggest **reference books**
- Recommend **similar alternatives** if a book is unavailable
- Suggest **online learning resources**
- Explain **why each book is recommended**
- Answer library-related questions politely
- Maintain **conversation history** throughout the session

---

## 🗂️ Project Structure

```
library_ai_agent/
├── app.py                  # Flask application + watsonx.ai integration
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── README.md               # This file
│
├── templates/
│   ├── base.html           # Base layout (navbar, footer)
│   ├── login.html          # Student login page
│   ├── index.html          # Home page
│   ├── dashboard.html      # Student dashboard
│   ├── search.html         # Book search & filter
│   ├── book_detail.html    # Book detail page
│   ├── chat.html           # AI chat interface
│   └── contact.html        # Contact librarian
│
└── static/
    ├── css/
    │   └── style.css       # Main stylesheet (Bootstrap 5 + custom)
    ├── js/
    │   ├── main.js         # Dark mode, toast notifications
    │   └── chat.js         # Chat interface logic
    └── images/             # Static assets (place your images here)
```

---

## 🚀 Quick Start

### 1. Clone or Download

```bash
cd library_ai_agent
```

### 2. Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env
```

Now open `.env` and fill in your credentials:

```env
IBM_API_KEY=your_actual_ibm_api_key
WATSONX_PROJECT_ID=your_actual_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-3-8b-instruct
SECRET_KEY=a_long_random_secret_string
FLASK_ENV=development
PORT=5000
```

### 5. Run the Application

```bash
python app.py
```

Open your browser and navigate to: **http://localhost:5000**

---

## 🔑 IBM Credentials Setup

### Step 1 — IBM Cloud API Key
1. Go to [https://cloud.ibm.com/iam/apikeys](https://cloud.ibm.com/iam/apikeys)
2. Click **Create an IBM Cloud API key**
3. Copy the key and paste it as `IBM_API_KEY` in `.env`

### Step 2 — watsonx.ai Project ID
1. Go to [https://dataplatform.cloud.ibm.com/](https://dataplatform.cloud.ibm.com/)
2. Open or create a **watsonx.ai project**
3. Go to **Manage → General** tab
4. Copy the **Project ID** and paste it as `WATSONX_PROJECT_ID` in `.env`

### Step 3 — Service URL
- Default Dallas region: `https://us-south.ml.cloud.ibm.com`
- Frankfurt: `https://eu-de.ml.cloud.ibm.com`
- London: `https://eu-gb.ml.cloud.ibm.com`
- Tokyo: `https://jp-tok.ml.cloud.ibm.com`

---

## 👤 Demo Login Credentials

| Username | Password | Profile |
|---|---|---|
| `demo` | `demo` | CSE, Semester 3 |
| `student1` | `pass123` | CSE, Semester 5 |
| `student2` | `pass123` | ECE, Semester 3 |

---

## 🎨 Customising the AI Agent

Open `app.py` and edit the `AGENT_INSTRUCTIONS` dictionary at the top:

```python
AGENT_INSTRUCTIONS = {
    "personality":          "...",  # Agent name & character
    "recommendation_style": "...",  # How books are listed
    "academic_rules":       "...",  # Branch/semester logic
    "safety_instructions":  "...",  # What to allow/disallow
    "conversation_tone":    "...",  # Formal / friendly / etc.
    "recommendation_logic": "...",  # Step-by-step logic
}
```

Changes take effect immediately without restarting.

---

## 🌐 Deployment

### Option A — Gunicorn (Linux/macOS Production)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Option B — IBM Code Engine

```bash
# Build container
docker build -t library-ai-agent .
docker tag library-ai-agent icr.io/<namespace>/library-ai-agent:latest
docker push icr.io/<namespace>/library-ai-agent:latest

# Deploy on IBM Code Engine
ibmcloud ce application create \
  --name library-ai-agent \
  --image icr.io/<namespace>/library-ai-agent:latest \
  --port 5000 \
  --env-from-secret library-secrets
```

### Option C — Heroku

```bash
echo "web: gunicorn app:app" > Procfile
heroku create my-library-ai-agent
heroku config:set IBM_API_KEY=... WATSONX_PROJECT_ID=... SECRET_KEY=...
git push heroku main
```

### Option D — Railway / Render

1. Connect your GitHub repository
2. Set all environment variables in the dashboard
3. Deploy — the platform auto-detects Flask

---

## 🐳 Docker (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:

```bash
docker build -t library-ai-agent .
docker run -p 5000:5000 --env-file .env library-ai-agent
```

---

## 📝 Sample AI Queries

Try these in the AI Chat interface:

```
"I am a 3rd year CSE student. Recommend Artificial Intelligence books."
"I need beginner books for Python."
"Suggest books for Data Structures and Algorithms."
"Show available Machine Learning books."
"I am preparing for placements. Recommend aptitude and DSA books."
"Recommend reference books for Computer Networks."
"What books should I read for DBMS in semester 4?"
"Suggest online resources for learning Deep Learning."
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, Flask 3.0 |
| AI Engine | IBM watsonx.ai SDK (`ibm-watsonx-ai`) |
| Foundation Model | IBM Granite 3.8B Instruct |
| Frontend | Bootstrap 5.3, Bootstrap Icons, HTML5, CSS3, JS |
| Config | python-dotenv |
| Production Server | Gunicorn |

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

*Built with ❤️ using IBM watsonx.ai and IBM Granite AI*
