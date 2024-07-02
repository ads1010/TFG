from flask import Flask, render_template, request, redirect, url_for,send_file, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from models import Usuario, Archivo, Tarea, Grupo, GrupoUsuario, ArchivoGrupo, TareaGrupo, db
from werkzeug.utils import secure_filename   #Para evitar nombres de archivo inseguros
from werkzeug.security import generate_password_hash, check_password_hash
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



def listar_archivos():
    """
   Devuelve todos los archivos del usuario actual
    Returns:
        List[Archivo]: Lista de objetos `Archivo` del usuario actual.
    """
    files = Archivo.query.filter_by(propietario_id=current_user.id).all()
    return files


def listar_grupos():
    """
    Devuelve todos los grupos del usuario actual.
    Returns:
        List[Grupo]: Lista de objetos `Grupo` a los que pertenece el usuario actual.
    """
    grupos = Grupo.query.join(GrupoUsuario, Grupo.id == GrupoUsuario.grupo_id).filter(GrupoUsuario.usuario_id == current_user.id).all() #Consulta Join de Grupo y GurpoUsuario para devolver los grupos que pertenece
    return grupos


# Función para cargar un usuario
@login_manager.user_loader
def cargar_usuario(usuario_id):
    return Usuario.query.get(int(usuario_id))



