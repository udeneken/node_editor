import json
import os.path
from PIL import ImageGrab

from .object import Node, Edge

def parse_canvas(app):
    nodes = app.get_objs(Node)
    edges = app.get_objs(Edge)

    export_data = {'General': {}, 'Nodes': {}, 'Edges': {}}

    node_number = {node: i for i, node in enumerate(nodes)}
    for node, i in node_number.items():
        export_data['Nodes'][i] = node.get_data()

    for i, edge in enumerate(edges):
        data = edge.get_data()
        nodeA = data['nodeA']
        nodeB = data['nodeB']
        data['nodeA'] = node_number[nodeA]
        data['nodeB'] = node_number[nodeB]
        export_data['Edges'][i] = data

    return export_data

def save_canvas(app, file_name):
    export_data = parse_canvas(app)
    json_object = json.dumps(export_data, indent=4)

    save_file(json_object, file_name)


def save_file(data, file_name):
    '''Save any text file'''
    if os.path.isfile(file_name):
        print('Overwriting file. ')

    with open(file_name, "w") as outfile:
        outfile.write(data)
    print(f'File saved in: {file_name}')

def open_file(app, file_name):
    print(f'Opening file: {file_name}')

    if not os.path.isfile(file_name):
        msg = 'file does not exist '
        app.set_status(msg)
        app.change_mode('Normal')
        print(msg)
        return

    with open(file_name, 'r') as openfile:
        import_data = json.load(openfile)

    node_data = import_data['Nodes']
    node_numbers = {}
    for i, data in node_data.items():
        new_node = Node(app.root.canvas, **data)
        app.add_node(new_node)
        node_numbers[i] = new_node

    edge_data = import_data['Edges']
    for i, data in edge_data.items():
        # print(f"nodeA: {data['nodeA']}, nodeB {data['nodeB']}")
        nodeA = node_numbers[str(data['nodeA'])]
        nodeB = node_numbers[str(data['nodeB'])]
        e = Edge(app.root.canvas, nodeA, nodeB)
        app.add_edge(e)
        # print(e.description)

    # for node in app.get_objs(Node):
    #     print(f'{node.text}: {[e.description for e in node.edges]}')

    print('Opened. ')


def import_mermaid(app, mermaid_string):
    '''Import a mermaid file and parse it'''
    mermaid_lines = [line.strip() for line in mermaid_string.split('\n')]
    if not mermaid_lines[0].startswith('flowchart'):
        print('Mermaidstyle not supported.')

    nodes = []
    edges = []
    for line in mermaid_lines[1:]:
        A, B = line.split('--')
        A = A.replace('<', '').strip()
        B = B.replace('>', '').strip()
        if A not in nodes:
            nodes.append(A)
        if B not in nodes:
            nodes.append(B)
        if [A, B] not in edges:
            edges.append([A,B])

    node_objs = {}
    for i, node_name in enumerate(nodes):
        new_node = Node(x=50, y=i*60 + 50, text=node_name)
        node_objs[node_name] = app.add_node(new_node)

    for e in edges:
        edge = Edge(node_objs[e[0]], node_objs[e[1]])
        app.add_edge(edge)
    return

def export_mermaid(app):
    edges = app.get_objs(Edge)

    mermaid_string = 'flowchart TD\n'
    for e in edges:
        mermaid_string += f'    {e.nodeA.text} --> {e.nodeB.text}\n'

    return mermaid_string


def export_svg(app, file_name):
    svg_template = ''

    edges = app.get_objs(Edge)
    for edge in edges:
        points = ' '.join([f"{p[0]}, {p[1]}"for p in edge.points])
        svg_template += f'    <polyline points="{points}" style="fill:none;stroke:black;stroke-width:1" />\n'

    nodes = app.get_objs(Node)
    for node in nodes:
        text_pos = (node.x + node.width//2, node.y + node.height // 2)
        svg_template += f'    <rect width="{node.width}" height="{node.height}" x="{node.x}" y="{node.y}" fill="white" stroke="black" stroke-width="2" />\n'
        svg_template += f'    <text x="{text_pos[0]}" y="{text_pos[1]}" fill="black" font-size="10">{node.text}</text>\n'

    svg_template =  f'<svg height="{app.root.canvas_height}" width="{app.root.canvas_width}" xmlns="http://www.w3.org/2000/svg">\n{svg_template}</svg>'

    save_file(svg_template, file_name)

def get_screenshot(app):
    root = app.root
    x = root.winfo_rootx()
    y = root.winfo_rooty()
    w = app.canvas_width
    h = app.canvas_height

    # Force geometry + drawing update
    root.update_idletasks()
    root.update()


    # disable cursor and command window
    app.cursor_visible = False
    app.set_command('')
    app.root.cmd_frame.lower()
    app.redraw()

    img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
    
    app.cursor_visible = True
    app.redraw()

    return img

def export_image(app, file_name):
    '''Save image in file path'''
    img = get_screenshot(app)
    img.save(file_name)
