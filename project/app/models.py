from app import db
import uuid


class Account(db.Model):
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    password = db.Column(db.String(32), nullable=False)
    role = db.Column(db.String(10), default="user")


class Profile(db.Model):
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    id_account = db.Column(db.String, db.ForeignKey("account.id"), nullable=False)
    nik = db.Column(db.String(16), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    pob = db.Column(db.String(50), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    religion = db.Column(db.String(15), nullable=False)
    marital_status = db.Column(db.String(50), nullable=False)
    nationality = db.Column(db.String(10), nullable=False)
    ktp_url = db.Column(db.String, nullable=True)
    photo_url = db.Column(db.String, nullable=True)


class Address(db.Model):
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    id_user = db.Column(db.String, db.ForeignKey("account.id"), nullable=False)
    province = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    subdistrict = db.Column(db.String(100), nullable=False)
    village = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    rt = db.Column(db.String(3), nullable=False)
    rw = db.Column(db.String(3), nullable=False)
