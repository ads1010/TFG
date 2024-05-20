from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
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


class Archivo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    ruta = db.Column(db.String(255), nullable=False)
    propietario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    fecha_subida = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) #Se trabaja directamente aqui por lo que no es necesario introducirlo al crear el Archivo


class CompartirArchivo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    archivo_id = db.Column(db.Integer, db.ForeignKey('archivo.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)


class Tarea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    propietario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class CompartirTarea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tarea_id = db.Column(db.Integer, db.ForeignKey('tarea.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
