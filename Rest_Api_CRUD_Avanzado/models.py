from flask_sqlalchemy import SQLAlchemy  # Importa la clase SQLAlchemy del módulo flask_sqlalchemy

db = SQLAlchemy()  # Crea una instancia de la clase SQLAlchemy, que se utilizará para interactuar con la base de datos

class Users(db.Model):
    __tablename__ = 'users'  # Establece el nombre de la tabla en la base de datos como 'users'

    id = db.Column(db.Integer, primary_key=True)  # Define una columna 'id' de tipo Integer y clave primaria
    cedula = db.Column(db.Integer)  # Define una columna 'cedula' de tipo Integer
    nombre = db.Column(db.String(30))  # Define una columna 'nombre' de tipo String con un máximo de 30 caracteres
    apellido = db.Column(db.String(30))  # Define una columna 'apellido' de tipo String con un máximo de 30 caracteres
    rol = db.Column(db.String(20), default='invitado')  # Define una columna 'rol' de tipo String con un valor predeterminado 'invitado'
    correo = db.Column(db.String(100))  # Define una columna 'correo' de tipo String con un máximo de 100 caracteres
    contraseña = db.Column(db.String(200))  # Define una columna 'contraseña' de tipo String con un máximo de 200 caracteres

    def __init__(self, cedula, nombre, apellido, correo, contraseña, rol='invitado'):
        self.cedula = cedula  # Inicializa el atributo 'cedula' con el valor proporcionado
        self.nombre = nombre  # Inicializa el atributo 'nombre' con el valor proporcionado
        self.apellido = apellido  # Inicializa el atributo 'apellido' con el valor proporcionado
        self.rol = rol  # Inicializa el atributo 'rol' con el valor proporcionado (o el valor predeterminado 'invitado')
        self.correo = correo  # Inicializa el atributo 'correo' con el valor proporcionado
        self.contraseña = contraseña  # Inicializa el atributo 'contraseña' con el valor proporcionado

