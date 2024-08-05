import os
import json
from flask import Flask, render_template, request, flash
from flask_mail import Mail, Message
import random
import logging

if os.path.exists("env.py"):
    import env

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

# Configuration settings
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USER")
app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASS")
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get("MAIL_USER")

# Initialize the Mail object
mail = Mail(app)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

def custom_title(value):
    ignore_words = ['or']
    words = value.split()
    title_cased_words = [word.title() if word.lower() not in ignore_words else word.lower() for word in words]
    return ' '.join(title_cased_words)

app.jinja_env.filters['custom_title'] = custom_title

@app.route("/")
def index():
    letters = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
    random_letter = random.choice(letters)

    random_entry = None
    try:
        file_path = os.path.join(app.root_path, 'data', f"{random_letter.lower()}.json")
        app.logger.debug(f"Loading JSON file from: {file_path}")
        with open(file_path, "r") as json_data:
            data = json.load(json_data)
            if data:
                random_entry = random.choice(data)
                if not isinstance(random_entry, dict) or 'name' not in random_entry:
                    raise ValueError("Invalid data format: Each entry must be a dictionary with a 'name' key.")
    except (FileNotFoundError, ValueError) as e:
        app.logger.error(f"Error loading JSON file: {e}")
        random_entry = {"name": "File not found or invalid data format."}

    return render_template("index.html", page_title="Index", letters=letters, random=random_entry, listing_name=random_letter)

@app.route("/<listing_name>")
def listing(listing_name):
    data = []
    letters = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
    current_index = letters.index(listing_name.upper())
    prev_letter = letters[current_index - 1] if current_index > 0 else None
    next_letter = letters[current_index + 1] if current_index < len(letters) - 1 else None

    try:
        file_path = os.path.join(app.root_path, 'data', f"{listing_name.lower()}.json")
        app.logger.debug(f"Loading JSON file from: {file_path}")
        with open(file_path, "r") as json_data:
            data = json.load(json_data)
    except FileNotFoundError:
        app.logger.error(f"JSON file not found: {file_path}")

    return render_template("listing.html", listing_name=listing_name, listings=data, prev_letter=prev_letter, next_letter=next_letter)

@app.route("/<listing_name>/<entry_name>")
def entry(listing_name, entry_name):
    entry = {}
    entry_name = entry_name.replace("_", " ").upper()

    try:
        file_path = os.path.join(app.root_path, 'data', f"{listing_name.lower()}.json")
        app.logger.debug(f"Loading JSON file from: {file_path}")
        with open(file_path, "r") as json_data:
            data = json.load(json_data)
            for obj in data:
                if obj["name"] == entry_name:
                    entry = obj
                    break
    except FileNotFoundError:
        app.logger.error(f"JSON file not found: {file_path}")

    return render_template("entry.html", entry=entry)

@app.route("/about")
def about():
    return render_template("about.html", page_title="About")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        content = request.form.get("message")
        sender = request.form.get("name")
        address = request.form.get("email")

        msg = Message(
            "Feedback Message on The Devil's Dictionary App",
            recipients=[os.environ.get("MAIL_USER")]
        )
        msg.body = f"{sender} ({address}) says: '{content}'."
    
        with app.app_context():
            mail.send(msg)
            flash("Thanks {}, we have received your message!".format(request.form.get("name")))
        
    return render_template("contact.html", page_title="Contact")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
