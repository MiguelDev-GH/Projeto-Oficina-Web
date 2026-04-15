FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema necessárias para weasyprint, nmap e Playwright
RUN apt-get update && apt-get install -y \
    nmap \
    python3-cffi \
    python3-brotli \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz-subset0 \
    libfontconfig1 \
    libffi-dev \
    libgdk-pixbuf-2.0-0 \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Instala os binários do Chromium para o Playwright (headless DAST)
# --with-deps instala automaticamente libglib, libnss, etc. necessários pelo Chromium
RUN playwright install chromium --with-deps

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
