import os
from flask import Blueprint, jsonify
from app.extensions import db
from app.models.cafe import Cafe

main_bp = Blueprint("main", __name__)

@main_bp.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "success",
        "name": "CafePulse REST API",
        "version": "1.0.0",
        "description": "Modular REST API for Cafe & Coworking Space Management with PostgreSQL Supabase",
        "endpoints": {
            "health_check": "GET /",
            "db_check": "GET /db-check",
            "list_cafes": "GET /api/cafes",
            "cafe_detail": "GET /api/cafes/<int:cafe_id>",
            "create_cafe": "POST /api/cafes",
            "update_cafe": "PUT or PATCH /api/cafes/<int:cafe_id>",
            "delete_cafe": "DELETE /api/cafes/<int:cafe_id>"
        }
    }), 200

@main_bp.route("/db-check", methods=["GET"])
def db_check():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        return jsonify({
            "status": "error",
            "message": "DATABASE_URL belum dikonfigurasi di Environment Variables Vercel! Silakan buka Dashboard Vercel -> Settings -> Environment Variables, tambahkan DATABASE_URL, lalu lakukan Redeploy."
        }), 500

    try:
        # Validasi koneksi langsung ke Supabase
        db.session.execute(db.select(1))
        cafe_count = Cafe.query.count()
        return jsonify({
            "status": "success",
            "database": "Terhubung ke Supabase PostgreSQL!",
            "schema": "cafepulse",
            "stats": {
                "active_cafes": cafe_count
            }
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Koneksi database gagal: {str(e)}"
        }), 500
        return jsonify({
            "status": "error",
            "message": f"Koneksi database gagal: {str(e)}"
        }), 500
