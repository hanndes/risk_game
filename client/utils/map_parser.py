import re
from PyQt6.QtGui import QPainterPath

def svg_d_to_qpath(d_string):
    path = QPainterPath()
    tokens = re.findall(r'([MmLlCcSsZz])|(-?\d*\.?\d+)', d_string)

    current_cmd = None
    points = []

    for cmd, val in tokens:
        if cmd:
            current_cmd = cmd
            points = []
            if cmd in ('Z', 'z'):
                path.closeSubpath()
            continue

        points.append(float(val))

        if current_cmd in ('M', 'm') and len(points) == 2:
            path.moveTo(points[0], points[1])
        elif current_cmd in ('L', 'l') and len(points) == 2:
            path.lineTo(points[0], points[1])
        elif current_cmd in ('C', 'c') and len(points) == 6:
            path.cubicTo(points[0], points[1], points[2], points[3], points[4], points[5])
            points = []

    return path