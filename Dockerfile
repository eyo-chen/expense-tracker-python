FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
  curl \
  build-essential \
  && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
  mv /root/.local/bin/uv /usr/local/bin/uv

# Ensure PATH includes /usr/local/bin
ENV PATH="/usr/local/bin:$PATH"

# Copy project files
COPY . .

# Run uv sync
RUN uv sync --frozen --no-cache

# Expose port
EXPOSE 50051

# Run the application
CMD ["uv", "run", "src/index.py"]