FROM python:3
WORKDIR /ac_app
COPY requirements.txt requirements.txt
COPY . .
RUN pip3 install -r requirements.txt
CMD ["python3", "-u","app.py"]