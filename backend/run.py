from app import create_app
from dotenv import load_dotenv
import logging

load_dotenv() 
app = create_app()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=True)