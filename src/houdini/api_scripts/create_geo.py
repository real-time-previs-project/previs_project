import json
import hou

def create_geometry_in_houdini(geometry_data):
    frame = geometry_data["frame"]
    geometry = geometry_data["geometry"]

    # Create a new geometry node
    geo_node = hou.node("/obj").createNode("geo", f"frame_{frame}_geometry")
    geo_node.moveToGoodPosition()

    for polygon in geometry:
        vertices = polygon["vertices"]

        # Create an Add SOP node
        add_node = geo_node.createNode("add")
        add_node.parm("usept0").set(True)

        for i, vertex in enumerate(vertices):
            add_node.parm(f"pt{i}").set(f"{vertex['x']},{vertex['y']},0")

        add_node.parm("useprim0").set(True)

        # Add attributes
        attributes = polygon.get("attributes", {})
        if "color" in attributes:
            color = attributes["color"]
            add_node.parmTuple("Cd").set((color[0] / 255, color[1] / 255, color[2] / 255))

    print(f"Geometry for frame {frame} created.")

# Example usage
with open("geometry_data.json", "r") as f:
    geometry_data = json.load(f)

create_geometry_in_houdini(geometry_data)
