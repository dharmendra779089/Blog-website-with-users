# Import the 'os' module to access environment variables (used for the secret key)
import os
# Import 'date' from datetime to get today's date for blog post timestamps
from datetime import date
# Import core Flask components:
# Flask - the main application class that creates the web app
# abort - used to return HTTP error responses (e.g., 403 Forbidden)
# render_template - renders HTML templates with Jinja2 template engine
# redirect - redirects the user to a different URL/route
# url_for - generates a URL for a given route function by name
# flash - displays one-time messages to the user (e.g., error/success messages)
# request - accesses incoming HTTP request data (form data, method type, etc.)
from flask import Flask, abort, render_template, redirect, url_for, flash, request
# Import Bootstrap5 integration for Flask to use Bootstrap CSS/JS in templates
from flask_bootstrap import Bootstrap5
# Import CKEditor integration for Flask to provide a rich text editor in forms
from flask_ckeditor import CKEditor
# Import Gravatar to generate user profile images based on their email address
from flask_gravatar import Gravatar
# Import Flask-Login components:
# UserMixin - provides default implementations for user authentication methods
# login_user - logs a user in by creating a session
# LoginManager - manages the login state and session handling
# current_user - a proxy for the currently logged-in user object
# logout_user - logs the current user out by clearing the session
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
# Import SQLAlchemy integration for Flask to interact with the database using ORM
from flask_sqlalchemy import SQLAlchemy
# Import SQLAlchemy ORM components:
# relationship - defines relationships between database tables (one-to-many, etc.)
# DeclarativeBase - base class for defining database models using the new SQLAlchemy 2.0 style
# Mapped - used for type-annotated column definitions
# mapped_column - creates a database column with type annotations
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
# Import SQLAlchemy column types:
# Integer - for whole number columns (e.g., id, foreign keys)
# String - for short text columns with a max length (e.g., names, emails)
# Text - for long text columns without a fixed length (e.g., blog post body)
from sqlalchemy import Integer, String, Text
# Import 'wraps' to preserve the original function's metadata when creating decorators
from functools import wraps
# Import password hashing utilities from Werkzeug:
# generate_password_hash - creates a salted hash of a password for secure storage
# check_password_hash - verifies a password against its stored hash
from werkzeug.security import generate_password_hash, check_password_hash
# Import 'bleach' for sanitizing HTML content to prevent XSS (Cross-Site Scripting) attacks
import bleach
# Import custom WTForms form classes defined in forms.py:
# CreatePostForm - form for creating/editing blog posts
# RegisterForm - form for new user registration
# LoginForm - form for user login
# CommentForm - form for submitting comments on blog posts
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm

'''
Make sure the required packages are installed: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from the requirements.txt for this project.
'''

# Create the Flask application instance, __name__ tells Flask where to look for templates/static files
app = Flask(__name__)
# Set the secret key used for session cookies and CSRF protection
# Reads from the FLASK_KEY environment variable; falls back to a default if not set
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY', '8BYkEfBA6O6donzWlSihBXox7C0sKR6b')
# Initialize the CKEditor extension with the Flask app for rich text editing
ckeditor = CKEditor(app)
# Initialize Bootstrap5 extension to use Bootstrap styling in templates
Bootstrap5(app)

# Configure Flask-Login's LoginManager to handle user session management
login_manager = LoginManager()
# Register the login manager with the Flask app
login_manager.init_app(app)


# This callback is used by Flask-Login to reload the user object from the user ID stored in the session
# It is called on every request to check if the user is still logged in
@login_manager.user_loader
def load_user(user_id):
    # Use db.session.get() which returns None if user not found (instead of raising a 404 error)
    return db.session.get(User, user_id)


