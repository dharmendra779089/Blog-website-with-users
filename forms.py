# Import FlaskForm - the base class for all WTForms used with Flask
# FlaskForm automatically includes CSRF protection for security
from flask_wtf import FlaskForm
# Import form field types:
# StringField - renders as a text input (<input type="text">)
# SubmitField - renders as a submit button (<input type="submit">)
# PasswordField - renders as a password input (<input type="password">) that hides typed characters
from wtforms import StringField, SubmitField, PasswordField
# Import form validators:
# DataRequired - ensures the field is not submitted empty
# URL - validates that the input is a properly formatted URL
# Email - validates that the input is a properly formatted email address
from wtforms.validators import DataRequired, URL, Email
# Import CKEditorField - a rich text editor field that replaces a standard textarea
# with a full WYSIWYG editor (bold, italic, links, images, etc.)
from flask_ckeditor import CKEditorField


# WTForm for creating and editing a blog post
# This form is used in both the "new post" and "edit post" routes
class CreatePostForm(FlaskForm):
    # Text input for the blog post title - must not be empty (DataRequired)
    title = StringField("Blog Post Title", validators=[DataRequired()])
    # Text input for the blog post subtitle - must not be empty
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    # Text input for the blog post's featured image URL
    # Must not be empty (DataRequired) and must be a valid URL format (URL)
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    # Rich text editor (CKEditor) for the blog post body/content
    # Allows HTML formatting (bold, lists, headings, etc.) - must not be empty
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    # Submit button to save the blog post
    submit = SubmitField("Submit Post")


# WTForm for registering new users on the blog
class RegisterForm(FlaskForm):
    # Text input for the user's email address
    # DataRequired ensures it's not empty, Email() validates it's a valid email format
    email = StringField("Email", validators=[DataRequired(), Email()])
    # Password input for the user's password - characters are hidden as dots/asterisks
    # DataRequired ensures the field is not empty
    password = PasswordField("Password", validators=[DataRequired()])
    # Text input for the user's display name - must not be empty
    name = StringField("Name", validators=[DataRequired()])
    # Submit button to register the new user
    submit = SubmitField("Sign Me Up!")


# WTForm for logging in existing users
class LoginForm(FlaskForm):
    # Text input for the user's email address
    # DataRequired ensures it's not empty, Email() validates the format
    email = StringField("Email", validators=[DataRequired(), Email()])
    # Password input for the user's password - must not be empty
    password = PasswordField("Password", validators=[DataRequired()])
    # Submit button to log in
    submit = SubmitField("Let Me In!")


# WTForm for adding comments to blog posts
class CommentForm(FlaskForm):
    # Rich text editor (CKEditor) for the comment body
    # Allows HTML formatting - must not be empty
    comment_text = CKEditorField("Comment", validators=[DataRequired()])
    # Submit button to post the comment
    submit = SubmitField("Submit Comment")
