from flask import Flask, request, jsonify
import hou


@app.route('/run_simulation', methods=['POST'])
def run_simulation():
    data = request.json
    preset = data["preset"]
    parameters = data["parameters"]
    frame_range = data["frame_range"]

    # Set up Houdini simulation node
    geo_node = hou.node("/obj").createNode("geo", "simulation")
    sim_node = geo_node.createNode(preset)

    for param, value in parameters.items():
        if sim_node.parm(param):
            sim_node.parm(param).set(value)

    # Set render range
    start, end = frame_range
    render_node = hou.node("/out").createNode("mantra", "sim_render")
    render_node.parm("f1").set(start)
    render_node.parm("f2").set(end)
    render_node.parm("vm_picture").set(f"/output/simulation/frame.$F4.png")

    # Trigger render
    render_node.render(verbose=True)

    return jsonify({"status": "success", "output_path": "/output/simulation"})
