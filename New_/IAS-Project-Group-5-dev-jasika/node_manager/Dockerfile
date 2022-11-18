FROM python:3
WORKDIR /node_manager
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
# EXPOSE 20000
CMD ["python", "-u", "app.py"]

