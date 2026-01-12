FROM python:3.9-slim
WORKDIR /app
COPY ./api /app/api
COPY requirements.txt /app
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "api/app.py"]
