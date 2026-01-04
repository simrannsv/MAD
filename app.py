import os
import sys
from llm_server import app  # Import your main app

# Hugging Face Spaces uses port 7860 by default
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    app.run(host="0.0.0.0", port=port)

    