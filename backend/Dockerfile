FROM python:3.9-slim

WORKDIR /app

# Instala netcat (nc) y cualquier otra utilidad del sistema
RUN apt-get update && apt-get install -y netcat-openbsd

COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
