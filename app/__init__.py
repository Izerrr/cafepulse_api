import os
from flask import Flask
from dotenv import load_dotenv
from app.extensions import db

load_dotenv()

def create_app():
    app = Flask(__name__)

    # Konfigurasi Database dari .env
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Bind SQLAlchemy ke instance app
    db.init_app(app)

    # Endpoint 1: Health check app Flask
    @app.route("/", methods=["GET"])
    def index():
        return {
            "status": "success",
            "project": "CafePulse REST API",
            "message": "Engine Flask backend berhasil berjalan!"
        }, 200

    # Endpoint 2: Health check koneksi ke Supabase PostgreSQL
    @app.route("/db-check", methods=["GET"])
    def check_db():
        try:
            # Query ping sederhana
            db.session.execute(db.select(1))
            return {
                "status": "success",
                "database": "Terhubung sempurna ke Supabase PostgreSQL!",
                "schema": "cafepulse"
            }, 200
        except Exception as e:
            return {
                "status": "error",
                "message": f"Koneksi database gagal: {str(e)}"
            }, 500

    return app