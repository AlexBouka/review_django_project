FROM python:3.12
ENV PYTHONUNBUFFERED=1
WORKDIR /newtekreviews
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .