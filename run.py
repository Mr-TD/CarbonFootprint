import os
from app import create_app

# Use production as default for Hugging Face Spaces
config_name = os.environ.get("FLASK_ENV", "production")
app = create_app(config_name)

if __name__ == "__main__":
    # Standard Flask entrypoint for running directly
    port = int(os.environ.get("PORT", 7860))
    app.run(host="0.0.0.0", port=port)
