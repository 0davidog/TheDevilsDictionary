import os
import json
from flask import Flask, render_template, request, flash
if os.path.exists("env.py"):
    import env

app = Flask(__name__)  # Create an instance of the Flask class and store it in the app variable
app.secret_key = os.environ.get("SECRET_KEY")


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


def custom_title(value):
    ignore_words = ['or']
    words = value.split()
    title_cased_words = [word.title() if word.lower() not in ignore_words else word.lower() for word in words]
    return ' '.join(title_cased_words)

# Register the custom filter with the Flask app
app.jinja_env.filters['custom_title'] = custom_title


@app.route("/")  # Decorator to associate the index() function with the root URL ("/")
def index():  # Define a function called index, which will be executed when the root URL is accessed
    letters = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
    return render_template("index.html", page_title="Index", letters=letters)


@app.route("/<listing_name>")
def listing(listing_name):
    data = []

    try:
        with open("data/" + listing_name + ".json", "r") as json_data:
            data = json.load(json_data)
    except FileNotFoundError:
        # Handle the case where the file does not exist
        pass

    return render_template("listing.html", listing_name=listing_name, listings=data)


@app.route("/<listing_name>/<entry_name>")
def entry(listing_name, entry_name):
    entry = {}

    # Replace underscores with spaces in the entry_name and return to uppercase to match data.
    entry_name = entry_name.replace("_", " ").upper()

    try:
        with open(f"data/{listing_name}.json", "r") as json_data:
            data = json.load(json_data)
            for obj in data:
                if obj["name"] == entry_name:
                    entry = obj
                    break
    except FileNotFoundError:
        # Handle the case where the file does not exist
        pass

    return render_template("entry.html", entry=entry)


@app.route("/about")
def about():
    return render_template("about.html", page_title="About")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        flash("Thanks {}, we have received your message!".format(
            request.form.get("name")))
    return render_template("contact.html", page_title="Contact")


if __name__ == "__main__":  # Check if the script is being run directly (not imported as a module)
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