# Configure Gravatar for generating profile images in the comment section
# Gravatar creates avatar images based on the user's email hash
gravatar = Gravatar(app,
                    size=100,           # Image size in pixels (100x100)
                    rating='g',         # Only show 'g' rated (general audience) images
                    default='retro',    # Use 'retro' style if no Gravatar exists for the email
                    force_default=False, # Don't force the default image; use user's Gravatar if available
                    force_lower=False,  # Don't force email to lowercase before hashing
                    use_ssl=False,      # Use HTTP instead of HTTPS for Gravatar URLs
                    base_url=None)      # Use the default Gravatar base URL

# CREATE DATABASE
# Define the base class for all SQLAlchemy models using the new DeclarativeBase pattern
class Base(DeclarativeBase):
    pass
# Configure the database URI to use DB_URI env var if present (e.g. Postgres on Render), otherwise SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URI', 'sqlite:///posts.db')
# Create the SQLAlchemy instance with our custom Base class for model definitions
db = SQLAlchemy(model_class=Base)
# Register the SQLAlchemy instance with the Flask app to enable database operations
db.init_app(app)


# CONFIGURE TABLES
# Define the BlogPost model representing the 'blog_posts' table in the database
class BlogPost(db.Model):
    # Set the actual table name in the database
    __tablename__ = "blog_posts"
    # Primary key column - auto-incrementing integer that uniquely identifies each blog post
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Foreign Key linking to the 'users' table - stores the ID of the user who authored this post
    # "users.id" refers to the 'id' column in the 'users' table
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    # ORM relationship to the User model - allows accessing the full User object via post.author
    # back_populates="posts" creates a bidirectional link with User.posts
    author = relationship("User", back_populates="posts")
    # Blog post title - must be unique (no two posts can share the same title) and cannot be empty
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    # Blog post subtitle - cannot be empty
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    # Date the post was published, stored as a formatted string (e.g., "June 23, 2026")
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    # The main content/body of the blog post - uses Text type for unlimited length HTML content
    body: Mapped[str] = mapped_column(Text, nullable=False)
    # URL for the blog post's header/featured image
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    # Parent relationship to comments - one blog post can have many comments
    # back_populates="parent_post" links to Comment.parent_post
    comments = relationship("Comment", back_populates="parent_post")


# Define the User model representing the 'users' table for all registered users
# UserMixin provides default implementations of is_authenticated, is_active, is_anonymous, get_id()
class User(UserMixin, db.Model):
    # Set the actual table name in the database
    __tablename__ = "users"
    # Primary key - auto-incrementing unique identifier for each user
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # User's email address - must be unique so no two users can register with the same email
    email: Mapped[str] = mapped_column(String(100), unique=True)
    # User's hashed password - never stores the plain text password
    password: Mapped[str] = mapped_column(String(100))
    # User's display name shown on blog posts and comments
    name: Mapped[str] = mapped_column(String(100))
    # Relationship to BlogPost - acts like a list of all BlogPost objects authored by this user
    # back_populates="author" links to BlogPost.author
    posts = relationship("BlogPost", back_populates="author")
    # Relationship to Comment - acts like a list of all Comment objects written by this user
    # back_populates="comment_author" links to Comment.comment_author
    comments = relationship("Comment", back_populates="comment_author")


# Define the Comment model representing the 'comments' table for blog post comments
class Comment(db.Model):
    # Set the actual table name in the database
    __tablename__ = "comments"
    # Primary key - auto-incrementing unique identifier for each comment
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # The comment text/body content - uses Text type for potentially long comments
    text: Mapped[str] = mapped_column(Text, nullable=False)
    # Foreign Key linking to 'users' table - stores the ID of the user who wrote this comment
    # "users.id" refers to the 'id' column in the 'users' table
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    # ORM relationship to User - allows accessing the full User object via comment.comment_author
    # back_populates="comments" creates a bidirectional link with User.comments
    comment_author = relationship("User", back_populates="comments")
    # Foreign Key linking to 'blog_posts' table - stores the ID of the blog post this comment belongs to
    # "blog_posts.id" refers to the 'id' column in the 'blog_posts' table
    post_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("blog_posts.id"))
    # ORM relationship to BlogPost - allows accessing the parent post via comment.parent_post
    # back_populates="comments" creates a bidirectional link with BlogPost.comments
    parent_post = relationship("BlogPost", back_populates="comments")


