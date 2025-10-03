FROM python:3.11-slim

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

EXPOSE 8080

# Don't run as root
RUN useradd -m nonrootuser
USER nonrootuser

CMD ["python", "app.py"]
