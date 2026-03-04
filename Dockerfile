FROM python:3.10-slim

WORKDIR /workspace

# Install Python deps
COPY requirements.lock ./requirements.lock
RUN pip install --no-cache-dir -r requirements.lock

# Copy repo
COPY . .
RUN chmod +x tools/repro/reproduce_all_linux.sh

# Reproduce pipeline (Linux equivalent of reproduce_all.ps1)
CMD ["bash", "tools/repro/reproduce_all_linux.sh"]
