import os
import json
from flask import Flask, render_template

app = Flask(__name__)  # Create an instance of the Flask class and store it in the app variable


@app.route("/")  # Decorator to associate the index() function with the root URL ("/")
def index():  # Define a function called index, which will be executed when the root URL is accessed
    letters = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
    return render_template("index.html", page_title="Index", letters=letters)


@app.route("/<listing_name>")
def listing(listing_name):
    data = []

    with open("data/" + listing_name + ".json", "r") as json_data:
        data = json.load(json_data)
    return render_template("listing.html", listing_name=listing_name, listings=data)


@app.route("/<listing_name>/<entry_name>")
def a_entry(listing_name, entry_name):
    entry = {}
    with open("data/" + listing_name + ".json", "r") as json_data:
        data = json.load(json_data)
        for obj in data:
            if obj["name"] == entry_name:
                entry = obj
    return render_template("entry.html", entry=entry)


@app.route("/about")
def about():
    return render_template("about.html", page_title="About")


if __name__ == "__main__":  # Check if the script is being run directly (not imported as a module)
    app.run(  # Start the Flask development server
        host=os.environ.get("IP", "0.0.0.0"),  # Get the IP address from the environment variable "IP" or default to "0.0.0.0"
        port=int(os.environ.get("IP", "5000")),  # Get the port number from the environment variable "IP" or default to 5000
        debug=True  # Enable debug mode for the Flask application
    )
