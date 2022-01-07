FROM python:3.10.1-slim-buster
RUN apt-get -y update
RUN apt-get -y install git

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

RUN mkdir data
RUN mkdir logs

CMD [ "python3", "-m", "bot" ]