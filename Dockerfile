FROM python:3.10-slim
RUN apt-get -y update
RUN apt-get install -y gcc
RUN apt-get -y install libpq-dev python-dev

ADD ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

#ENV PYTHONUNBUFFERED 1

COPY . /app
WORKDIR /app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
