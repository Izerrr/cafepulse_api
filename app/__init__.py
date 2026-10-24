import os
from flask import Flask, jsonify, request, Response
from dotenv import load_dotenv
from app.extensions import db
from app.routes.main import main_bp
from app.routes.cafes import cafe_bp

load_dotenv()

def create_app():
    app = Flask(__name__)

    # Konfigurasi Database & Connection Pooling untuk Serverless
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("[WARNING] DATABASE_URL tidak diset! Menggunakan fallback in-memory database.")
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "pool_pre_ping": True,
            "pool_recycle": 300,
        }

    # Inisialisasi Ekstensi
    db.init_app(app)

    # Registrasi Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(cafe_bp)

    # CORS Headers (Memungkinkan Frontend di domain lain/localhost memanggil API)
    @app.before_request
    def handle_options():
        if request.method == "OPTIONS":
            res = Response()
            res.headers["Access-Control-Allow-Origin"] = "*"
            res.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            res.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            return res

    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    # Global JSON Error Handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "status": "error",
            "message": "Resource atau endpoint tidak ditemukan"
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "status": "error",
            "message": "Metode HTTP tidak diizinkan untuk endpoint ini"
        }), 405

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "status": "error",
            "message": "Terjadi kesalahan internal pada server"
        }), 500

    return app

    return app