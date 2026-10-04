from flask_sqlalchemy import SQLAlchemy

# Inisialisasi db terpisah untuk mencegah circular import
db = SQLAlchemy()