from flask import Flask, jsonify, request, g, session
from models import db, Users 
import bcrypt
from valid_password import validate_password

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:12345678@localhost:3307/my_projects'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'my_secret_key'
db.init_app(app)  # Inicializar la base de datos de Flask

# Middleware para verificar la autenticación del usuario antes de cada solicitud
@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = Users.query.get(session['user_id'])  # Obtener el usuario de la base de datos

@app.route('/')
def index():
    return jsonify({'menszzaje': 'Hola Mundo!'})

# Ruta para el inicio de sesión
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    correo = data.get('correo')
    contraseña = data.get('contraseña')

    if not correo or not contraseña:
        return jsonify({'error': 'Correo y contraseña son obligatorios'}), 400

    usuario = Users.query.filter_by(correo=correo).first()  # Buscar al usuario por su correo

    if usuario and bcrypt.checkpw(contraseña.encode('utf-8'), usuario.contraseña.encode('utf-8')):
        session['user_id'] = usuario.id  # Almacenar el ID del usuario en la sesión
        if usuario.rol == 'admin':
            return jsonify({'message': 'Inicio de sesión exitoso como administrador'}), 200
        else:
            return jsonify({'message': 'Inicio de sesión exitoso como invitado'}), 200

    return jsonify({'message': 'Correo o Contraseña incorrecta'}), 401

# Ruta para el cierre de sesión
@app.route('/logout', methods=['POST'])
def logout():
    # Obtener el rol del usuario antes de limpiar la sesión
    user_rol = g.user.rol if g.user else None

    # Limpiar la sesión
    session.clear()

    # Eliminar información de autenticación
    g.user = None

    if user_rol:
        return jsonify({'message': f'Cierre de sesión exitoso como {user_rol}'}), 200
    
    if g.user is None:
        return jsonify({'error': 'No ha iniciado session'}), 400

# Ruta para el registro de usuarios
@app.route('/registro', methods=['POST']) 
def create_user():
    data = request.get_json()
    
    cedula = data.get('cedula')
    nombre = data.get('nombre')
    apellido = data.get('apellido')
    rol = data.get('rol', 'invitado')
    correo = data.get('correo')
    contraseña = data.get('contraseña')
    
    # Validaciones de campos obligatorios
    if not cedula or not nombre or not apellido or not correo or not contraseña:
        return jsonify({'error': 'Todos los campos son obligatorios'}), 400
    
    # Validar la contraseña
    is_valid_password, message = validate_password(contraseña)
    if not is_valid_password:
        return jsonify({'error': message}), 400
    
    # Verificar duplicados de cédula y correo
    if Users.query.filter_by(cedula=cedula).first():
        return jsonify({'error': 'Ya existe un usuario con la misma cédula'}), 409
    
    if Users.query.filter_by(correo=correo).first():
        return jsonify({'error': 'Ya existe un usuario con el mismo correo'}), 409
    
    # Asegurarse de que solo el administrador pueda asignar roles diferentes de 'invitado'
    if rol != 'invitado' and (g.user is None or g.user.rol != 'admin'):
        return jsonify({'error': 'Solo el administrador puede asignar roles diferentes de "invitado"'}), 403
    
    # Generar el hash de la contraseña
    hashed_password = bcrypt.hashpw(contraseña.encode('utf-8'), bcrypt.gensalt())
    
    # Crear y agregar el nuevo usuario a la base de datos
    new_user = Users(cedula=cedula, nombre=nombre, apellido=apellido, rol=rol ,correo=correo, contraseña=hashed_password)
    db.session.add(new_user) 
    db.session.commit()  
    return jsonify({'message': 'Usuario creado exitosamente'}), 201

# Ruta para mostrar todos los usuarios
@app.route('/user', methods=['GET'])
def show_users():
    usuarios = Users.query.all()
    resultado = []
    
    # Construir la lista de usuarios para la respuesta
    for usuario in usuarios:
        resultado.append({
            'id': usuario.id,
            'cedula': usuario.cedula,
            'nombre': usuario.nombre,
            'apellido': usuario.apellido,
            'correo': usuario.correo
        })
     
    # Verificar si el usuario está registrado
    if g.user is None:
        return jsonify({'error': 'Acceso denegado. Inicia sesión o regístrate'}), 401    
        
    return jsonify(resultado)

# Ruta para consultar un usuario por cédula
@app.route('/user/cedula/<int:cedula>', methods=['GET'])
def show_user_cedula(cedula):
    usuario = Users.query.filter_by(cedula=cedula).first()
    
    if usuario is None:
        return jsonify({'error': 'Usuario no existe'}), 400
    
    # Verificar si el usuario está registrado
    if g.user is None:
        return jsonify({'error': 'Acceso denegado. Inicia sesión o regístrate'}), 401
    
    return jsonify({
        'id': usuario.id,
        'cedula': usuario.cedula,
        'nombre': usuario.nombre,
        'apellido': usuario.apellido,
        'correo': usuario.correo
    })

# Ruta para mostrar un usuario por ID
@app.route('/user/<int:id>', methods=['GET'])
def show_user_id(id):
    usuario = Users.query.get(id)
    
    if usuario is None:
        return jsonify({'error': 'Usuario no existe'}), 400
    
    # Verificar si el usuario está registrado
    if g.user is None:
        return jsonify({'error': 'Acceso denegado. Inicia sesión o regístrate'}), 401
    
    return jsonify({
        'id': usuario.id,
        'cedula': usuario.cedula,
        'nombre': usuario.nombre,
        'apellido': usuario.apellido,
        'correo': usuario.correo
    })

