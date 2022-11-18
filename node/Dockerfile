FROM python:3
WORKDIR /node
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
# EXPOSE 21000
CMD ["python", "-u", "app.py"]

