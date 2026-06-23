# Lumina — A Modern Collaborative Blogging Platform

Lumina is a premium, responsive web application for writers and tech enthusiasts, built using a modern **Flask** backend and styled with a custom **Dark Glassmorphism** design system. The platform allows users to register, log in, publish rich-text articles, and join the conversation via secure comments.

---

## ✨ Features

- **🎨 Premium Dark Glassmorphism UI**: High-end styling utilizing modern CSS layout tokens, radial gradients, glass panels (`backdrop-filter`), smooth hover lifts, animations, and typography (Outfit & Inter) loaded from Google Fonts.
- **👥 Multi-Author Collaboration**: Any registered user can write and publish new posts. The platform dynamically attributes posts to their respective authors.
- **🔐 Author-Level Controls**: Post editing and deletion are restricted to the author of the post or the system administrator (`id = 1`).
- **📝 Rich-Text Editing**: Blog post creation and comments support full formatting (headings, lists, bold text, code blocks) using the CKEditor WYSIWYG editor.
- **💬 Interactive Comments**: Registered users can comment on any post. Body content is strictly sanitized using `bleach` to block XSS and malicious script injection.
- **🛡️ Secure Auth System**: Managed via `Flask-Login` with hashed passwords (`Werkzeug` PBKDF2/SHA-256) and CSRF protection (`Flask-WTF`).
- **👤 Gravatar Avatars**: Profile images are generated automatically for users in the comments section based on their email.
- **📱 Responsive Layout**: Fully optimized and pixel-perfect for mobile, tablet, and desktop viewports.

---

## 🛠️ Tech Stack

- **Backend**: Python (Flask 2.3)
- **Database**: SQLite (SQLAlchemy 2.0 ORM / Flask-SQLAlchemy)
- **Forms & Validation**: WTForms (Flask-WTF, Email-Validator)
- **Security**: Werkzeug (hashing), Bleach (XSS sanitization)
- **Avatars**: Flask-Gravatar
- **Formatting**: Flask-CKEditor
- **Styling**: Vanilla CSS (Modern Overrides) + Bootstrap 5 (Bootstrap-Flask)

---

## 📂 Project Structure

```text
├── main.py             # Main Flask application, routes, and models
├── forms.py            # Form validation definitions (WTForms)
├── requirements.txt    # Project dependencies
├── static/
│   ├── css/
│   │   ├── styles.css  # Base theme stylesheet
│   │   └── custom.css  # Redesigned dark glassmorphism design tokens & styles
│   ├── js/
│   │   └── scripts.js  # Interactivity scripts
│   └── assets/         # Favicons, theme backgrounds, and image assets
└── templates/          # HTML templates (Jinja2)
    ├── header.html     # Redesigned navigation bar and fonts loading
    ├── footer.html     # Modern copyright footer and script bundles
    ├── index.html      # Glass-card post lists and pagination links
    ├── post.html       # Post detail view, comment editor, and commenter list
    ├── login.html      # Authentication portal
    ├── register.html   # User registration page
    ├── make-post.html  # Post creation and rich text editor
    ├── about.html      # Collective platform bio
    └── contact.html    # Translucent form with floating inputs
```

---

## 🚀 Getting Started

Follow these steps to run Lumina locally on your machine:

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/lumina-blog.git
cd lumina-blog
```

### 2. Set Up a Virtual Environment (Optional but Recommended)
On Windows:
```bash
python -m venv .venv
.venv\Scripts\activate
```
On macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Set up a custom Flask key for session security:
- **Windows (Command Prompt)**: `set FLASK_KEY=your_secret_key_here`
- **Windows (PowerShell)**: `$env:FLASK_KEY="your_secret_key_here"`
- **macOS/Linux**: `export FLASK_KEY="your_secret_key_here"`

*If not set, the app will fall back to a default development key.*

### 5. Run the Server
```bash
python main.py
```

The application will start running at `http://127.0.0.1:5001/`. Open this link in your browser to view the site.

---

## 🔒 Security Practices

- **Password Storage**: Cleartext passwords are never stored. Passwords are salted and hashed on registration using `pbkdf2:sha256`.
- **Session Management**: Secure cookies handle logins. Logouts clear all active session variables immediately.
- **XSS Protection**: Comment content submitted through the rich-text editor is parsed through `bleach` and sanitized on the server before being saved or rendered in the template.
- **CSRF Token checks**: All forms are automatically protected against Cross-Site Request Forgery through Flask-WTF validation.

---

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.
