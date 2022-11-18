import sys
from flask import Flask, request

app = Flask(__name__)

@app.route("/fanAction", methods=["POST", "GET"])
def performAction():
    data = request.json
    if data['data'] == 0:
        return "Turn Off Fan"
    else:
        return "Turn On Fan"


if __name__ == "__main__":
    port = sys.argv[1]
    app.run(port=port, debug=True)