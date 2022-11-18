FROM python:3
WORKDIR /control_manager
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
# EXPOSE 6000
CMD ["python", "-u", "app.py"]

