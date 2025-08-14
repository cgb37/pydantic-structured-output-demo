from webapp import create_app
from quart import jsonify

# Create the modular app from the package factory
app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