# Create all database tables based on the models defined above
# app_context() is required because SQLAlchemy needs the Flask app context to know which database to use
with app.app_context():
    db.create_all()


# Context processor that automatically injects 'current_year' into all templates
# This makes {{ current_year }} available in every template without passing it manually
@app.context_processor
def inject_year():
    # Return a dictionary with the current year (e.g., 2026) for dynamic copyright text
    return {'current_year': date.today().year}


# Custom decorator function that restricts route access to admin users only (user with id=1)
def admin_only(f):
    # @wraps preserves the original function's name and docstring
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If the user is not logged in, redirect them to the login page with a flash message
        if not current_user.is_authenticated:
            flash("You need to log in to access this page.")
            return redirect(url_for('login'))
        # If the user is logged in but is not the admin (user with ID 1), return a 403 Forbidden error
        if current_user.id != 1:
            return abort(403)
        # If the user IS the admin (id=1), proceed to execute the original route function
        return f(*args, **kwargs)
    # Return the wrapper function that replaces the original
    return decorated_function


# Route for user registration - accepts both GET (show form) and POST (submit form) requests
@app.route('/register', methods=["GET", "POST"])
def register():
    # Create an instance of the RegisterForm
    form = RegisterForm()
    # validate_on_submit() returns True only if the form was submitted via POST and all validators pass
    if form.validate_on_submit():

        # Query the database to check if a user with the submitted email already exists
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        # scalar() returns the first result or None if no match found
        user = result.scalar()
        # If a user with that email already exists in the database
        if user:
            # Show a flash message telling the user they're already registered
            flash("You've already signed up with that email, log in instead!")
            # Redirect them to the login page instead
            return redirect(url_for('login'))

        # Hash the password using PBKDF2 with SHA-256 algorithm and a salt of 8 characters
        # This creates a secure one-way hash that cannot be reversed back to the original password
        hash_and_salted_password = generate_password_hash(
            form.password.data,        # The plain text password from the form
            method='pbkdf2:sha256',     # The hashing algorithm to use
            salt_length=8               # Length of the random salt added before hashing
        )
        # Create a new User object with the form data
        new_user = User(
            email=form.email.data,              # Store the user's email
            name=form.name.data,                # Store the user's display name
            password=hash_and_salted_password,  # Store the hashed password (never plain text)
        )
        # Add the new user to the database session (stages it for saving)
        db.session.add(new_user)
        # Commit the session to actually save the new user to the database
        db.session.commit()
        # Automatically log in the newly registered user using Flask-Login
        login_user(new_user)
        # Redirect to the home page showing all blog posts
        return redirect(url_for("get_all_posts"))
    # For GET requests (or failed validation), render the registration page with the form
    return render_template("register.html", form=form, current_user=current_user)


# Route for user login - accepts both GET (show form) and POST (submit form) requests
@app.route('/login', methods=["GET", "POST"])
def login():
    # Create an instance of the LoginForm
    form = LoginForm()
    # Check if the form was submitted and all validators passed
    if form.validate_on_submit():
        # Get the password entered by the user from the form
        password = form.password.data
        # Query the database for a user with the submitted email address
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        # Get the single user result (email is unique, so there will be at most one match)
        user = result.scalar()
        # If no user was found with that email address
        if not user:
            # Show an error flash message
            flash("That email does not exist, please try again.")
            # Redirect back to the login page
            return redirect(url_for('login'))
        # If a user was found but the password doesn't match the stored hash
        elif not check_password_hash(user.password, password):
            # Show an error flash message
            flash('Password incorrect, please try again.')
            # Redirect back to the login page
            return redirect(url_for('login'))
        # If both email and password are correct
        else:
            # Log the user in using Flask-Login (creates a session)
            login_user(user)
            # Redirect to the home page
            return redirect(url_for('get_all_posts'))

    # For GET requests, render the login page with the form
    return render_template("login.html", form=form, current_user=current_user)


