import re

# Función para validar una contraseña
def validate_password(password):
    if len(password) < 5:
        return False, 'La contraseña debe tener al menos 5 caracteres'
    
    # if not re.search(r'[A-Z]', password):
    #     return False, 'La contraseña debe contener al menos una letra mayúscula'
    
    if not re.search(r'[a-z]', password):
        return False, 'La contraseña debe contener al menos una letra minúscula'
    
    # if not re.search(r'[0-9]', password):
    #     return False, 'La contraseña debe contener al menos un número'
    
    # if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
    #     return False, 'La contraseña debe contener al menos un carácter especial'
    
    return True, 'Contraseña válida'