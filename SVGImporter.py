import xml.etree.ElementTree as ET
import networkx as nx
import numpy as np
import svgpathtools
import tempfile
import matplotlib.pyplot as plt

def parse_svg(svg_content):
    """
    Parses SVG content to extract nodes, edges, and circles, and constructs data structures for further processing.
    Args:
        svg_content (str): A string containing the SVG content.
    Returns:
        tuple: A tuple containing:
            - data_gelenke (dict): A dictionary with keys 'Punkt', 'x-Koordinate', 'y-Koordinate', 'Statisch', 'Kurbel', and 'Bahnkurve'.
              Each key maps to a list of corresponding values extracted from the SVG.
            - connection_matrix (dict): A dictionary representing the connection matrix. The keys are string representations of node indices,
              and the values are lists of boolean values indicating connections between nodes.
    """

    with tempfile.NamedTemporaryFile(delete=False, suffix=".svg") as temp_svg_file:
        temp_svg_file.write(svg_content.encode('utf-8'))
        temp_svg_file_path = temp_svg_file.name

    paths, attributes, svg_attributes = svgpathtools.svg2paths2(temp_svg_file_path, return_svg_attributes=True)

    nodes = set()
    edges = []
    circles = []
    tolerance = 1e-6  # Tolerance to filter out zero-length lines

    for path in paths:
        for segment in path:
            if isinstance(segment, svgpathtools.Line):
                start = segment.start
                end = segment.end

                # Skip zero-length lines
                if abs(start - end) < tolerance:
                    continue

                nodes.add((start.real, -start.imag))  # Flip y-coordinate
                nodes.add((end.real, -end.imag))  # Flip y-coordinate
                edges.append(((start.real, -start.imag), (end.real, -end.imag)))  # Flip y-coordinate

    for attribute in attributes:
        if 'cx' in attribute and 'cy' in attribute:
            cx = float(attribute['cx'])
            cy = float(attribute['cy'])
            circles.append((cx, -cy))  # Flip y-coordinate

    print("Nodes:", nodes)
    print("Edges:", edges)
    print("Circles:", circles)

    data_gelenke = {
        'Punkt': [],
        'x-Koordinate': [],
        'y-Koordinate': [],
        'Statisch': [],
        'Kurbel': [],
        'Bahnkurve': []
    }

    node_list = list(nodes)
    for i, (x, y) in enumerate(node_list):
        data_gelenke['Punkt'].append(f"{i}")
        data_gelenke['x-Koordinate'].append(x)
        data_gelenke['y-Koordinate'].append(y)
        data_gelenke['Statisch'].append(False)
        data_gelenke['Kurbel'].append(False)
        data_gelenke['Bahnkurve'].append(False)

    for cx, cy in circles:
        data_gelenke['Punkt'].append(f"{len(node_list)}")
        data_gelenke['x-Koordinate'].append(cx)
        data_gelenke['y-Koordinate'].append(cy)
        data_gelenke['Statisch'].append(True)
        data_gelenke['Kurbel'].append(True)
        data_gelenke['Bahnkurve'].append(False)

    connection_matrix = [[0] * (len(node_list) + 1) for _ in range(len(node_list))]
    for (x1, y1), (x2, y2) in edges:
        i = node_list.index((x1, y1))
        j = node_list.index((x2, y2))
        connection_matrix[i][j] = 1
        connection_matrix[j][i] = 1  
    connection_matrix = np.triu(connection_matrix, k=1).astype(bool)  

    number_of_points = len(node_list) + 1
    links = {f"{i}": [False] * number_of_points for i in range(number_of_points)}
    for i, row in enumerate(connection_matrix):
        for j, val in enumerate(row):
            links[f"{i}"][j] = bool(val)

    connection_matrix = links
    
    return data_gelenke, connection_matrix