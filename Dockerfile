FROM python:3.9-slim

WORKDIR /app

COPY node.py /app/
COPY config /app/config/

RUN mkdir -p /app/logs

CMD ["python", "node.py"]
