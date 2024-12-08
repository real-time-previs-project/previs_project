from flask import Flask, request, jsonify
import hou

app = Flask(__name__)

@app.route('/send_geometry', methods=['POST'])
def send_geometry():
    data = request.json
    frame = data["frame"]
    geometry = data["geometry"]

    # Create a new geometry node in Houdini
    geo_node = hou.node("/obj").createNode("geo", f"frame_{frame}_geometry")
    geo_node.moveToGoodPosition()

    for polygon in geometry:
        vertices = polygon["vertices"]

        # Create an Add SOP node
        add_node = geo_node.createNode("add")
        add_node.parm("usept0").set(True)

        for i, vertex in enumerate(vertices):
            add_node.parm(f"pt{i}").set(f"{vertex['x']},{vertex['y']},0")

        add_node.parm("useprim0").set(True)  # Connect points into a polygon

        # Add attributes
        attributes = polygon.get("attributes", {})
        if "color" in attributes:
            color = attributes["color"]
            add_node.parmTuple("Cd").set((color[0] / 255, color[1] / 255, color[2] / 255))

    return jsonify({"status": "success", "message": f"Geometry for frame {frame} processed."})

def start():
    app.run(port=5000)
