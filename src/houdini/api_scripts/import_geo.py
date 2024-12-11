import hou
import json
import sys

def import_video_geometry_to_lop(json_file, node_name="video_geometry", output_hip_file="output_scene_lop.hip"):
    """
    Import video geometry from a JSON file, create a LOP node in Solaris,
    and save the scene as a .hip file.
    """
    with open(json_file, "r") as file:
        data = json.load(file)

    # Validate /obj context
    obj_context = hou.node("/obj")
    if obj_context is None:
        raise RuntimeError("The /obj context does not exist in Houdini.")

    # Create geometry node
    print(f"Creating geometry node: {node_name}")
    geo_node = obj_context.createNode("geo", node_name)
    if geo_node is None:
        raise RuntimeError(f"Failed to create geometry node '{node_name}' in /obj context.")
    geo_node.moveToGoodPosition()

    # Create an "add" node
    print("Creating 'add' SOP node...")
    add_sop = geo_node.createNode("add")
    if add_sop is None:
        raise RuntimeError("Failed to create the 'add' SOP node.")
    add_sop.setName("add_geometry")

    # Debugging: Print available parameters
    print("Available parameters on add_sop:", [parm.name() for parm in add_sop.parms()])

    # Add points using the 'points' parameter
    points_strings = []
    for i, frame_data in enumerate(data):
        vertices = frame_data["vertices"]

        # Format points as strings for the 'points' parameter
        for vertex in vertices:
            points_strings.append(f"{vertex['x']} {vertex['y']} 0")

        # Connect points into a polygon
        add_sop.parm("prims").set(1)  # Number of primitives
        add_sop.parm("closed0").set(1)  # Close the polygon

    # Set points parameter
    add_sop.parm("points").set(" ".join(points_strings))

    # Set up display and render flags
    print("Setting up display and render flags...")
    add_sop.setDisplayFlag(True)
    add_sop.setRenderFlag(True)
    add_sop.moveToGoodPosition()

    # Create a LOP node in the /stage context
    print("Creating SOP Import node in /stage context...")
    stage_context = hou.node("/stage")
    if not stage_context:
        stage_context = hou.node("/").createNode("lopnet", "stage")
    if stage_context is None:
        raise RuntimeError("Failed to create or find the /stage context in Houdini.")

    sop_import_lop = stage_context.createNode("sopimport", node_name + "_lop")
    if sop_import_lop is None:
        raise RuntimeError("Failed to create SOP Import node in the /stage context.")
    sop_import_lop.parm("soppath").set(geo_node.path())  # Link to the SOP geometry
    sop_import_lop.moveToGoodPosition()

    # Set up display and render flags for the LOP node
    sop_import_lop.setDisplayFlag(True)
    sop_import_lop.setRenderFlag(True)

    # Save the scene to a .hip file
    print(f"Saving scene to {output_hip_file}...")
    hou.hipFile.save(output_hip_file)
    print(f"Geometry imported to LOP node: {sop_import_lop.path()}")
    print(f"Scene saved to: {output_hip_file}")
    
if __name__ == "__main__":
    # Expect the JSON file path and output .hip file path as command-line arguments
   # if len(sys.argv) != 3:
      #  print("Usage: hython script.py <path_to_json> <output_hip_file>")
      #  sys.exit(1)

    json_file = sys.argv[1]
    #output_hip_file = sys.argv[2]
    import_video_geometry_to_lop(json_file)
