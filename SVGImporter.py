import xml.etree.ElementTree as ET
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

def parse_svg(svg_content):
    root = ET.fromstring(svg_content)

    # Check if the SVG has a namespace
    if '}' in root.tag:
        namespace = {'svg': root.tag.split('}')[0].strip('{')}
    else:
        namespace = {}

    nodes = set()
    edges = []
    circles = []

    # Extract all line elements
    lines = root.findall('.//svg:path', namespace)
    # print(f"Found {len(lines)} path elements")
    for line in lines:
        d = line.get('d')
        if d:
            points = d.split('L')
            for i in range(len(points) - 1):
                x1, y1 = map(float, points[i].strip('ML').split(','))
                x2, y2 = map(float, points[i + 1].strip('ML').split(','))
                nodes.add((x1, -y1))  # Flip y-coordinate
                nodes.add((x2, -y2))  # Flip y-coordinate
                edges.append(((x1, -y1), (x2, -y2)))  # Flip y-coordinates

    # Extract all circle elements
    circles_elements = root.findall('.//svg:circle', namespace)
    # print(f"Found {len(circles_elements)} circle elements")
    for circle in circles_elements:
        cx, cy = float(circle.get('cx')), float(circle.get('cy'))
        circles.append((cx, -cy))  # Flip y-coordinate

    # Prepare the data dictionary
    data_gelenke = {
        'Punkt': [],
        'x-Koordinate': [],
        'y-Koordinate': [],
        'Statisch': [],
        'Kurbel': []
    }

    # Add nodes to the data dictionary
    node_list = list(nodes)
    for i, (x, y) in enumerate(node_list):
        data_gelenke['Punkt'].append(f"{i}")
        data_gelenke['x-Koordinate'].append(x)
        data_gelenke['y-Koordinate'].append(y)
        data_gelenke['Statisch'].append(False)
        data_gelenke['Kurbel'].append(False)

    # Add circle center points to the data dictionary
    for cx, cy in circles:
        data_gelenke['Punkt'].append(f"{len(node_list)}")
        data_gelenke['x-Koordinate'].append(cx)
        data_gelenke['y-Koordinate'].append(cy)
        data_gelenke['Statisch'].append(True)
        data_gelenke['Kurbel'].append(True)

    # Create connection matrix
    connection_matrix = [[0] * (len(node_list) + 1) for _ in range(len(node_list))]
    for (x1, y1), (x2, y2) in edges:
        i = node_list.index((x1, y1))
        j = node_list.index((x2, y2))
        connection_matrix[i][j] = 1
        connection_matrix[j][i] = 1  # Assuming undirected graph
    connection_matrix = np.triu(connection_matrix, k=1).astype(bool)  # Convert 1 and 0 to True and False

    # Convert connection matrix to dict
    number_of_points = len(node_list)+1
    links = {f"{i}": [False] * number_of_points for i in range(number_of_points)}
    for i, row in enumerate(connection_matrix):
        for j, val in enumerate(row):
            links[f"{i}"][j] = bool(val)

    connection_matrix = links
    
    # print("data_gelenke:\n", data_gelenke)
    # print("data_gelenke Tyoe:", type(data_gelenke))
    # print("connection_matrix:\n", connection_matrix)
    # print("connection_matrix Type:", type(connection_matrix))
    return data_gelenke, connection_matrix


# pathSVG = "Test.svg"
# data_gelenke, connection_matrix = parse_svg(pathSVG)
# print(data_gelenke)
# print(connection_matrix)    
