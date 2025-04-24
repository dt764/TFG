# Sistema de Control de Acceso al Parking mediante Reconocimiento de Matrículas
## TFG de David Tarca: Implementación basada en Redes Neuronales

Sistema integral para la gestión automatizada de accesos a parkings mediante reconocimiento de matrículas. El proyecto integra las siguientes componentes principales:

## 🌐 Frontend de Administración
- **Tecnología**: Angular
- **Funcionalidad**: Panel de control para gestión del parking
- **Estado**: En desarrollo activo

## ⚙️ Backend API
- **Framework**: Flask (Python)
- **Despliegue**:
    1. `pip install -r requirements.txt`
    2. Configurar variables de entorno
    3. Ejecutar `python run.py`

## 🤖 Entrenamiento del Modelo
- Notebook optimizado para Google Colab
- Documentación detallada del proceso
- Scripts de entrenamiento y evaluación

## 📝 Sistema de Logging
- Implementación basada en Python logging
- Configuración vía YAML
- Trazabilidad completa del sistema

## 🚗 Sistema Principal del Parking
### Componentes:
- **Detector**: Reconocimiento en tiempo real
- **Verificador**: Validación de accesos
- **Control de Puerta**: Automatización de barreras

### Requisitos del Sistema
- RabbitMQ (AMQP) - Comunicación principal
- Mosquitto (MQTT) - Comunicación detector-display
- Runtime Edge TPU - Procesamiento del detector

### Configuración
Gestión centralizada en `base_config`:
- Endpoints de comunicación
- Parámetros de backend
- Configuración de umbrales
- Variables del sistema



