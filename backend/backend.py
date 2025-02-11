from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from datetime import datetime
import json
import os
import pathlib

app = Flask(__name__)
CORS(app)
ma = Marshmallow(app)



script_dir = pathlib.Path(__file__).parent.absolute()
DATA_FILE = script_dir / 'data.json'

# Función para cargar datos desde el archivo JSON
def cargar_datos():
    print(DATA_FILE)
    if not os.path.exists(DATA_FILE):
        print("hola")
        return {"usuarios": [], "historial": []}
    with open(DATA_FILE, 'r', encoding='utf-8') as file:
        return json.load(file)

# Función para guardar datos en el archivo JSON
def guardar_datos(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)







# Definir esquemas de validación con Marshmallow
class UsuarioSchema(ma.Schema):
    class Meta:
        fields = ('correo', 'nombre', 'apellidos', 'matricula1', 'matricula2')

    correo = ma.Email(required=True)
    nombre = ma.String(required=True)
    apellidos = ma.String(required=True)
    matricula1 = ma.String(required=True)
    matricula2 = ma.String()



class HistorialSchema(ma.Schema):
    class Meta:
        fields = ('matricula', 'fecha', 'permitido', 'usuario_id')

    matricula = ma.String(required=True)
    fecha = ma.Date(required=False)
    permitido = ma.Boolean(required=True)
    usuario_id = ma.Integer(required=False)



usuario_schema = UsuarioSchema()
historial_schema = HistorialSchema()








# Endpoint para crear un usuario con validación
@app.route('/usuarios', methods=['POST'])
def crear_usuario():
    data = request.get_json()
    datos = cargar_datos()

    # Validar datos de usuario
    errors = usuario_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    # Crear un nuevo usuario con un ID único
    nuevo_usuario = {
        "id": len(datos["usuarios"]) + 1,
        "correo": data["correo"],
        "nombre": data["nombre"],
        "apellidos": data["apellidos"],
        "matricula1": data["matricula1"],
        "matricula2": data["matricula2"]
    }

    # Verificar que no exista un usuario con el mismo correo
    if any(usuario["correo"] == nuevo_usuario["correo"] for usuario in datos["usuarios"]):
        return jsonify({"error": "El correo ya existe"}), 400

    datos["usuarios"].append(nuevo_usuario)
    guardar_datos(datos)
    return jsonify({"mensaje": "Usuario creado exitosamente"}), 201






# Endpoint para obtener el historial de un usuario por su ID
@app.route('/usuarios/<int:usuario_id>/historial', methods=['GET'])
def obtener_historial_usuario(usuario_id):
    datos = cargar_datos()
    
    # Verificar que el usuario exista
    usuario = next((usuario for usuario in datos["usuarios"] if usuario["id"] == usuario_id), None)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Filtrar el historial para obtener solo los registros del usuario
    historial_usuario = [registro for registro in datos["historial"] if registro["usuario_id"] == usuario_id]
    
    return jsonify(historial_usuario), 200






# Endpoint para verificar si una matrícula pertenece a algún usuario y registrar intentos fallidos
@app.route('/verificar_matricula', methods=['POST'])
def verificar_matricula():
    data = request.get_json()
    matricula = data.get("matricula")
    fecha = data.get("fecha", datetime.utcnow().strftime('%Y-%m-%d'))
    
    if not matricula:
        return jsonify({"error": "Matrícula es requerida"}), 400
    
    
    datos = cargar_datos()
    usuario = next((usuario for usuario in datos["usuarios"] if usuario["matricula1"] == matricula or usuario["matricula2"] == matricula), None)
    
    if usuario:
        # Agregar entrada al historial
        nuevo_historial = {
            "id": len(datos["historial"]) + 1,
            "usuario_id": usuario["id"],
            "matricula": matricula,
            "fecha": fecha,
            "permitido": True
        }
        datos["historial"].append(nuevo_historial)
        guardar_datos(datos)
        
        return jsonify({
            "pertenece": True,
            "matricula": matricula,
            "usuario": {
                "correo": usuario["correo"],
                "nombre": usuario["nombre"],
                "apellidos": usuario["apellidos"]
            }
        }), 200
    
    # Guardar intento fallido en historial
    nuevo_historial = {
        "id": len(datos["historial"]) + 1,
        "usuario_id": None,
        "matricula": matricula,
        "fecha": fecha,
        "permitido": False
    }
    datos["historial"].append(nuevo_historial)
    guardar_datos(datos)
    
    return jsonify({"matricula": matricula,"pertenece": False}), 200








# Endpoint para obtener todos los usuarios
@app.route('/usuarios', methods=['GET'])
def obtener_usuarios():
    datos = cargar_datos()
    return jsonify(datos["usuarios"]), 200





# Endpoint para obtener un usuario por su ID
@app.route('/usuarios/<int:usuario_id>', methods=['GET'])
def obtener_usuario_por_id(usuario_id):
    datos = cargar_datos()
    
    # Buscar el usuario con el ID proporcionado
    usuario = next((usuario for usuario in datos["usuarios"] if usuario["id"] == usuario_id), None)
    
    if usuario:
        return jsonify(usuario), 200

    return jsonify({"error": "Usuario no encontrado"}), 404






# Endpoint para actualizar un usuario por su ID con validación
@app.route('/usuarios/<int:usuario_id>', methods=['PUT'])
def actualizar_usuario(usuario_id):
    datos = cargar_datos()
    data = request.get_json()
    
    # Validar datos de usuario
    errors = usuario_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    
    # Buscar el usuario con el ID proporcionado
    usuario = next((usuario for usuario in datos["usuarios"] if usuario["id"] == usuario_id), None)
    
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Actualizar los datos del usuario
    usuario["correo"] = data.get("correo", usuario["correo"])
    usuario["nombre"] = data.get("nombre", usuario["nombre"])
    usuario["apellidos"] = data.get("apellidos", usuario["apellidos"])
    usuario["matricula1"] = data.get("matricula1", usuario["matricula1"])
    usuario["matricula2"] = data.get("matricula2", usuario["matricula2"])

    # Verificar que no haya otro usuario con el mismo correo
    if any(u["correo"] == usuario["correo"] and u["id"] != usuario_id for u in datos["usuarios"]):
        return jsonify({"error": "El correo ya está en uso por otro usuario"}), 400

    # Guardar los datos actualizados
    guardar_datos(datos)
    return jsonify({"mensaje": "Usuario actualizado exitosamente"}), 200

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)
