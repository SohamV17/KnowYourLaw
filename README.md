# ⚖️ KnowYourLaw – AI-Powered Legal Assistance Chatbot

KnowYourLaw is a web-based legal assistance chatbot designed to help users understand basic Indian laws, legal provisions, and commonly asked legal questions through a simple conversational interface.

The application uses **Natural Language Processing (NLP)** and **Sentence Transformers** to understand the semantic meaning of user queries and retrieve relevant answers from a structured legal question-and-answer knowledge base.

It is built using Python, Flask, PostgreSQL, and a responsive HTML/CSS frontend.

---

## 🚀 Features

### 1. Intelligent Legal Chatbot
- Interactive chatbot interface for asking legal questions.
- Supports natural-language queries.
- Provides answers from a predefined Indian legal Q&A knowledge base.
- Includes greeting detection for common greetings.
- Returns a fallback response when a sufficiently relevant answer is not found.

### 2. Hybrid Question-Matching System

The chatbot follows a two-step question-matching approach:

**Step 1 – Direct Matching**
- Converts the user's query to lowercase and removes surrounding whitespace.
- Checks whether the query exactly matches a question in the knowledge base.
- Returns the corresponding answer if a match is found.

**Step 2 – Semantic Similarity Search**
- Converts the user's query into a vector embedding using the Sentence Transformer model.
- Compares the query embedding with precomputed embeddings of the questions in the knowledge base.
- Uses cosine similarity to identify the most relevant question.
- Returns its corresponding answer if the similarity score exceeds the threshold of `0.60`.

If neither method produces a suitable result, the chatbot asks the user to rephrase the question.

### 3. User Authentication
- User registration with username and email.
- Secure password hashing using Werkzeug.
- Login and logout functionality.
- Flask session management.
- Protected profile route.

### 4. Database Integration
- PostgreSQL database integration using Flask-SQLAlchemy.
- User account storage.
- Unique username and email constraints.
- Database operations for registration and authentication.

### 5. Web Interface
- Interactive chatbot interface.
- Separate login and signup pages.
- Forgot-password page.
- HTML templates styled using CSS.
- AJAX-based chatbot communication using Fetch API.

---

## 🧠 NLP and Semantic Search Architecture

KnowYourLaw uses the pretrained Sentence Transformer model:

**`all-MiniLM-L6-v2`**

The model converts text into numerical vector representations called embeddings.

These embeddings allow the chatbot to identify questions with similar meanings, even when the wording differs.

### Chatbot Workflow

1. User enters a legal question.
2. The Flask backend receives the query.
3. Greeting detection checks for common greetings.
4. The system checks for an exact match in the Q&A dictionary.
5. If no exact match exists, the query is converted into an embedding.
6. Cosine similarity is calculated against the stored question embeddings.
7. The question with the highest similarity score is selected.
8. If its score is greater than `0.60`, the corresponding answer is returned.
9. Otherwise, a fallback response is displayed.

### Architecture Diagram

```text
             User
               |
               v
       Chatbot Web Interface
          (HTML / CSS)
               |
               v
        Flask Application
               |
               v
        Greeting Detection
               |
               v
       Exact Question Matching
               |
        Match Found?
          /       \
        Yes        No
         |          |
         v          v
      Return    Sentence Transformer
      Answer    (all-MiniLM-L6-v2)
                    |
                    v
             Query Embedding
                    |
                    v
            Cosine Similarity
                    |
                    v
          Find Most Similar Question
                    |
                    v
          Similarity Score > 0.60?
               /        \
             Yes         No
              |           |
              v           v
          Return       Fallback
          Answer       Response
```

---

## 📚 Legal Knowledge Base

The project includes a custom knowledge base named `KnowYourLaw.txt`, containing **363 question-and-answer entries**.

The knowledge base covers topics such as:

- Indian Constitution and Fundamental Rights
- Indian Penal Code (IPC) provisions
- Criminal offences and punishments
- FIR and criminal procedures
- Bail and anticipatory bail
- Motor Vehicle Act and traffic regulations
- Consumer protection and consumer rights
- Cybercrime and online fraud
- Property and real estate laws
- Family law and marriage-related provisions
- Labour and employment laws
- Intellectual property rights
- Banking and financial regulations
- Legal institutions and government agencies

The knowledge base follows a simple question-and-answer structure:

```text
Q: What is Section 302
A: Section 302 of the Indian Penal Code prescribes the punishment for murder...
```

