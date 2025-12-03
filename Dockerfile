FROM ubuntu:20.04

RUN apt-get update -y && \
    apt-get install -y python3.12 python3.12-dev python3-pip git libmysqlclient-dev curl

COPY requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

EXPOSE 80

CMD ["gunicorn", "application-docker:app", "--workers 4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:80","--timeout", "600"]
