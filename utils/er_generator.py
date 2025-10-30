import graphviz
import math
from typing import List, Dict

def generate_er_diagram(
    tables: List[Dict],
    output_folder: str = ".",
    filename: str = "er_diagram",
    format: str = "png"
):
    dot = graphviz.Digraph(format=format, engine="neato")

    dot.attr('graph', splines="true", overlap="false", margin="0.3")
    dot.attr('node', fontname="Arial", fontsize="14", width="1.2", height="0.45")
    dot.attr('edge', fontname="Arial", fontsize="12")

    n_entities = len(tables)
    radius = 10
    attr_radius = 2.6
    entity_positions = {}

    # 1. Entities in a circle
    for idx, table in enumerate(tables):
        name = table['table_name']
        angle = 2 * math.pi * idx / n_entities
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        entity_positions[name] = (x, y)

        dot.node(
            name,
            f"<<B>{name}</B>>",
            shape='rectangle',
            color='deepskyblue',
            fillcolor='lightblue',
            style='filled,bold',
            penwidth='2',
            pos=f"{x},{y}!",
            pin="true"
        )

        # Attributes
        columns = table.get("columns", [])
        for i, col in enumerate(columns):
            a_angle = angle + (2 * math.pi * i / len(columns)) / 2 if len(columns) > 1 else angle
            ax = x + attr_radius * math.cos(a_angle)
            ay = y + attr_radius * math.sin(a_angle)
            attr_node = f"{name}_{col}"

            dot.node(
                attr_node,
                col,
                shape='ellipse',
                color='goldenrod',
                fillcolor='lightyellow',
                style='filled,bold',
                penwidth='2',
                pos=f"{ax},{ay}!",
                pin="true"
            )
            dot.edge(name, attr_node, color="gray", constraint="false")

    # 2. Foreign key relationships (diamonds with position!)
    for table in tables:
        src = table['table_name']
        for i, fk in enumerate(table.get("foreign_keys", [])):
            tgt = fk['ref_table']
            if tgt not in entity_positions:
                continue

            # Coordinates
            x1, y1 = entity_positions[src]
            x2, y2 = entity_positions[tgt]

            # Midpoint with offset
            mx = (x1 + x2) / 2
            my = (y1 + y2) / 2
            angle = math.atan2(y2 - y1, x2 - x1)
            mx += 1.2 * math.cos(angle + math.pi / 2)
            my += 1.2 * math.sin(angle + math.pi / 2)

            relation_name = f"FK_{src}_to_{tgt}_{i}"
            label = f"{fk['column']} → {fk['ref_table']}.{fk['ref_column']}"
            if len(label) > 30:
                label = f"{fk['column']} → {fk['ref_table']}"

            dot.node(
                relation_name,
                label,
                shape='diamond',
                color='orchid',
                fillcolor='mistyrose',
                style='filled,bold',
                penwidth='2',
                fontsize="14",
                pos=f"{mx},{my}!",
                pin="true"
            )
            dot.edge(src, relation_name, color='orchid', constraint="false")
            dot.edge(tgt, relation_name, color='orchid', constraint="false")

    # Output
    output_path = f"{output_folder}/{filename}"
    dot.render(output_path, cleanup=True)
    return f"{output_path}.{format}"
