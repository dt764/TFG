import logging
import logging.config
import yaml
import pathlib

def setup_logger(config_path=None):
    """
    Configures the logging system using a YAML file.

    Args:
        config_path (str or Path, optional): Path to the configuration file. 
                                           If not provided, looks for a default one in the project root.
    """
    try:
        if config_path is None:
            # Busca el YAML en el directorio raíz del proyecto
            base_dir = pathlib.Path(__file__).parent
            config_path = base_dir / "logger_config.yaml"

        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        logging.config.dictConfig(config)

    except Exception as e:
        print(f"[Logger] Error cargando configuración desde {config_path}: {e}")
        logging.basicConfig(level=logging.INFO)
