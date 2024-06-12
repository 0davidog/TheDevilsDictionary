import os  
from flask import Flask, render_template

app = Flask(__name__)  # Create an instance of the Flask class and store it in the app variable


@app.route("/")  # Decorator to associate the index() function with the root URL ("/")
def index():  # Define a function called index, which will be executed when the root URL is accessed
    return render_template("index.html", page_title="Index")


@app.route("/about")
def about():
    return render_template("about.html", page_title="About")


if __name__ == "__main__":  # Check if the script is being run directly (not imported as a module)
    app.run(  # Start the Flask development server
        host=os.environ.get("IP", "0.0.0.0"),  # Get the IP address from the environment variable "IP" or default to "0.0.0.0"
        port=int(os.environ.get("IP", "5000")),  # Get the port number from the environment variable "IP" or default to 5000
        debug=True  # Enable debug mode for the Flask application
    )
