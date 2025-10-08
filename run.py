from app import create_app

# Create Flask app instance using the factory
app = create_app()

if __name__ == "__main__":
    # Development mode only; disable in production
    app.run(debug=True, host="0.0.0.0", port=5000)