The application loads this corpus at startup, extracts the questions and answers, and generates embeddings for the questions.

---

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Backend Framework | Flask |
| Frontend | HTML, CSS, JavaScript |
| Database | PostgreSQL |
| ORM | Flask-SQLAlchemy |
| NLP | Sentence Transformers |
| Embedding Model | all-MiniLM-L6-v2 |
| Similarity Measurement | Cosine Similarity |
| Authentication | Werkzeug Password Hashing |
| Communication | AJAX, Fetch API, JSON |
| Environment Management | python-dotenv |

---

## 📂 Project Structure

```text
KnowYourLaw/
│
├── app.py
│
├── KnowYourLaw.txt
│
├── requirements.txt
│
├── .env                 # Local environment variables
├── .gitignore
│
├── static/
│   ├── style.css
│   ├── login.css
│   ├── signup.css
│   ├── forgetpassword.css
│   ├── file.svg
│   └── Images and other assets
│
└── templates/
    ├── index.html
    ├── login.html
    ├── signup.html
    └── forgetpassword.html
```

---

## ⚙️ Installation and Setup

Follow these steps to run KnowYourLaw locally.

### Prerequisites

- Python 3.10 or compatible version
- PostgreSQL
- Git
- pip

### 1. Clone the Repository

```bash
git clone https://github.com/SohamV17/KnowYourLaw.git
```

Navigate into the project directory:

```bash
cd KnowYourLaw
```

### 2. Create a Virtual Environment

```bash
python -m venv env
```

Activate it on Windows:

```powershell
env\Scripts\activate
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory.

Add the following configuration:

```env
FLASK_SECRET_KEY=your_secret_key
DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5433/knowyourlaw
```

Replace `YOUR_PASSWORD` with your PostgreSQL password and configure the database port and name according to your local PostgreSQL setup.

**Important:** Never commit your `.env` file or expose database credentials publicly.

### 5. Create the PostgreSQL Database

Create a database named:

```sql
CREATE DATABASE knowyourlaw;
```

Ensure that the PostgreSQL credentials and port match the `DATABASE_URL` in your `.env` file.

The application creates the `users` table when it is started directly.

### 6. Run the Application

```bash
python app.py
```

On the first run, Sentence Transformers may download the `all-MiniLM-L6-v2` model.

Once the application starts, open:

```text
http://127.0.0.1:5000/
```

---

## 🔐 Authentication Routes

| Route | Method | Description |
|---|---|---|
| `/` | GET | Home page and chatbot |
| `/signup` | GET, POST | User registration |
| `/login` | GET, POST | User login |
| `/logout` | GET | Logout and clear session |
| `/forgetpassword` | GET, POST | Forgot-password page; reset functionality is not configured |
| `/profile` | GET | Protected profile route |

## 💬 Chatbot API

The chatbot provides an AJAX endpoint:

**Endpoint:**

```text
POST /get
```

**Request:**

```json
{
  "msg": "What is Article 21?"
}
```

**Response:**

```json
{
  "response": "Article 21 of the Indian Constitution guarantees the Right to Life and Personal Liberty..."
}
```

---

## 🔮 Future Improvements

- Implement secure email-based password reset functionality.
- Expand and regularly update the legal knowledge base.
- Improve legal answer accuracy and semantic search relevance.
- Add advanced keyword-based retrieval alongside semantic search.
- Add source references and citations to legal answers.
- Integrate an updated legal database and current legislation.
- Improve chatbot context handling for follow-up questions.
- Add a complete user profile page.
- Deploy the application to a cloud hosting platform.

---

## ⚠️ Disclaimer

KnowYourLaw is an educational legal information project intended to help users understand basic legal concepts and provisions.

The chatbot retrieves answers from a predefined knowledge base. It does not provide professional legal advice, replace consultation with a qualified lawyer, or guarantee that an answer is complete or applicable to a particular situation.

**Legal provisions and interpretations can change.** Some entries in the current knowledge base refer to older legislation, including the IPC and CrPC. Users should independently verify the current applicable law and consult a qualified legal professional before making legal decisions.

---

## 👨‍💻 Author

**Soham V.**

GitHub: [@SohamV17](https://github.com/SohamV17)

Project Repository: [KnowYourLaw](https://github.com/SohamV17/KnowYourLaw)

---

⭐ If you find this project interesting, consider giving the repository a star!
