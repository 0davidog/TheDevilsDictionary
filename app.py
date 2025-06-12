import os
import json
import requests
from flask import Flask, render_template, request, flash
from flask import send_from_directory, redirect, url_for
from flask import jsonify
from flask_mail import Mail, Message
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Email
from config import DevelopmentConfig, ProductionConfig
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.exceptions import HTTPException
import random
import logging
import re

# Import environment variables from env.py if it exists
if os.path.exists("env.py"):
    import env

app = Flask(__name__)
limiter = Limiter(key_func=get_remote_address)  # Don't pass app here
limiter.init_app(app)  # Then initialize with the app


# Load configuration based on environment
if os.environ.get("FLASK_ENV") == "development":
    app.config.from_object(DevelopmentConfig)
else:
    app.config.from_object(ProductionConfig)


# Error handling for missing configurations
required_config = ["SECRET_KEY", "MAIL_USERNAME", "MAIL_PASSWORD", "RECAPTCHA_SECRET_KEY", "SITE_KEY"]
missing_config = [key for key in required_config if not app.config.get(key)]
if missing_config:
    raise ValueError(
        f"Missing critical configuration(s): {', '.join(missing_config)}"
        )


# Initialize the Mail object
mail = Mail(app)

# Set up basic logging
logging.basicConfig(level=logging.DEBUG)

# Create a logger
logger = logging.getLogger(__name__)

# Create a file handler that logs to a specific file

# Path to log file
log_file_path = os.path.join(app.root_path, 'app.log')
file_handler = logging.FileHandler(log_file_path)

# Log all messages from DEBUG level and above
file_handler.setLevel(logging.DEBUG)

# Create a formatter for the log messages
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

# Add a console handler to log to the console as well
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
# Change to INFO or higher to limit console output

console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


# Set up Error code Handling 500
@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error(f"Server error: {e}")
    return render_template('500.html'), 500


# Set up Error code Handling 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# Set up for undandle exceptions
@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Unhandled Exception: {e}")
    return render_template('500.html'), 500


# Jinja filter for managing title case
def custom_title(value):
    """
    Convert a string to title case, with exceptions for certain words.

    This function takes a string and converts it to title case, where the
    first letter of each word is capitalized. However, it ignores certain
    common words (like "or", "and", "the") that are not capitalized
    unless they appear at the beginning of the title.

    Args:
        value (str): The input string to be converted to title case.

    Returns:
        str: The input string formatted in title case, with exceptions
        applied to specified words.

    Example:
        >>> custom_title("the quick brown fox jumps over the lazy dog")
        'The Quick Brown Fox Jumps Over the Lazy Dog'
    """
    ignore_words = {'or', 'and', 'the'}  # Set for fast lookup

    words = re.split(r'(\W+)', value)  # Splitting while keeping punctuation

    title_cased_words = [
        word.title() if word.lower()
        not in ignore_words else word.lower() for word in words
    ]
    # Fix spacing issues by ensuring no spaces appear directly inside parentheses
    result = ''.join(title_cased_words)
    result = re.sub(r'\(\s+', '(', result)  # Remove space after '('
    result = re.sub(r'\s+\)', ')', result)  # Remove space before ')'

    return result


app.jinja_env.filters['custom_title'] = custom_title


# link to robots.txt
@app.route('/robots.txt')
def robots():
    return send_from_directory(app.root_path, 'robots.txt')