@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Vista del inicio de sesión de un usuario.
    Returns:
        render_template: Renderiza el template 'login.html'.
    """
    if request.method == 'POST':
        email = request.form['email']
        contraseña = request.form['contraseña']
        
        usuario_existente = Usuario.query.filter_by(email = email).first()
        if usuario_existente and check_password_hash(usuario_existente.contraseña, contraseña):
            login_user(usuario_existente)
            return redirect(url_for('inicio'))
        else:# Si el usuario no existe
            mensaje = 'Credenciales inválidas. Inténtalo de nuevo.'
            return render_template('login.html', mensaje=mensaje)
    
    return render_template('login.html')


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    """
    Vista para el registro de un nuevo usuario.
    Returns:
        render_template: Renderiza el template 'registro.html'.
    """
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
            contraseña_hash = generate_password_hash(contraseña)
            nuevo_usuario = Usuario(usuario=usuario, email=email, contraseña=contraseña_hash)
            db.session.add(nuevo_usuario)
            db.session.commit()
            
            # Redirige al usuario al login 
            return redirect(url_for('login'))
    
    return render_template('registro.html')


# Vista Prueba
@app.route('/')
@login_required
def prueba():
    return redirect(url_for('inicio'))


@app.route('/home', methods=['GET'])
@login_required
def inicio():
    """
    Vista principal del home del usuario.
    Returns:
        render_template: Renderiza el template 'home.html' con los archivos y grupos del usuario actual.
    """
    files=listar_archivos()
    grupos=listar_grupos()
    return render_template('home.html',nombre_usuario=current_user.usuario, files= files, grupos=grupos)


@app.route('/logout')
@login_required
def logout():
    """
    Vista para cerrar la sesión del usuario.
    Returns:
        redirect: Redirige a la página de inicio de sesión.
    """
    logout_user()
    return redirect(url_for('login'))

#Vista archivos  
@app.route('/archivos',methods=['GET'])
@login_required
def archivos():
    """
    Vista principal de  los archivos del usuario
    Returns:
        render_template: Renderiza el template 'archivos.html' con los archivos y grupos del usuario.
    """
    files=listar_archivos()
    grupos=listar_grupos()
    return render_template('archivos.html', nombre_usuario=current_user.usuario, files= files, grupos= grupos)


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
        return redirect(url_for('archivos'))
    return render_template('uploadPop.html')

@app.route('/delete/<int:archivo_id>', methods=['POST'])
@login_required
def delete_archivo(archivo_id):
    archivo = Archivo.query.get_or_404(archivo_id)
    archivo_path = archivo.ruta
    if os.path.exists(archivo_path):
        os.remove(archivo_path)
        db.session.delete(archivo)
        db.session.commit() #Archivo eliminada de BD y ficheros     
        flash('Archivo eliminado.', 'success') 
    else:
        pass
    return redirect(url_for('archivos'))

@app.route('/descargar/<int:archivo_id>', methods=['GET'])
@login_required
def descargar_archivo(archivo_id):
    archivo = Archivo.query.get_or_404(archivo_id)
    archivo_path = archivo.ruta

    if os.path.exists(archivo_path):
        return send_file(archivo_path, as_attachment=True)
    else:
        flash('El archivo no existe.', 'danger')
        return redirect(url_for('archivos'))

@app.route('/compartir_archivo_grupo', methods=['POST'])
@login_required
def compartir_archivo_grupo():
    archivo_id = request.form['archivo_id']
    grupo_id = request.form['grupo_id']
    
    archivo = Archivo.query.get_or_404(archivo_id)
    grupo = Grupo.query.get_or_404(grupo_id)
    

    archivo_grupo_existente = ArchivoGrupo.query.filter_by(archivo_id=archivo.id, grupo_id=grupo.id).first()
    if archivo_grupo_existente:
        flash('Esate archivo ya esta disponible en este grupo.', 'warning')
    else:
        #Guardamos que el archivo pertener al grupo en la tabla 
        nueva_asociacion = ArchivoGrupo(archivo_id=archivo.id, grupo_id=grupo.id)
        db.session.add(nueva_asociacion)
        db.session.commit()

    return redirect(url_for('archivos'))

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

@app.route('/deletetarea/<int:tarea_id>', methods=['POST'])
@login_required
def delete_tarea(tarea_id):
    tarea = Tarea.query.get_or_404(tarea_id)
    if tarea.propietario_id == current_user.id:
        db.session.delete(tarea)
        db.session.commit()
        flash('Tarea eliminada.', 'success')
    else:
        pass
    return redirect(url_for('tareas'))

@app.route('/editartarea/<int:tarea_id>', methods=['POST'])
@login_required
def editar_tarea(tarea_id):
    tarea = Tarea.query.get_or_404(tarea_id)
    if tarea.propietario_id == current_user.id:
        tarea.titulo = request.form['titulo']
        tarea.descripcion = request.form['descripcion']
        db.session.commit()
        flash('Tarea actualizada.', 'success')
    else:
        pass
    return redirect(url_for('tareas'))

# Vista para ver grupos
@app.route('/grupos', methods=['GET'])
@login_required
def ver_grupos():
    grupos = listar_grupos()
    return render_template('grupos.html', nombre_usuario=current_user.usuario, grupos=grupos)

# crear grupo
@app.route('/crear_grupo', methods=['POST'])
@login_required
def crear_grupo():
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    nuevo_grupo = Grupo(nombre=nombre, descripcion=descripcion, propietario_id=current_user.id)
    db.session.add(nuevo_grupo)
    db.session.commit()

    # tine que ser miembro del propio grupo
    grupo_usuario = GrupoUsuario(usuario_id=current_user.id, grupo_id=nuevo_grupo.id)
    db.session.add(grupo_usuario)
    db.session.commit()
    return redirect(url_for('ver_grupos'))


@app.route('/grupo/<int:grupo_id>', methods=['GET'])
@login_required
def ver_grupo(grupo_id):
    grupo = Grupo.query.get_or_404(grupo_id)
    archivos = grupo.archivos  
    tareas = grupo.tareas  
    miembros = Usuario.query.join(GrupoUsuario).filter(GrupoUsuario.grupo_id == grupo_id).all()
    return render_template('grupo.html', grupo=grupo, archivos=archivos, tareas=tareas, miembros=miembros)

@app.route('/delete_grupo/<int:grupo_id>', methods=['POST'])
@login_required
def delete_grupo(grupo_id):
    grupo = Grupo.query.get_or_404(grupo_id)
    if grupo.propietario_id == current_user.id:
        db.session.delete(grupo)
        db.session.commit()
        flash('Grupo eliminado.', 'eliminado')
    else:
        pass
    return redirect(url_for('ver_grupos'))

@app.route('/invitar/<int:grupo_id>', methods=['POST'])
@login_required
def invitar_usuario(grupo_id):
    email = request.form['email']
    usuario = Usuario.query.filter_by(email=email).first()
    grupo = Grupo.query.get_or_404(grupo_id)

    if not usuario:
        flash('El usuario no existe.', 'danger')
        return redirect(url_for('ver_grupo', grupo_id=grupo_id))
    
    if usuario in grupo.usuarios:
        flash('El usuario es miembro del grupo.', 'warning')
        return redirect(url_for('ver_grupo', grupo_id=grupo_id))

    nuevo_miembro = GrupoUsuario(usuario_id=usuario.id, grupo_id=grupo.id)
    db.session.add(nuevo_miembro)
    db.session.commit()
    flash('Usuario invitado.', 'success')
    
    return redirect(url_for('ver_grupo', grupo_id=grupo_id))

@app.route('/eliminar_miembro/<int:grupo_id>', methods=['POST'])
@login_required
def eliminar_miembro(grupo_id):
    grupo = Grupo.query.get_or_404(grupo_id)
    usuario_id = request.form['usuario_id']
    grupo_usuario = GrupoUsuario.query.filter_by(grupo_id=grupo_id, usuario_id=usuario_id).first()  

    if grupo_usuario:
        db.session.delete(grupo_usuario)
        db.session.commit()
        flash('Usuario eliminado del grupo.', 'success')
    else:
        flash('El usuario no pertenece al grupo.', 'warning')
    
    return redirect(url_for('ver_grupo', grupo_id=grupo_id))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crea las tablas en la base de datos si no existen
    app.run()






