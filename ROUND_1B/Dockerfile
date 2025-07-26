FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc build-essential libopenjp2-7 libjpeg-dev libfreetype6-dev && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN ln -s /lib/x86_64-linux-gnu/libcrypt.so.1 /usr/lib/libcrypt.so.2

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download and cache your model offline
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2').save('./models/embed_model')"

COPY . .

CMD ["python", "main.py"]