# Index page
@app.route("/")
def index():
    """
    Render the index page displaying a random entry from the dataset.

    This function selects a random letter from A to Z, attempts to load the
    corresponding JSON file containing entries, and selects a random entry
    from that file to display on the index page. It handles errors related
    to file not found, JSON decoding issues, and data validation.

    Returns:
        str: Rendered template for the index page, including the random
        entry and a list of letters from A to Z.

    Raises:
        FileNotFoundError: If the corresponding JSON file for the selected
        letter does not exist.
        json.JSONDecodeError: If the JSON file cannot be parsed.
        ValueError: If the data in the JSON file is not in the expected
        format (i.e., a list of dictionaries with 'name' keys).
    """
    letters = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
    random_letter = random.choice(letters)

    random_entry = None
    try:
        file_path = os.path.join(
            app.root_path, 'data', f"{random_letter.lower()}.json"
            )
        app.logger.debug(f"Loading JSON file from: {file_path}")

        with open(file_path, "r") as json_data:
            data = json.load(json_data)

        # Validate that the data is a list of dictionaries with 'name' keys
        if not isinstance(data, list) or not all(
            isinstance(item, dict) and 'name' in item for item in data
        ):
            raise ValueError(
                "Invalid data format: "
                "Expected a list of dictionaries with 'name' "
                "keys."
            )

        random_entry = (
            random.choice(data) if data else {"name": "No data available."}
            )

    except FileNotFoundError:
        app.logger.error(f"File not found: {file_path}")
        random_entry = {"name": "File not found."}
    except json.JSONDecodeError:
        app.logger.error(f"Error parsing JSON file: {file_path}")
        random_entry = {"name": "Error parsing data."}
    except ValueError as e:
        app.logger.error(f"Data validation error: {e}")
        random_entry = {"name": "Invalid data format."}

    return render_template(
        "index.html", page_title="Index", letters=letters,
        random=random_entry, listing_name=random_letter
        )


# Listing the words in each letter of the alphabet
@app.route("/<listing_name>")
def listing(listing_name):
    """
    Render the listing page for a specific letter of the alphabet.

    This function retrieves and displays all entries associated with the
    specified letter (listing_name). It also determines the previous and
    next letters in the alphabet for navigation purposes. The function
    attempts to load the corresponding JSON file and validate the format.

    Args:
        listing_name (str): The letter of the alphabet for which to
        display entries (e.g., 'A', 'B', etc.).

    Returns:
        str: Rendered template for the listing page, including the
        entries for the specified letter and navigation links to the
        previous and next letters.

    Raises:
        FileNotFoundError: If the corresponding JSON file for the
        specified letter does not exist.
        json.JSONDecodeError: If the JSON file cannot be parsed.
        ValueError: If the data in the JSON file is not in the expected
        format (i.e., a list of dictionaries).
    """
    data = []
    letters = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
    current_index = letters.index(listing_name.upper())
    prev_letter = letters[current_index - 1] if current_index > 0 else None
    next_letter = (
        letters[current_index + 1]
        if current_index < len(letters) - 1
        else None
        )

    try:
        file_path = os.path.join(
            app.root_path, 'data', f"{listing_name.lower()}.json"
            )
        app.logger.debug(f"Loading JSON file from: {file_path}")

        with open(file_path, "r") as json_data:
            data = json.load(json_data)
            if not isinstance(data, list):
                raise ValueError(
                    "Invalid JSON format: Expected a list of dictionaries."
                    )
            if not data:
                app.logger.warning(f"No entries found for '{listing_name}'")
                return render_template('404.html'), 404

        if not data:
            app.logger.warning(f"No entries found for '{listing_name}'")
            return render_template('404.html'), 404

    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        app.logger.error(f"Error loading or parsing JSON file: {e}")

    return render_template(
        "listing.html", listing_name=listing_name,
        listings=data, prev_letter=prev_letter, next_letter=next_letter
        )


