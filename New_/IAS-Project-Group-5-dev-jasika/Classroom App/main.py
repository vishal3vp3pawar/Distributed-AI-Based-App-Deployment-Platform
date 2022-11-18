from flask import Flask, render_template
import threading

app = Flask()

def fire_detection():
    pass

def student_motion_detect():
    
    pass

def attention_detection():
    pass

app.route('/')
def home():
    return render_template("index.html")

app.route('/attendance')
def attendance():
    pass

app.route('/attention')
def attention():
    pass

app.route('/peripherals')
def peripherals():
    pass


if __name__ == "__main__":
    t1 = threading.Thread(target = fire_detection)
    t2 = threading.Thread(target = student_motion_detect)
    t3 = threading.Thread(target = attention_detection)
    
    app.run(port=5000)