# Route for logging out - only accepts GET requests (clicking the logout link)
@app.route('/logout')
def logout():
    # Clear the user's session data using Flask-Login
    logout_user()
    # Redirect to the home page after logging out
    return redirect(url_for('get_all_posts'))


# Route for the home page - displays all blog posts
@app.route('/')
def get_all_posts():
    # Get the current page number from the query parameters, default is 1
    page = request.args.get('page', 1, type=int)
    # Paginate posts (e.g., 3 posts per page) ordered by ID in descending order (newest first)
    pagination = db.paginate(
        db.select(BlogPost).order_by(BlogPost.id.desc()),
        page=page,
        per_page=3,
        error_out=False
    )
    # Render the index template, passing the current page's posts, pagination object, and current user
    return render_template("index.html", all_posts=pagination.items, pagination=pagination, current_user=current_user)



# Route for viewing a single blog post and its comments
# Accepts both GET (view post) and POST (submit comment) requests
# <int:post_id> captures the post ID from the URL as an integer
@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    # Fetch the blog post by ID, or return a 404 error if not found
    requested_post = db.get_or_404(BlogPost, post_id)
    # Create an instance of the CommentForm for the comment section
    comment_form = CommentForm()
    # Check if the comment form was submitted and validated
    if comment_form.validate_on_submit():
        # Verify the user is logged in before allowing them to comment
        if not current_user.is_authenticated:
            # Show a flash message prompting the user to log in
            flash("You need to login or register to comment.")
            # Redirect to the login page
            return redirect(url_for("login"))

        # Sanitize the comment HTML to prevent XSS (Cross-Site Scripting) attacks
        # bleach.clean() strips any HTML tags/attributes not in the allowlist
        clean_text = bleach.clean(
            comment_form.comment_text.data,  # The raw HTML from the CKEditor comment field
            # List of allowed HTML tags - only safe formatting tags are permitted
            tags=['a', 'abbr', 'b', 'blockquote', 'code',
                  'em', 'i', 'li', 'ol', 'p', 'strong', 'ul', 'br',
                  'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'pre', 'span', 'div', 'hr'],
            # List of allowed attributes per tag - only safe attributes are permitted
            attributes={'a': ['href', 'title'], 'abbr': ['title']},
        )
        # Create a new Comment object with sanitized text
        new_comment = Comment(
            text=clean_text,                    # The sanitized comment text
            comment_author=current_user,        # Link the comment to the logged-in user
            parent_post=requested_post          # Link the comment to the blog post
        )
        # Add the new comment to the database session
        db.session.add(new_comment)
        # Save the comment to the database
        db.session.commit()
    # Render the post template with the blog post, current user, and comment form
    return render_template("post.html", post=requested_post, current_user=current_user, form=comment_form)


# Route for creating a new blog post - accessible by any logged-in user
@app.route("/new-post", methods=["GET", "POST"])
def add_new_post():
    # If the user is not logged in, redirect them to the login page
    if not current_user.is_authenticated:
        flash("You need to log in to create a new post.")
        return redirect(url_for('login'))
    
    # Create an instance of the CreatePostForm
    form = CreatePostForm()
    # Check if the form was submitted and all validators passed
    if form.validate_on_submit():
        # Create a new BlogPost object with data from the form
        new_post = BlogPost(
            title=form.title.data,                          # Blog post title from the form
            subtitle=form.subtitle.data,                    # Blog post subtitle from the form
            body=form.body.data,                            # Blog post body/content (HTML from CKEditor)
            img_url=form.img_url.data,                      # Featured image URL from the form
            author=current_user,                            # Set the author to the currently logged-in user
            date=date.today().strftime("%B %d, %Y")         # Format today's date as "Month Day, Year"
        )
        # Add the new post to the database session
        db.session.add(new_post)
        # Save the post to the database
        db.session.commit()
        # Redirect to the home page to see the new post in the list
        return redirect(url_for("get_all_posts"))
    # For GET requests, render the make-post template with the empty form
    return render_template("make-post.html", form=form, current_user=current_user)


# Route for editing an existing blog post - accessible by the post author or admin (user id=1)
# <int:post_id> captures the post ID from the URL
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    # Fetch the blog post by ID, or return a 404 error if not found
    post = db.get_or_404(BlogPost, post_id)
    
    # If the user is not logged in, redirect them to the login page
    if not current_user.is_authenticated:
        flash("You need to log in to edit this post.")
        return redirect(url_for('login'))
        
    # Check if the current user is either the author of the post or the admin (id=1)
    if current_user.id != post.author_id and current_user.id != 1:
        return abort(403)
        
    # Pre-populate the form with the existing post data so the user can edit it
    edit_form = CreatePostForm(
        title=post.title,           # Pre-fill with current title
        subtitle=post.subtitle,     # Pre-fill with current subtitle
        img_url=post.img_url,       # Pre-fill with current image URL
        author=post.author,         # Pre-fill with current author
        body=post.body              # Pre-fill with current body content
    )
    # Check if the edit form was submitted and validated
    if edit_form.validate_on_submit():
        # Update the post's title with the new value from the form
        post.title = edit_form.title.data
        # Update the post's subtitle
        post.subtitle = edit_form.subtitle.data
        # Update the post's image URL
        post.img_url = edit_form.img_url.data
        # Update the post's body content
        post.body = edit_form.body.data
        # Save the changes to the database (no need for db.session.add since the object is already tracked)
        db.session.commit()
        # Redirect to the updated post's page
        return redirect(url_for("show_post", post_id=post.id))
    # For GET requests, render the make-post template with pre-filled form and is_edit=True flag
    return render_template("make-post.html", form=edit_form, is_edit=True, current_user=current_user)


# Route for deleting a blog post - accessible by the post author or admin (user id=1)
# Only accepts GET requests (clicking the delete button/link)
@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    # Fetch the blog post by ID, or return a 404 error if not found
    post_to_delete = db.get_or_404(BlogPost, post_id)
    
    # If the user is not logged in, redirect them to the login page
    if not current_user.is_authenticated:
        flash("You need to log in to delete this post.")
        return redirect(url_for('login'))
        
    # Check if the current user is either the author of the post or the admin (id=1)
    if current_user.id != post_to_delete.author_id and current_user.id != 1:
        return abort(403)
    # Remove the post from the database session (marks it for deletion)
    db.session.delete(post_to_delete)
    # Commit the deletion to the database
    db.session.commit()
    # Redirect to the home page after deletion
    return redirect(url_for('get_all_posts'))


# Route for the About page - only accepts GET requests
@app.route("/about")
def about():
    # Render the about template, passing the current user for navbar display
    return render_template("about.html", current_user=current_user)


# Route for the Contact page - accepts GET (show form) and POST (submit form) requests
@app.route("/contact", methods=["GET", "POST"])
def contact():
    # Flag to track whether the contact message was successfully sent
    msg_sent = False
    # Check if the form was submitted via POST
    if request.method == "POST":
        # Access the submitted form data from the POST request
        data = request.form
        # Print the contact form data to the console (placeholder for actual email sending logic)
        print(f"Contact form from {data.get('name')}: {data.get('message')}")
        # Set the flag to True so the template shows a success message
        msg_sent = True
    # Render the contact template, passing the current user and the msg_sent flag
    return render_template("contact.html", current_user=current_user, msg_sent=msg_sent)


# This block only runs when the script is executed directly (not when imported as a module)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=False, host="0.0.0.0", port=port)
