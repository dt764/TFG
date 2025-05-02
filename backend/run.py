from app import create_app
from dotenv import load_dotenv
import os
import logging

load_dotenv()
app = create_app()

if __name__ == '__main__':
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "yes")
    
    if debug_mode:
        logging.basicConfig(level=logging.DEBUG)
    
    app.run(host='0.0.0.0', debug=debug_mode)
