from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/send_geometry', methods=['POST'])
def send_geometry():
    data = request.json
    frame = data["frame"]
    geometry = data["geometry"]


    return jsonify({"status": "success", "message": f"Geometry for frame {frame} processed."})

def start():
    print('Hellp')
    app.run(port=5000)
