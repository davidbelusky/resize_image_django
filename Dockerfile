FROM python:3.8.2

ENV PYTHONUNBUFFERED 1

#Create folder app
RUN mkdir /app

#Set app as main workdir
WORKDIR /app

#Copy current project folder into docker image app folder
ADD . /app/

#Install all requirements
RUN pip install -r requirements.txt