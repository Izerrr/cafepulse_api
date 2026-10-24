from decimal import Decimal
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.cafe import Cafe, CafeAmenity

cafe_bp = Blueprint("cafes", __name__, url_prefix="/api/cafes")

# 1. READ ALL (GET /api/cafes)
@cafe_bp.route("", methods=["GET"])
def get_cafes():
    try:
        # Opsional filter query params
        crowd = request.args.get("crowd_density")
        search = request.args.get("q")

        query = Cafe.query.filter_by(is_active=True)
        if crowd:
            query = query.filter(Cafe.crowd_density == crowd.upper())
        if search:
            query = query.filter(Cafe.name.ilike(f"%{search}%"))

        cafes = query.order_by(Cafe.id.asc()).all()
        return jsonify({
            "status": "success",
            "total": len(cafes),
            "data": [c.to_dict() for c in cafes]
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Gagal mengambil data kafe: {str(e)}"
        }), 500


# 2. READ ONE (GET /api/cafes/<int:cafe_id>)
@cafe_bp.route("/<int:cafe_id>", methods=["GET"])
def get_cafe(cafe_id):
    try:
        cafe = db.session.get(Cafe, cafe_id)
        if not cafe:
            return jsonify({
                "status": "error",
                "message": f"Kafe dengan ID {cafe_id} tidak ditemukan"
            }), 404

        return jsonify({
            "status": "success",
            "data": cafe.to_dict(include_reviews=True)
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Gagal mengambil detail kafe: {str(e)}"
        }), 500


# 3. CREATE (POST /api/cafes)
@cafe_bp.route("", methods=["POST"])
def create_cafe():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error",
                "message": "Payload JSON tidak boleh kosong"
            }), 400

        # Validasi field wajib
        if not data.get("name") or not data.get("address"):
            return jsonify({
                "status": "error",
                "message": "Field 'name' dan 'address' wajib diisi"
            }), 400

        # Penyiapan nilai dengan default aman
        owner_id = int(data.get("owner_id", 1))
        latitude = Decimal(str(data.get("latitude", -7.56000000)))
        longitude = Decimal(str(data.get("longitude", 110.82000000)))
        opening_hours = data.get("opening_hours", "08:00 - 22:00")
        crowd_density = data.get("crowd_density", "LOW").upper()
        is_active = data.get("is_active", True)

        new_cafe = Cafe(
            owner_id=owner_id,
            name=data["name"].strip(),
            address=data["address"].strip(),
            latitude=latitude,
            longitude=longitude,
            opening_hours=opening_hours,
            crowd_density=crowd_density,
            is_active=is_active
        )
        db.session.add(new_cafe)
        db.session.flush()  # Dapatkan ID kafe baru

        # Tambahkan amenities bila ada di payload
        amenities_data = data.get("amenities")
        if amenities_data and isinstance(amenities_data, dict):
            amenity = CafeAmenity(
                cafe_id=new_cafe.id,
                wifi_speed_mbps=amenities_data.get("wifi_speed_mbps", 50),
                wifi_stability=amenities_data.get("wifi_stability", "EXCELLENT").upper(),
                plug_score=amenities_data.get("plug_score", "PLENTY").upper(),
                noise_level=amenities_data.get("noise_level", "QUIET").upper(),
                has_outdoor=amenities_data.get("has_outdoor", False),
                has_prayer_room=amenities_data.get("has_prayer_room", False),
                air_conditioned=amenities_data.get("air_conditioned", True)
            )
            db.session.add(amenity)

        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "Data kafe berhasil ditambahkan",
            "data": new_cafe.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": f"Gagal menambahkan data kafe: {str(e)}"
        }), 500


# 4. UPDATE (PUT /api/cafes/<int:cafe_id>)
@cafe_bp.route("/<int:cafe_id>", methods=["PUT"])
def update_cafe(cafe_id):
    try:
        cafe = db.session.get(Cafe, cafe_id)
        if not cafe:
            return jsonify({
                "status": "error",
                "message": f"Kafe dengan ID {cafe_id} tidak ditemukan"
            }), 404

        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error",
                "message": "Payload JSON tidak boleh kosong"
            }), 400

        # Update atribut kafe jika disediakan di request
        if "name" in data:
            cafe.name = data["name"].strip()
        if "address" in data:
            cafe.address = data["address"].strip()
        if "latitude" in data:
            cafe.latitude = Decimal(str(data["latitude"]))
        if "longitude" in data:
            cafe.longitude = Decimal(str(data["longitude"]))
        if "opening_hours" in data:
            cafe.opening_hours = data["opening_hours"]
        if "crowd_density" in data:
            cafe.crowd_density = data["crowd_density"].upper()
        if "is_active" in data:
            cafe.is_active = bool(data["is_active"])

        cafe.updated_at = datetime.now(timezone.utc)

        # Update amenities jika disediakan di request
        amenities_data = data.get("amenities")
        if amenities_data and isinstance(amenities_data, dict):
            if cafe.amenities:
                if "wifi_speed_mbps" in amenities_data:
                    cafe.amenities.wifi_speed_mbps = amenities_data["wifi_speed_mbps"]
                if "wifi_stability" in amenities_data:
                    cafe.amenities.wifi_stability = amenities_data["wifi_stability"].upper()
                if "plug_score" in amenities_data:
                    cafe.amenities.plug_score = amenities_data["plug_score"].upper()
                if "noise_level" in amenities_data:
                    cafe.amenities.noise_level = amenities_data["noise_level"].upper()
                if "has_outdoor" in amenities_data:
                    cafe.amenities.has_outdoor = bool(amenities_data["has_outdoor"])
                if "has_prayer_room" in amenities_data:
                    cafe.amenities.has_prayer_room = bool(amenities_data["has_prayer_room"])
                if "air_conditioned" in amenities_data:
                    cafe.amenities.air_conditioned = bool(amenities_data["air_conditioned"])
                cafe.amenities.updated_at = datetime.now(timezone.utc)
            else:
                new_amenity = CafeAmenity(
                    cafe_id=cafe.id,
                    wifi_speed_mbps=amenities_data.get("wifi_speed_mbps", 50),
                    wifi_stability=amenities_data.get("wifi_stability", "EXCELLENT").upper(),
                    plug_score=amenities_data.get("plug_score", "PLENTY").upper(),
                    noise_level=amenities_data.get("noise_level", "QUIET").upper(),
                    has_outdoor=amenities_data.get("has_outdoor", False),
                    has_prayer_room=amenities_data.get("has_prayer_room", False),
                    air_conditioned=amenities_data.get("air_conditioned", True)
                )
                db.session.add(new_amenity)

        db.session.commit()
        return jsonify({
            "status": "success",
            "message": f"Data kafe dengan ID {cafe_id} berhasil diperbarui",
            "data": cafe.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": f"Gagal memperbarui data kafe: {str(e)}"
        }), 500


# 5. DELETE (DELETE /api/cafes/<int:cafe_id>)
@cafe_bp.route("/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    try:
        cafe = db.session.get(Cafe, cafe_id)
        if not cafe:
            return jsonify({
                "status": "error",
                "message": f"Kafe dengan ID {cafe_id} tidak ditemukan"
            }), 404

        cafe_name = cafe.name
        db.session.delete(cafe)
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": f"Kafe '{cafe_name}' (ID: {cafe_id}) berhasil dihapus"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": f"Gagal menghapus data kafe: {str(e)}"
        }), 500