# Ruta para eliminar un usuario por cedula
@app.route('/user/cedula/<int:cedula>', methods=['DELETE'])
def delete_user_cedula(cedula):
    usuario = Users.query.filter_by(cedula=cedula).first()
    
    if usuario is None:
        return jsonify({'error': 'Usuario no existe'}), 400
    
    # Verificar si el usuario está registrado
    if g.user is None:
        return jsonify({'error': 'Acceso denegado. Inicia sesión o regístrate'}), 401
    
    # Verificar si el usuario tiene permiso de administrador para eliminar usuarios
    if g.user.rol != 'admin':
        return jsonify({'error': 'Solo el administrador puede eliminar usuarios'}), 403
    
    # Eliminar el usuario de la base de datos
    db.session.delete(usuario)
    db.session.commit()
    return jsonify({'message': 'Usuario eliminado exitosamente'})

# Ruta para eliminar un usuario por ID
@app.route('/user/<int:id>', methods=['DELETE'])
def delete_user(id):
    usuario = Users.query.get(id)
    
    if usuario is None:
        return jsonify({'error': 'Usuario no existe'}), 400
    
    # Verificar si el usuario está registrado
    if g.user is None:
        return jsonify({'error': 'Acceso denegado. Inicia sesión o regístrate'}), 401
    
    # Verificar si el usuario tiene permiso de administrador para eliminar usuarios
    if g.user.rol != 'admin':
        return jsonify({'error': 'Solo el administrador puede eliminar usuarios'}), 403
    
    # Eliminar el usuario de la base de datos
    db.session.delete(usuario)
    db.session.commit()
    return jsonify({'message': 'Usuario eliminado exitosamente'})

# Ruta para actualizar un usuario por cedular
@app.route('/user/cedula/<int:cedula>', methods=['PUT'])
def update_user_cedula(cedula):
    usuario = Users.query.filter_by(cedula=cedula).first()
    
    if usuario is None:
        return jsonify({'error': 'Usuario no existe'}), 400
    
    # Verificar si el usuario está registrado
    if g.user is None:
        return jsonify({'error': 'Acceso denegado. Inicia sesión o regístrate'}), 401
    
    data = request.get_json()
    
    cedula = data.get('cedula', usuario.cedula)
    nombre = data.get('nombre', usuario.nombre)
    apellido = data.get('apellido', usuario.apellido)
    correo = data.get('correo', usuario.correo)
    contraseña = data.get('contraseña')
    rol = data.get('rol', usuario.rol)
    
    # Verificar si el usuario tiene permiso de administrador para actualizar usuarios
    if g.user.rol != 'admin':
        return jsonify({'error': 'Solo el administrador puede actualizar usuarios'}), 403
    
    # Verificar duplicados de cédula y correo
    if cedula != usuario.cedula and Users.query.filter_by(cedula=cedula).first():
        return jsonify({'error': 'Ya existe un usuario con la misma cedula'}), 409
    
    if correo != usuario.correo and Users.query.filter_by(correo=correo).first():
        return jsonify({'error': 'Ya existe un usuario con el mismo correo'}), 409
    
    if contraseña:
        is_valid_password, message =  validate_password(contraseña)
        if not is_valid_password:
            return jsonify({'error': message}), 400

        hashed_password = bcrypt.hashpw(contraseña.encode('utf-8'), bcrypt.gensalt())
        usuario.contraseña = hashed_password
        
    # Actualizar los detalles del usuario
    usuario.cedula = cedula
    usuario.nombre = nombre
    usuario.apellido = apellido
    usuario.correo = correo
    usuario.rol = rol
    
    db.session.commit()
    return jsonify({'message': 'Usuario actualizado exitosamente'}), 200

# Ruta para actualizar un usuario por ID
@app.route('/user/<int:id>', methods=['PUT'])
def update_user(id):
    usuario = Users.query.get(id)
    
    if usuario is None:
        return jsonify({'error': 'Usuario no existe'}), 400
    
    # Verificar si el usuario está registrado
    if g.user is None:
        return jsonify({'error': 'Acceso denegado. Inicia sesión o regístrate'}), 401
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No se ha proporcionado ningún dato'}), 400  # Retorna un error si no se proporcionaron datos JSON
    
    cedula = data.get('cedula', usuario.cedula)
    nombre = data.get('nombre', usuario.nombre)
    apellido = data.get('apellido', usuario.apellido)
    correo = data.get('correo', usuario.correo)
    contraseña = data.get('contraseña')
    rol = data.get('rol', usuario.rol)
    
    # Verificar si el usuario tiene permiso de administrador para actualizar usuarios
    if g.user.rol != 'admin':
        return jsonify({'error': 'Solo el administrador puede actualizar usuarios'}), 403
    
    # Verificar duplicados de cédula y correo
    if cedula != usuario.cedula and Users.query.filter_by(cedula=cedula).first():
        return jsonify({'error': 'Ya existe un usuario con la misma cedula'}), 409
    
    if correo != usuario.correo and Users.query.filter_by(correo=correo).first():
        return jsonify({'error': 'Ya existe un usuario con el mismo correo'}), 409

    if contraseña:

        is_valid_password, message =  validate_password(contraseña)
        if not is_valid_password:
            return jsonify({'error': message}), 400
        
        hashed_password = bcrypt.hashpw(contraseña.encode('utf-8'), bcrypt.gensalt())
        usuario.contraseña = hashed_password
        
    # Actualizar los detalles del usuario
    usuario.cedula = cedula
    usuario.nombre = nombre
    usuario.apellido = apellido
    usuario.correo = correo
    usuario.rol = rol
    
    db.session.commit()
    return jsonify({'message': 'Usuario actualizado exitosamente'}), 200

# Verificar si el script se está ejecutando directamente y no importado
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crear las tablas en la base de datos
    app.run(debug=True)  # Ejecutar la aplicación en modo de depuración
