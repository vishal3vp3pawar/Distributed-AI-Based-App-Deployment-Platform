FROM python:3
WORKDIR /sensor_manager
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
# EXPOSE 5000
CMD ["python3", "-u", "app.py"]

