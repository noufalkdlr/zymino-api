FROM python:3.12-slim

# System dependencies for Pillow (Image processing) and PostgreSQL
RUN apt-get update && apt-get install -y \
  gcc \
  libpq-dev \
  libjpeg-dev \
  zlib1g-dev \
  && rm -rf /var/lib/apt/lists/*

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory
WORKDIR /app

# Set the working directory
COPY pyproject.toml uv.lock* ./

# Install Python libraries and Gunicorn using uv
RUN uv pip install --system . gunicorn

# Copy the project source code
COPY . .

# Collect static files for Nginx
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Start the application using Gunicorn with 3 workers
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
