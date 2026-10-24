from datetime import datetime, timezone
from app.extensions import db

class User(db.Model):
    __tablename__ = "users"
    __table_args__ = {"schema": "cafepulse"}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(
        db.Enum("CUSTOMER", "CAFE_OWNER", "ADMIN", name="user_role_enum", schema="cafepulse", create_type=False),
        default="CUSTOMER"
    )
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    cafes = db.relationship("Cafe", backref="owner", lazy=True, cascade="all, delete-orphan")
    reviews = db.relationship("Review", backref="user", lazy=True, cascade="all, delete-orphan")
    preorders = db.relationship("Preorder", backref="user", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Cafe(db.Model):
    __tablename__ = "cafes"
    __table_args__ = {"schema": "cafepulse"}

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("cafepulse.users.id", ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.Numeric(10, 8), nullable=False)
    longitude = db.Column(db.Numeric(11, 8), nullable=False)
    opening_hours = db.Column(db.String(100), nullable=False)
    crowd_density = db.Column(
        db.Enum("LOW", "MODERATE", "FULL", name="crowd_level_enum", schema="cafepulse", create_type=False),
        nullable=True
    )
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    amenities = db.relationship("CafeAmenity", backref="cafe", uselist=False, cascade="all, delete-orphan")
    reviews = db.relationship("Review", backref="cafe", lazy=True, cascade="all, delete-orphan")
    menu_items = db.relationship("MenuItem", backref="cafe", lazy=True, cascade="all, delete-orphan")
    preorders = db.relationship("Preorder", backref="cafe", lazy=True, cascade="all, delete-orphan")

    def to_dict(self, include_reviews=False):
        data = {
            "id": self.id,
            "owner_id": self.owner_id,
            "name": self.name,
            "address": self.address,
            "latitude": float(self.latitude) if self.latitude is not None else None,
            "longitude": float(self.longitude) if self.longitude is not None else None,
            "opening_hours": self.opening_hours,
            "crowd_density": self.crowd_density,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "amenities": self.amenities.to_dict() if self.amenities else None,
            "total_reviews": len(self.reviews) if self.reviews else 0
        }
        if include_reviews:
            data["reviews"] = [r.to_dict() for r in self.reviews]
        return data


class CafeAmenity(db.Model):
    __tablename__ = "cafe_amenities"
    __table_args__ = {"schema": "cafepulse"}

    id = db.Column(db.Integer, primary_key=True)
    cafe_id = db.Column(db.Integer, db.ForeignKey("cafepulse.cafes.id", ondelete="CASCADE"), nullable=False, unique=True)
    wifi_speed_mbps = db.Column(db.Integer)
    wifi_stability = db.Column(
        db.Enum("POOR", "FAIR", "EXCELLENT", name="wifi_stability_enum", schema="cafepulse", create_type=False)
    )
    plug_score = db.Column(
        db.Enum("NONE", "LIMITED", "PLENTY", name="plug_score_enum", schema="cafepulse", create_type=False)
    )
    noise_level = db.Column(
        db.Enum("QUIET", "MODERATE", "NOISY", name="noise_level_enum", schema="cafepulse", create_type=False)
    )
    has_outdoor = db.Column(db.Boolean, default=False)
    has_prayer_room = db.Column(db.Boolean, default=False)
    air_conditioned = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "cafe_id": self.cafe_id,
            "wifi_speed_mbps": self.wifi_speed_mbps,
            "wifi_stability": self.wifi_stability,
            "plug_score": self.plug_score,
            "noise_level": self.noise_level,
            "has_outdoor": self.has_outdoor,
            "has_prayer_room": self.has_prayer_room,
            "air_conditioned": self.air_conditioned,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class Review(db.Model):
    __tablename__ = "reviews"
    __table_args__ = {"schema": "cafepulse"}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("cafepulse.users.id", ondelete="CASCADE"), nullable=False)
    cafe_id = db.Column(db.Integer, db.ForeignKey("cafepulse.cafes.id", ondelete="CASCADE"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    verified_wifi_speed = db.Column(db.Integer)
    verified_crowd = db.Column(
        db.Enum("LOW", "MODERATE", "FULL", name="crowd_level_enum", schema="cafepulse", create_type=False)
    )
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "cafe_id": self.cafe_id,
            "rating": self.rating,
            "comment": self.comment,
            "verified_wifi_speed": self.verified_wifi_speed,
            "verified_crowd": self.verified_crowd,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class MenuItem(db.Model):
    __tablename__ = "menu_items"
    __table_args__ = {"schema": "cafepulse"}

    id = db.Column(db.Integer, primary_key=True)
    cafe_id = db.Column(db.Integer, db.ForeignKey("cafepulse.cafes.id", ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(
        db.Enum("COFFEE", "NON_COFFEE", "MEAL", "SNACK", "DESSERT", name="menu_category_enum", schema="cafepulse", create_type=False),
        nullable=False
    )
    price = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "cafe_id": self.cafe_id,
            "name": self.name,
            "category": self.category,
            "price": float(self.price) if self.price is not None else 0.0,
            "description": self.description,
            "is_available": self.is_available,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Preorder(db.Model):
    __tablename__ = "preorders"
    __table_args__ = {"schema": "cafepulse"}

    id = db.Column(db.Integer, primary_key=True)
    order_code = db.Column(db.String(50), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("cafepulse.users.id", ondelete="CASCADE"), nullable=False)
    cafe_id = db.Column(db.Integer, db.ForeignKey("cafepulse.cafes.id", ondelete="CASCADE"), nullable=False)
    pickup_time = db.Column(db.DateTime(timezone=True), nullable=False)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    workflow_status = db.Column(
        db.Enum("QUEUED", "BREWING", "READY_FOR_PICKUP", "COMPLETED", "CANCELLED", name="order_workflow_enum", schema="cafepulse", create_type=False),
        default="QUEUED"
    )
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    items = db.relationship("OrderItem", backref="order", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "order_code": self.order_code,
            "user_id": self.user_id,
            "cafe_id": self.cafe_id,
            "pickup_time": self.pickup_time.isoformat() if self.pickup_time else None,
            "total_amount": float(self.total_amount) if self.total_amount is not None else 0.0,
            "workflow_status": self.workflow_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "items": [item.to_dict() for item in self.items]
        }


class OrderItem(db.Model):
    __tablename__ = "order_items"
    __table_args__ = {"schema": "cafepulse"}

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("cafepulse.preorders.id", ondelete="CASCADE"), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey("cafepulse.menu_items.id", ondelete="RESTRICT"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)
    notes = db.Column(db.String(255))

    menu_item = db.relationship("MenuItem", backref="order_items", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "menu_item_id": self.menu_item_id,
            "menu_item_name": self.menu_item.name if self.menu_item else None,
            "quantity": self.quantity,
            "unit_price": float(self.unit_price) if self.unit_price is not None else 0.0,
            "subtotal": float(self.subtotal) if self.subtotal is not None else 0.0,
            "notes": self.notes
        }
    comment = db.Column(db.Text)