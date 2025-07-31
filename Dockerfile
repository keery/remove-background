# Dockerfile final optimisé
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libglib2.0-0 libsm6 libxext6 libxrender-dev \
    libgomp1 libgl1-mesa-glx curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pré-charger le modèle
RUN python -c "from rembg import new_session; new_session('u2net')"

COPY . .

EXPOSE 8080
ENV PORT=8080 PYTHONUNBUFFERED=1

# Démarrage direct avec Python (sans uvicorn dans CMD)
CMD ["python", "main.py"]