# pages for each word
@app.route("/<listing_name>/<entry_name>")
def entry(listing_name, entry_name):
    """
    Render the entry page for a specific word from a given listing.

    This function retrieves and displays detailed information about a
    specific entry identified by the entry_name within the context of
    a specified letter (listing_name). The function attempts to load
    the corresponding JSON file and validate the format before
    searching for the specified entry.

    Args:
        listing_name (str): The letter of the alphabet that the entry
        belongs to (e.g., 'A', 'B', etc.).
        entry_name (str): The name of the entry to display, formatted
        with underscores as spaces (e.g., 'example_entry').

    Returns:
        str: Rendered template for the entry page, including the
        details of the specified entry.

    Raises:
        FileNotFoundError: If the corresponding JSON file for the
        specified letter does not exist.
        json.JSONDecodeError: If the JSON file cannot be parsed.
        ValueError: If the data in the JSON file is not in the expected
        format (i.e., a list of dictionaries) or if the specified entry
        is not found.
    """
    entry = {}
    entry_name = entry_name.replace("_", " ").upper()

    try:
        file_path = os.path.join(
            app.root_path, 'data', f"{listing_name.lower()}.json"
            )
        app.logger.debug(f"Loading JSON file from: {file_path}")

        with open(file_path, "r") as json_data:
            data = json.load(json_data)
            if not isinstance(data, list):
                raise ValueError(
                    "Invalid JSON format: Expected a list of dictionaries."
                    )
            if not data:
                app.logger.warning(f"No entries found for '{listing_name}'")
                return render_template('404.html'), 404
            for obj in data:
                if obj["name"] == entry_name:
                    entry = obj
                    break

            if not entry:
                app.logger.warning(
                    f"Entry '{entry_name}' not found in '{listing_name}'"
                    )
                return render_template('404.html'), 404

    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        app.logger.error(f"Error loading or parsing JSON file: {e}")

    return render_template("entry.html", entry=entry)


# about page
@app.route("/about")
def about():
    """
    Render the About page.

    Returns:
        str: Rendered template for the About page.
    """
    return render_template("about.html", page_title="About")


class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired()])
    honeypot = HiddenField('Leave empty')  # Honeypot field, should be empty
    submit = SubmitField('Send Message')


# contact page
@limiter.limit("3/hour")  # Or adjust to "1/minute", "10/day", etc.
@app.route("/contact", methods=["GET", "POST"])
def contact():
    """
    Handle the contact form submission.

    If the request method is POST, validate the form data and send an email.
    If the validation fails, display error messages. If successful, redirect
    to the success page.

    Returns:
        str: Rendered template for the contact page
        or redirect to success page.
    """

    form = ContactForm()
    if form.validate_on_submit():  # Validate the form on submission
        if form.honeypot.data:
            # Honeypot field filled -> likely spam
            flash('Spam detected. Submission rejected.')
            return redirect(url_for('contact'))
        content = form.message.data
        sender = form.name.data
        address = form.email.data

        msg = Message(
            "Feedback Message on The Devil's Dictionary App",
            recipients=[os.environ.get("MAIL_USERNAME")]
        )
        msg.body = f"{sender} ({address}) says: '{content}'."

        recaptcha_response = request.form.get('g-recaptcha-response')
        verify_url = 'https://www.google.com/recaptcha/api/siteverify'
        payload = {
            'secret': app.config["RECAPTCHA_SECRET_KEY"],
            'response': recaptcha_response
            }

        recaptcha_result = requests.post(verify_url, data=payload).json()
    
        if not recaptcha_result.get('success'):
            flash('Please complete the CAPTCHA.')
            return redirect('/contact')


        with app.app_context():
            try:
                mail.send(msg)
                flash("Message sent successfully!", "success")
                return redirect(url_for('contact_success'))
            except Exception as e:
                app.logger.error(f"Email send failed: {e}")
                flash('There was a problem sending your message. Please try again later.')
                return redirect('/contact')

    return render_template("contact.html", form=form, page_title="Contact", site_key=app.config["SITE_KEY"])


@app.route("/contact/success")
def contact_success():
    """
    Render the Contact Success page.

    Returns:
        str: Rendered template for the Contact Success page.
    """
    return render_template(
        "contact_success.html", page_title="Contact Success"
        )


if __name__ == "__main__":
    """
    Set the port for the application to run on,
    defaulting to 5000 if not specified
    Start the Flask application with host set to 0.0.0.0
    to make it accessible externally
    """
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template("429.html"), 429