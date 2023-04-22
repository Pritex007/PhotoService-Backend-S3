FROM python:3

WORKDIR /usr/app/src

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./proto/ ./proto/