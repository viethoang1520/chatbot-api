FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git

COPY . .
RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "main.py"]