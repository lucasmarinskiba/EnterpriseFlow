# app/models.py
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    role = db.Column(db.String(50))
    last_login = db.Column(db.DateTime)

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    plan = db.Column(db.String(50))
    expiry_date = db.Column(db.DateTime)
