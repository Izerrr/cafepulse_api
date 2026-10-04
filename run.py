import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True") == "True"

    print(f"[*] Server CafePulse API berjalan pada port {port} (Debug={debug})")
    app.run(host="0.0.0.0", port=port, debug=debug)