FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app


# System deps for Chrome/Selenium if later needed (kept minimal)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       curl \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip setuptools wheel \
    && pip install -r /app/requirements.txt

# Copy application
COPY . /app

# Expose port (Vercel provides $PORT at runtime)
EXPOSE 8000

# Run Streamlit on the provided PORT environment variable
CMD ["sh", "-c", "streamlit run streamlit_app.py --server.port ${PORT:-8000} --server.address 0.0.0.0"]
