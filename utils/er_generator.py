import graphviz
import math
import re
from typing import List, Dict

def generate_er_diagram(
    tables: List[Dict],
    output_folder: str = ".",
    filename: str = "er_diagram",
    format: str = "png"
):
    dot = graphviz.Digraph(format=format, engine="neato")
    dot.attr('graph', splines="true", overlap="false", margin="0.5")
    dot.attr('node', fontname="Arial", fontsize="18", width="1.8", height="0.6")
    dot.attr('edge', fontname="Arial", fontsize="16")

    n_entities = len(tables)
    radius = 16
    attr_radius = 3.5
    entity_positions = {}

    def normalize(colname):
        return re.sub(r'[\d_.]+$', '', colname.lower())

    for idx, table in enumerate(tables):
        raw_name = table['table_name']
        angle = 2 * math.pi * idx / n_entities
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        entity_positions[raw_name] = (x, y)
        dot.node(
            raw_name,
            "Entity",
            shape='rectangle',
            color='deepskyblue',
            fillcolor='lightblue',
            style='filled,bold',
            penwidth='2',
            pos=f"{x},{y}!",
            pin="true"
        )
        raw_columns = table.get("columns", [])
        fk_columns = {fk['column'] for fk in table.get("foreign_keys", [])}
        non_fk_columns = [col for col in raw_columns if col not in fk_columns]
        collapsed = {}
        for col in non_fk_columns:
            base = normalize(col)
            if base not in collapsed:
                collapsed[base] = set()
            collapsed[base].add(col)
        for i, base_attr in enumerate(collapsed.keys()):
            a_angle = angle + (2 * math.pi * i / len(collapsed)) / 2 if len(collapsed) > 1 else angle
            ax = x + attr_radius * math.cos(a_angle)
            ay = y + attr_radius * math.sin(a_angle)
            attr_node = f"{raw_name}_{base_attr}"
            dot.node(
                attr_node,
                base_attr,
                shape='ellipse',
                color='goldenrod',
                fillcolor='lightyellow',
                style='filled,bold',
                penwidth='2',
                pos=f"{ax},{ay}!",
                pin="true"
            )
            dot.edge(raw_name, attr_node, color="gray", constraint="false")
    for table in tables:
        src = table['table_name']
        for i, fk in enumerate(table.get("foreign_keys", [])):
            tgt = fk['ref_table']
            if tgt not in entity_positions:
                continue
            x1, y1 = entity_positions[src]
            x2, y2 = entity_positions[tgt]
            mx = (x1 + x2) / 2
            my = (y1 + y2) / 2
            angle = math.atan2(y2 - y1, x2 - x1)
            mx += 1.5 * math.cos(angle + math.pi / 2)
            my += 1.5 * math.sin(angle + math.pi / 2)
            relation_name = f"FK_{src}_to_{tgt}_{i}"
            label = "Relates with"
            dot.node(
                relation_name,
                label,
                shape='diamond',
                color='orchid',
                fillcolor='mistyrose',
                style='filled,bold',
                penwidth='2',
                fontsize="18",
                pos=f"{mx},{my}!",
                pin="true"
            )
            dot.edge(src, relation_name, color='orchid', constraint="false", arrowhead="none")
            dot.edge(tgt, relation_name, color='orchid', constraint="false", arrowhead="none")
    output_path = f"{output_folder}/{filename}"
    dot.render(output_path, cleanup=True)
    return f"{output_path}.{format}"
