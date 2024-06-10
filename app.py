from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from models import Usuario, Archivo, Tarea, Grupo, GrupoUsuario, db
from werkzeug.utils import secure_filename   #Para evitar nombres de archivo inseguros
import os


app = Flask(__name__)
app.secret_key = '2c1f2bceaff99004'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'  # Nombre de la base de datos SQLite
db.init_app(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')    #Directorio base donde se guardan los archivos
#ALLOWED_EXTENSIONS = {'txt', 'pdf','jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  #Redireccion para login requerido


#Lsitado de los directorios 
def listar_archivos():
    """user_folder = os.path.join(UPLOAD_FOLDER, current_user.usuario)  #Verifcamos las carpetas por cada usuario 
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)"""
    files = Archivo.query.filter_by(propietario_id=current_user.id).all()
    return files

#Listado de los grupos
def listar_grupos():
    grupos = Grupo.query.join(GrupoUsuario, Grupo.id == GrupoUsuario.grupo_id).filter(GrupoUsuario.usuario_id == current_user.id).all() #Consulta Join de Grupo y GurpoUsuario para devolver los grupos que pertenece
    return grupos


# Función para cargar un usuario
@login_manager.user_loader
def cargar_usuario(usuario_id):
    return Usuario.query.get(int(usuario_id))


# Vista inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        contraseña = request.form['contraseña']
        
        usuario_existente = Usuario.query.filter_by(email = email).first()
        if usuario_existente and usuario_existente.contraseña == contraseña:
            login_user(usuario_existente)
            return redirect(url_for('inicio'))
        else:# Si el usuario no existe
            mensaje = 'Credenciales inválidas. Inténtalo de nuevo.'
            return render_template('login.html', mensaje=mensaje)
    
    return render_template('login.html')

# Vista registro
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        usuario = request.form['usuario']
        email = request.form['email']
        contraseña = request.form['contraseña']
        
        # Verifica si el usuario ya existe
        email_existente = Usuario.query.filter_by(email=email).first()
        if email_existente:
            mensaje = 'El Email ya existe. Por favor, introduce otro email.'
            return render_template('registro.html', mensaje=mensaje)
        else:
            # Crea un nuevo usuario
            nuevo_usuario = Usuario(usuario=usuario,email=email,contraseña=contraseña)
            db.session.add(nuevo_usuario)
            db.session.commit()
            
            # Redirige al usuario al login 
            return redirect(url_for('login'))
    
    return render_template('registro.html')


# Vista Prueba
@app.route('/')
@login_required
def prueba():
    return f'Bienvenido, {current_user.usuario}! <a href="/logout">Cerrar sesión</a>'


@app.route('/home', methods=['GET'])
@login_required
def inicio():
    files=listar_archivos()
    return render_template('home.html', files= files)

# Vista cerrar sesión
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

#Vista archivos  
@app.route('/archivos',methods=['GET'])
@login_required
def archivos():
    # Pasa el usuario conectado 
    files=listar_archivos()
    return render_template('archivos.html', nombre_usuario=current_user.usuario, files= files)


@app.route('/upload',methods=['GET', 'POST'])  #Mantener? Puede ser el post de archivos
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        user_folder = os.path.join(UPLOAD_FOLDER, current_user.usuario)
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)
        file.save(os.path.join(user_folder, filename))
        # Primera forma de entrada en la base de datos
        nuevo_archivo = Archivo(nombre=filename, ruta=os.path.join(user_folder, filename), propietario_id=current_user.id)
        db.session.add(nuevo_archivo)
        db.session.commit()
    return render_template('uploadPop.html')

@app.route('/delete/<nombre_archivo>', methods=['POST'])
@login_required
def delete_archivo(nombre_archivo):
    user_folder = os.path.join(UPLOAD_FOLDER, current_user.usuario)
    archivo = os.path.join(user_folder, nombre_archivo)
    if os.path.exists(archivo):
        os.remove(archivo)
        # Primera forma de elimar en la base de datos 
        archivo_bd = Archivo.query.filter_by(nombre=nombre_archivo, propietario_id=current_user.id).first()
        if archivo_bd:
            db.session.delete(archivo_bd)
            db.session.commit()
    return redirect(url_for('archivos'))  # Recargamos la pagina inico

@app.route('/tareas', methods=['GET', 'POST'])
@login_required
def tareas():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        nueva_tarea = Tarea(titulo=titulo, descripcion=descripcion, propietario_id=current_user.id)
        db.session.add(nueva_tarea)
        db.session.commit()
        return redirect(url_for('tareas'))
    
    tareas = Tarea.query.filter_by(propietario_id=current_user.id).all()
    return render_template('tareas.html',nombre_usuario=current_user.usuario, tareas=tareas)


# Vista para ver grupos
@app.route('/grupos', methods=['GET'])
@login_required
def ver_grupos():


    grupos = listar_grupos()
    return render_template('grupos.html', grupos=grupos)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crea las tablas en la base de datos si no existen
    app.run()






