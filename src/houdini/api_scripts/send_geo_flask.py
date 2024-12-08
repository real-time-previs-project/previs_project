from flask import Flask, request, jsonify
import hou

app = Flask(__name__)

@app.route('/send_geometry', methods=['POST'])
def send_geometry():
    data = request.json
    frame = data["frame"]
    geometry = data["geometry"]

    # Create a Houdini node for the frame's geometry
    geo_node = hou.node("/obj").createNode("geo", f"frame_{frame}_geometry")
    geo_node.moveToGoodPosition()

    for polygon in geometry:
        vertices = polygon["vertices"]
        attributes = polygon.get("attributes", {})

        # Create geometry in Houdini
        add_node = geo_node.createNode("add")
        add_node.parm("usept0").set(True)
        
        for i, point in enumerate(vertices):
            add_node.parm(f"pt{i}").set(f"{point['x']},{point['y']},0")

        add_node.parm("useprim0").set(True)

        # Add attributes like color or area
        if "color" in attributes:
            color = attributes["color"]
            add_node.parmTuple("Cd").set((color[0] / 255, color[1] / 255, color[2] / 255))

    return jsonify({"status": "success", "message": f"Geometry for frame {frame} processed."})

if __name__ == "__main__":
    app.run(port=5000, debug=True)
