#!/usr/bin/env python3

import sys
import subprocess
import base64
import xml.etree.ElementTree as ET
import os.path
import re
from time import gmtime
from datetime import datetime

JAVABIN = "java"
PLANTUMLJAR = "plantuml-1.2024.4.jar"
DEBUG = False

DIO_AGENT_NAME    = "5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36"
DIO_ETAG_ID       = "ETAG111111111111xx01"
DIO_DIAGRAM_ID    = "DIAGRAM111111111xx01"
DIO_USEROBJECT_ID = "USEROBJECT111111xx01-1"

def dprint(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <PlantUML-file>")
        sys.exit(1)

    plantuml_file = sys.argv[1]

    if not os.path.isfile(plantuml_file):
        print("Error: PlantUML file not found.")
        sys.exit(1)

    if not os.path.isfile(PLANTUMLJAR):
        print("Error: PlantUML JAR file not found.")
        sys.exit(1)

    #
    # Convert PlantUML plain text data to SVG data
    #
    # Read in PlantUML
    with open(plantuml_file, 'r') as f:
        plantuml_textdata = f.read().strip()

    dprint("PlantUML_Text=[{}]\n".format(plantuml_textdata))

    # Convert PlantUML to SVG using PlanUML Java Library
    cmd = [JAVABIN, "-jar", PLANTUMLJAR, "-tsvg", "-pipe"]
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               universal_newlines=True)

    try:
        stdout, _ = process.communicate(input=plantuml_textdata, timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        print("Error: PlantUML process timed out.")
        sys.exit(1)

    plantuml_svgdata = stdout
    dprint("PlantUML_SVG=[{}]\n".format(plantuml_svgdata))

    #
    # base64 encode the PlantUML SVG data
    #
    plantuml_svgb64data = base64.b64encode(plantuml_svgdata.encode()).decode()
    dprint("PlantUML_Base64=[{}]\n".format(plantuml_svgb64data))

    #
    # XML/HTML/URL encode the PlantUML text data
    # Only 5 characters are needed to be escaped for XML, and include newlines and tabs
    #
    plantuml_escapedtextdata = (
        plantuml_textdata
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
        .replace('"', '&quot;')
        .replace("'", '&apos;')
        .replace('\r\n', '\\n')
        .replace('\n', '\\n')
        .replace('\r', '\\n')
        .replace('\t', '\\t')
    )
    dprint("PlantUML_EscapedText=[{}]\n".format(plantuml_escapedtextdata))

    #
    # Obtain the SVG dimensions
    #
    svg_width = ''
    svg_height = ''
    svg_dimensions_match = re.match(r'.*width:([\d]+)px;height:([\d]+)px;.*', plantuml_svgdata)
    if svg_dimensions_match:
        svg_width = svg_dimensions_match.group(1)
        svg_height = svg_dimensions_match.group(2)

    dprint("[width={},height={}]\n".format(svg_width, svg_height))

    #
    # Set the Draw.io revision date to the last modified date of the PlantUML file
    #
    file_mtime = os.path.getmtime(plantuml_file)
    file_gmtime = gmtime(file_mtime)
    gmt_timestamp = datetime.fromtimestamp(file_mtime).strftime('%Y-%m-%dT%H:%M:%S.000Z')

    dprint("[gmtime={}]\n".format(gmt_timestamp))

    #
    # Create the Draw.io file with imported PlantUML code and SVG
    # XML Data Template pulled from a random source file
    #
    # <mxfile ...>
    xml_root = ET.Element('mxfile', {
        'host': 'app.diagrams.net',
        'modified': gmt_timestamp,
        'agent': DIO_AGENT_NAME,
        'etag': DIO_ETAG_ID,
        'version': '20.0.1',
        'type': 'embed'
    })

    # <diagram ...>
    diagram_elem = ET.SubElement(xml_root, 'diagram', {'id': DIO_DIAGRAM_ID, 'name': 'Page-1'})

    # <mxGraphModel ...>
    mxGraphModel_elem = ET.SubElement(diagram_elem, 'mxGraphModel', {
        'dx': '1219', 'dy': '1005', 'grid': '1', 'gridSize': '10',
        'guides': '1', 'tooltips': '1', 'connect': '1', 'arrows': '1',
        'fold': '1', 'page': '1', 'pageScale': '1', 'pageWidth': '850',
        'pageHeight': '1100', 'math': '0', 'shadow': '0'
    })

    # <root ...>
    root_elem = ET.SubElement(mxGraphModel_elem, 'root')

    # <mxCell ...>
    mxCell_0_elem = ET.SubElement(root_elem, 'mxCell', { 'id': '0' })

    # <mxCell ...>
    mxCell_1_elem = ET.SubElement(root_elem, 'mxCell', { 'id': '1', 'parent': '0' })

    # <UserObject ...>
    userObject_elem = ET.SubElement(root_elem, 'UserObject', {
        'label': '',
        'plantUmlData': '{{\n  "data": "{}",\n  "format": "svg"\n}}'.format(plantuml_escapedtextdata),
        'id': DIO_USEROBJECT_ID
    })

    # Embed SVG image data
    svg_image_data = 'data:image/svg+xml,{}'.format(plantuml_svgb64data)
    # <mxCell ...>
    mxCell_elem = ET.SubElement(userObject_elem, 'mxCell', {
        'style': 'shape=image;noLabel=1;verticalAlign=top;aspect=fixed;imageAspect=0;image={}'.format(svg_image_data),
        'parent': '1',
        'vertex': '1'
    })

    # <mxGeometry ... />
    mxGeometry_elem = ET.SubElement(mxCell_elem, 'mxGeometry', {
        'x': '0', 'y': '0', 'width': svg_width, 'height': svg_height, 'as': 'geometry'
    })

    #
    # Print the Draw.io file to STDOUT
    #
    xml_str = ET.tostring(xml_root, encoding='unicode')
    print(xml_str)

if __name__ == "__main__":
    main()
