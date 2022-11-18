FROM python:3.8-slim-buster
WORKDIR /ac_app
COPY ./requirements.txt /var/www/requirements.txt
RUN pip3 install -r /var/www/requirements.txt
COPY . .
# EXPOSE 6001
CMD ["python3","-m","flask","run"]