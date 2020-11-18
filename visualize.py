import glob
import xml.etree.ElementTree as ElTree
import networkx as nx
import matplotlib.pyplot as plt
import os

FROM = 'fromID'
TO = 'toID'

for name in ['Highlights_of_the_Prado_Museum', 'Bicycles']:
    files = list(glob.iglob('data/**/{}.xml'.format(name), recursive=True))
    if len(files) > 0:
        tree = ElTree.parse(files[0])

        spatial_entities = {}
        meta_links = []
        links = []

        entities = tree.find('TAGS')
        for e in entities:
            if e.tag in ['SPATIAL_ENTITY', 'PLACE']:
                spatial_entities[e.get('id')] = e.get('text')
            elif e.tag == 'METALINK':
                meta_links.append(e)

        for e in entities:
            if e.tag in ['QSLINK', 'OLINK']:
                from_id, to_id = e.get(FROM), e.get(TO)
                if from_id in spatial_entities and to_id in spatial_entities:
                    color = '#56cc5e' if e.tag == 'QSLINK' else '#e03f3f'
                    rel_type = e.get('relType')
                    links.append((from_id, to_id, rel_type, color))

        for meta_link in meta_links:
            from_id, to_id = meta_link.get(FROM), meta_link.get(TO)
            if from_id in spatial_entities and to_id in spatial_entities:
                replace_id = from_id
                new_id = to_id
                if spatial_entities[new_id] == '':
                    replace_id, new_id = new_id, replace_id
                spatial_entities.pop(replace_id)
                links = [(new_id if f == replace_id else f, new_id if t == replace_id else t, r, c) for (f, t, r, c) in
                         links]

        G = nx.Graph()

        G.add_nodes_from(spatial_entities.keys())
        for (f, t, r, c) in links:
            G.add_edge(f, t)

        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G, k=0.4, iterations=20)
        pos = nx.fruchterman_reingold_layout(G, k=0.2, iterations=20)
        nx.draw_networkx_nodes(G, pos,
                               node_color=['#0377fc' if str.startswith(e, 'se') else '#fcb103' for e in G.nodes])
        nx.draw_networkx_labels(G, pos, labels=spatial_entities, font_size=8)
        nx.draw_networkx_edges(G, pos, edge_color=[c for (f, t, r, c) in links])
        nx.draw_networkx_edge_labels(G, pos, edge_labels={(f, t): r for (f, t, r, c) in links}, font_size=8)

        plt.savefig(os.path.join('output', '{}.jpg'.format(name)))



