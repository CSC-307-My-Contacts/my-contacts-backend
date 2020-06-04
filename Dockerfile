FROM python:3.6

WORKDIR /app
RUN mkdir uploads
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./backend/contactsAPI.py"]

