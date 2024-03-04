from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(100), unique=True, nullable=False)
    contraseña = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)  # Necesario para flask-login

    
    @property
    def is_authenticated(self):
        return True  # Necesario para flask-login

    """@property
    def is_active(self):
        return self.is_active"""

    @property
    def is_anonymous(self):
        return False  #No tenemos ususarios anonimos

    def get_id(self):
        return str(self.id)