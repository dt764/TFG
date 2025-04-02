# TFG David Tarca: Sistema de control de acceso al parking mediante reconocimiento de matrículas basado en redes neuronales

Este repositorio contiene el código del proyecto de TFG para el sistema del parking. Se divide en los siguientes módulos:

## Módulos del Sistema

### Frontend de Administración (admin_frontend)
- Proyecto en Angular para la gestión administrativa del parking
- Estado: En desarrollo

### Backend
- Implementado con Flask
- Instrucciones de instalación:
    1. Instalar dependencias del `requirements.txt`
    2. Configurar variables de entorno
    3. Ejecutar `run.py`

### Entrenamiento del Modelo (model-training)
- Notebook preparado para Google Colab
- Incluye instrucciones detalladas de uso
- Script completo de entrenamiento del modelo

### Módulo de Logging (logging_module)
- Basado en el módulo logging de Python
- Configuración mediante archivos YAML

### Sistema de Parking (Parking System)
Incluye los siguientes subsistemas:
- Detector
- Verificador
- Control de puerta

#### Requisitos del Sistema
- Broker AMQP (RabbitMQ) para comunicación principal
- Broker MQTT (Mosquitto) para comunicación detector-pantalla
- Runtime Edge TPU para el detector

#### Configuración
- Cada subsistema tiene su propio `main.py`
- Configuración centralizada en `base_config`:
    - URLs de brokers
    - URL del backend
    - Umbrales de confianza
    - Otros parámetros del sistema

