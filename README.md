# Customer Feedback Dashboard

A complete, full-stack, ready-to-run **Customer Feedback Management & Analytics Web Application** built with **Python 3**, **Flask**, **SQLite**, **Chart.js**, and **Vanilla CSS3/JavaScript**.

Developed as a demonstration-ready final-year project for **BCA (Bachelor of Computer Applications)** and software engineering academic presentations.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Key Features](#key-features)
3. [Technology Stack](#technology-stack)
4. [System Architecture & Working Mechanism](#system-architecture--working-mechanism)
5. [Database Design & Schema](#database-design--schema)
6. [Sentiment Analysis Implementation](#sentiment-analysis-implementation)
7. [System Requirements](#system-requirements)
8. [Installation & Setup Guide](#installation--setup-guide)
9. [Administrator Credentials](#administrator-credentials)
10. [Step-by-Step Running Guide](#step-by-step-running-guide)
11. [VS Code Setup & Debugging Guide](#vs-code-setup--debugging-guide)
12. [Project Folder Structure](#project-folder-structure)
13. [API & Application Routes](#api--application-routes)
14. [Troubleshooting & FAQs](#troubleshooting--faqs)

---

## 1. Project Overview

Organizations rely heavily on timely customer feedback to identify service bottlenecks, refine product features, and maintain customer satisfaction. The **Customer Feedback Dashboard** provides a dual-facing platform:
1. **Public Customer Portal**: An intuitive, interactive feedback form where customers rate their experience (1 to 5 stars) across departments and provide detailed comments.
2. **Administrative Analytics Dashboard**: A password-protected command center providing key performance indicators (KPIs), interactive graphical visualizations, multi-criteria filtering, search, individual feedback audit logs with sentiment breakdown, and instant CSV/PDF export.

---

## 2. Key Features

- **Executive Analytics Dashboard**:
  - Real-time stat cards: Total Feedback, Average Rating, Positive %, Neutral %, Negative %, and Submissions Today.
  - 4 Dynamic interactive Chart.js graphs:
    - **Rating Distribution**: Bar chart breakdown of 1 to 5 stars.
    - **Sentiment Breakdown**: Doughnut chart showing Positive, Neutral, and Negative proportions.
    - **Feedback Submission Trend**: Line chart with smoothed area fill over time.
    - **Category-Wise Distribution**: Bar chart comparing feedback volumes across departments.
  - Recent customer feedback preview stream.

- **Public Customer Feedback Form**:
  - Interactive 5-star rating widget with hover states and live text feedback.
  - Client-side & server-side validation (email format, message character count, required fields).
  - Modern submission confirmation banner with option to submit subsequent responses.

- **Feedback Management & Directory**:
  - Search feedback by customer name, email address, product/service name, or message content.
  - Multi-criteria filtering: Rating (1-5), Category, Sentiment (Positive/Neutral/Negative), and Date Range.
  - Dynamic sorting (Newest, Oldest, Highest Rating, Lowest Rating).
  - Clean server-side pagination (10 items per page).

- **Sentiment Analysis Engine**:
  - 100% Python-based lexicon analyzer with negation handling (e.g., *"not good"*, *"never satisfied"*) and intensifier scaling (e.g., *"extremely"*, *"super"*).
  - Hybrid scoring incorporating both semantic text analysis and star ratings.
  - Zero external paid AI APIs required.

- **Reports & Exporting**:
  - Category-wise performance table with positive sentiment percentage indicators.
  - Rating distribution percentages.
  - Monthly timeline breakdown table.
  - **Print Report**: Custom CSS print layout (`@media print`) for clean paper or browser-native PDF printing.
  - **Export CSV**: Instant generation and download of formatted CSV spreadsheet data.
  - **Download PDF**: Formatted executive analytics report generated using Python's `reportlab` library.

- **Security & Session Authentication**:
  - Admin login protected with cryptographic password hashing using `werkzeug.security`.
  - Secure server-side Flask sessions.
  - Parameterized SQLite queries preventing SQL injection vulnerabilities.

---

## 3. Technology Stack

| Layer | Technology | Description |
| :--- | :--- | :--- |
| **Backend** | Python 3.10+ / 3.14 | Core backend programming language |
| **Web Framework** | Flask 3.x | Lightweight WSGI web application framework |
| **Authentication** | Werkzeug Security | Password hashing with PBKDF2 / SHA-256 |
| **Database** | SQLite 3 | Embedded ACID-compliant relational database |
| **Frontend** | HTML5, CSS3, JavaScript | Modern, responsive interface without bloated heavy frameworks |
| **Visual Charts** | Chart.js 4.4 | Canvas-based responsive interactive charts |
| **Icons & Typography**| Font Awesome 6, Google Fonts | Plus Jakarta Sans & Outfit typography |
| **PDF Reporting** | ReportLab 4.x / 5.x | Programmatic PDF document compilation |

---

## 4. System Architecture & Working Mechanism

```
  +------------------+         +-----------------------------------------+
  |  Browser Client  | <=====> |             Flask Web Server            |
  | (HTML/CSS/JS/UI) |  HTTP   |  (Routes, Session Auth, Jinja Engine)   |
  +------------------+         +-------------------+---------------------+
                                                   |
                             +---------------------+---------------------+
                             |                                           |
                             v                                           v
                   +-------------------+                       +-------------------+
                   | Sentiment Engine  |                       |  SQLite Database  |
                   |  (sentiment.py)   |                       |   (feedback.db)   |
                   +-------------------+                       +-------------------+
```

### How the Frontend Connects to Flask
1. The user navigates to a URL (e.g., `/dashboard` or `/feedback`).
2. Flask receives the HTTP GET/POST request via `app/routes.py`.
3. For protected routes, the `@login_required` decorator checks `flask.session['admin_logged_in']`.
4. The route queries the SQLite database, performs statistical aggregations, and packages the data.
5. Jinja2 templates (`templates/*.html`) render HTML populated with dynamic variables, then the browser renders the page alongside Chart.js visualizations.

### How Feedback is Stored
1. Customer submits the form on `/feedback`.
2. Server validates all fields against length and regex rules.
3. `analyze_sentiment()` computes the sentiment score and classification (`Positive`, `Neutral`, `Negative`).
4. An `INSERT INTO feedback (...) VALUES (?, ...)` query safely writes the record to SQLite using parameterized inputs.

### How Dashboard Statistics are Generated
- **Total Feedback**: `SELECT COUNT(*) FROM feedback`
- **Average Rating**: `SELECT ROUND(AVG(rating), 2) FROM feedback`
- **Sentiment Breakdown**: `SELECT COUNT(*) FROM feedback WHERE sentiment = ?`
- **Category Counts**: `SELECT category, COUNT(*) FROM feedback GROUP BY category`
- **Rating Counts**: `SELECT rating, COUNT(*) FROM feedback GROUP BY rating`

---

## 5. Database Design & Schema

The application uses an SQLite database located at `database/feedback.db`.

### 1. `users` Table
Stores administrator authentication credentials:
```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. `feedback` Table
Stores customer reviews, contact info, ratings, and sentiment outputs:
```sql
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    product_service TEXT NOT NULL,
    category TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
    message TEXT NOT NULL,
    sentiment TEXT NOT NULL CHECK(sentiment IN ('Positive', 'Neutral', 'Negative')),
    sentiment_score REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Database Performance Indexes
To ensure fast searching and filtering:
```sql
CREATE INDEX IF NOT EXISTS idx_feedback_category ON feedback(category);
CREATE INDEX IF NOT EXISTS idx_feedback_sentiment ON feedback(sentiment);
CREATE INDEX IF NOT EXISTS idx_feedback_rating ON feedback(rating);
CREATE INDEX IF NOT EXISTS idx_feedback_created_at ON feedback(created_at);
```

---

## 6. Sentiment Analysis Implementation

The sentiment engine (`app/sentiment.py`) implements a hybrid NLP algorithm designed specifically for university viva demonstrations:

1. **Word Tokenization & Normalization**: Converts message to lowercase and removes punctuation.
2. **Lexicon Matching**:
   - `POSITIVE_WORDS`: *excellent, amazing, great, good, love, outstanding, superb, fast, helpful, polite, clean, ...*
   - `NEGATIVE_WORDS`: *terrible, horrible, bad, poor, slow, worst, broken, defect, unhelpful, buggy, late, ...*
3. **Negation Flipping**:
   - Negation words (`not`, `no`, `never`, `hardly`, `isn't`, `wasn't`, `didn't`) preceding a positive word flip its polarity (e.g. *"not good"* is counted as negative).
4. **Intensifier Amplification**:
   - Modifiers like `very` (1.5x), `extremely` (1.8x), and `super` (1.6x) boost the sentiment impact of neighboring words.
5. **Rating Calibration**:
   - Blends 65% text semantics with 35% star rating factor (1 star = -1.0, 3 stars = 0.0, 5 stars = +1.0).
6. **Classification Thresholds**:
   - Compound score $\ge +0.20 \implies$ **Positive**
   - Compound score $\le -0.20 \implies$ **Negative**
   - Between $-0.20$ and $+0.20 \implies$ **Neutral**

---

## 7. System Requirements

- **Operating System**: Windows 10/11, macOS, or Linux.
- **Python Version**: Python 3.10, 3.11, 3.12, 3.13, or 3.14.
- **Web Browser**: Any modern browser (Google Chrome, Microsoft Edge, Mozilla Firefox, Brave).
- **Network**: Internet connection only on initial page load to fetch CDN assets (Font Awesome & Chart.js).

---

## 8. Installation & Setup Guide

### Step 1: Open Terminal / Command Prompt
Navigate to the project root directory:
```bash
cd "c:\Users\Rohith C\OneDrive\Desktop\crt"
```

### Step 2: Create a Virtual Environment (Recommended)
```bash
python -m venv venv
```

### Step 3: Activate the Virtual Environment
- **On Windows (PowerShell)**:
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- **On Windows (Command Prompt - CMD)**:
  ```cmd
  venv\Scripts\activate.bat
  ```
- **On macOS / Linux**:
  ```bash
  source venv/bin/activate
  ```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 9. Administrator Credentials

The initialization script sets up a default administrator account:

| Field | Value |
| :--- | :--- |
| **Username** | `admin` |
| **Password** | `admin123` |
| **Role** | System Administrator |

*(Passwords are securely hashed using PBKDF2/SHA-256; plain-text passwords are never stored in the database).*

---

## 10. Step-by-Step Running Guide

### 1. Initialize the SQLite Database
Creates the database directory and required tables:
```bash
python scripts/init_db.py
```
*Expected Output:*
```
[SUCCESS] Database tables ('users', 'feedback') verified.
[SUCCESS] Admin account created successfully!
          Username : admin
          Password : admin123
```

### 2. Populate Sample Feedback Data
Inserts 21 realistic customer reviews across diverse dates, ratings, and categories:
```bash
python scripts/seed_data.py
```
*Expected Output:*
```
[SUCCESS] Seeded 21 sample feedback entries across various categories and ratings!
```

### 3. Start the Flask Web Application
```bash
python app.py
```
*Expected Output:*
```
 * Customer Feedback Dashboard running on http://127.0.0.1:5000
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### 4. Access the Application in Your Browser
- **Admin Dashboard**: [http://127.0.0.1:5000/dashboard](http://127.0.0.1:5000/dashboard) *(Redirects to `/login` if not authenticated)*
- **Admin Login**: [http://127.0.0.1:5000/login](http://127.0.0.1:5000/login)
- **Public Customer Form**: [http://127.0.0.1:5000/feedback](http://127.0.0.1:5000/feedback)
- **Feedback Management**: [http://127.0.0.1:5000/feedback/list](http://127.0.0.1:5000/feedback/list)
- **Executive Reports**: [http://127.0.0.1:5000/reports](http://127.0.0.1:5000/reports)

---

## 11. VS Code Setup & Debugging Guide

1. Open **Visual Studio Code**.
2. Go to **File** $\rightarrow$ **Open Folder...** and select the project folder (`crt`).
3. Press `Ctrl + Shift + P` (or `Cmd + Shift + P` on Mac) and type:
   ```
   Python: Select Interpreter
   ```
4. Select the Python interpreter corresponding to your virtual environment (`.\venv\Scripts\python.exe`).
5. Open an integrated terminal in VS Code (`Ctrl + ~`).
6. Run:
   ```bash
   python app.py
   ```
7. Click the URL `http://127.0.0.1:5000` directly in the terminal to view in your browser.

---

## 12. Project Folder Structure

```
customer_feedback_dashboard/
│
├── app.py                     # Main application entrypoint
├── config.py                  # Configuration settings & DB path
├── requirements.txt           # Python dependencies (Flask, ReportLab, etc.)
├── README.md                  # Comprehensive project documentation
│
├── app/                       # Application Package
│   ├── __init__.py            # Flask Application Factory & Jinja filters
│   ├── database.py            # SQLite connection helper & context manager
│   ├── routes.py              # Application routing & HTTP controllers
│   ├── sentiment.py           # Lexicon-based sentiment analysis engine
│   └── reports_pdf.py         # Programmatic PDF report generator (ReportLab)
│
├── database/
│   └── feedback.db            # SQLite database file (created upon init)
│
├── scripts/
│   ├── init_db.py             # Database table creation & default admin seeder
│   └── seed_data.py           # Sample data script (21 realistic reviews)
│
├── static/                    # Frontend Static Assets
│   ├── css/
│   │   └── style.css          # Design system, layout, colors, and print styles
│   └── js/
│       ├── main.js            # Sidebar toggle, alert dismissal & delete modal
│       ├── dashboard.js       # Chart.js initialization for all 4 charts
│       ├── feedback.js        # Star rating widget & form validation
│       └── reports.js         # Print report trigger
│
└── templates/                 # Jinja2 HTML Templates
    ├── base.html              # Core layout (Sidebar, Navbar, Modals)
    ├── login.html             # Admin login page
    ├── dashboard.html         # Main executive analytics dashboard
    ├── feedback_form.html     # Public customer feedback form
    ├── feedback_list.html     # Feedback search, filter, and pagination
    ├── feedback_detail.html   # Detailed feedback view & sentiment breakdown
    ├── reports.html           # Comprehensive executive analytics report
    ├── 404.html               # Custom 404 error page
    └── 500.html               # Custom 500 server error page
```

---

## 13. API & Application Routes

| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Public | Redirects to `/dashboard` if logged in, else `/feedback` |
| `GET, POST` | `/login` | Public | Admin login authentication |
| `GET` | `/logout` | Authenticated | Clears admin session and redirects to login |
| `GET` | `/dashboard` | Authenticated | Main admin dashboard with KPIs & Chart.js graphs |
| `GET` | `/api/dashboard-stats`| Authenticated | JSON endpoint for live statistics |
| `GET, POST` | `/feedback` | Public | Customer feedback submission form |
| `GET` | `/feedback/list` | Authenticated | Search, filter, and paginated feedback directory |
| `GET` | `/feedback/<id>` | Authenticated | Detailed view of a single feedback record |
| `POST` | `/feedback/<id>/delete`| Authenticated | Deletes feedback record permanently |
| `GET` | `/reports` | Authenticated | Executive reports and performance summary |
| `GET` | `/reports/export/csv` | Authenticated | Download complete feedback records as CSV file |
| `GET` | `/reports/export/pdf` | Authenticated | Download executive analytics report as PDF |

---

## 14. Troubleshooting & FAQs

### Q1: `ModuleNotFoundError: No module named 'flask'`
**Solution**: Make sure your virtual environment is activated, then run:
```bash
pip install -r requirements.txt
```

### Q2: Database locked or table not found error
**Solution**: Run the initialization script to recreate/verify database tables:
```bash
python scripts/init_db.py
```

### Q3: How do I change the default admin password?
**Solution**: You can generate a new password hash in Python using `werkzeug.security.generate_password_hash("your_new_password")` and update the `users` table via `sqlite3`.

### Q4: Port 5000 is already in use
**Solution**: Specify a different port when running `app.py`:
```bash
set PORT=5001
python app.py
```
*(On Linux/macOS: `PORT=5001 python app.py`)*

---

### Project Demonstration Tips for BCA Viva
1. **Explain the Architecture**: Highlight the separation of concerns: `database.py` manages connections, `sentiment.py` encapsulates NLP business logic, `routes.py` handles HTTP controllers, and `templates/` cleanly formats the presentation layer.
2. **Highlight Security**: Explain that Werkzeug cryptographic password hashing and parameterized SQL queries (`?`) are implemented to protect against plain-text leaks and SQL injection.
3. **Showcase Sentiment Explainability**: Open any feedback detail page (`/feedback/<id>`) to show the examiner how the algorithm identified specific positive/negative keywords, accounted for negations, and computed the compound score.
