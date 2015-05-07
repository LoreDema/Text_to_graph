__author__ = 'Lorenzo De Mattei'
__license__ = 'GPL'
__email__ = 'lorenzo.demattei@gmail.com'


import networkx as nx
import pickle
import json
import codecs
import os
import sparql


class Graph:
    def __init__(self, kb):
        self.graph = nx.MultiDiGraph()
        self.kb = kb

    def build_graph(self, data_folder, endpoint):
        entities = {}
        for tagme in os.listdir('tagme_out/'):
            if tagme.endswith('.json'):
                obj = codecs.open(data_folder + tagme, 'r', 'utf-8')
                obj = obj.read()
                obj = json.loads(json.loads(obj, encoding='utf-8'))
                for entity in obj['annotations']:
                    if float(entity['rho']) > 0.1:
                        info = (tagme[:-5], int(entity['start']), int(entity['end']))
                        try:
                            dbpedia_entity = self.kb + entity['title'].replace(' ', '_')
                        except KeyError:
                            continue
                        if dbpedia_entity not in entities:
                            entities[dbpedia_entity] = [info]
                        else:
                            entities[dbpedia_entity].append(info)

        for entity in entities:
            service = sparql.Service(endpoint)
            query = 'SELECT distinct ?property ?a WHERE {<' + entity + '> ?property ?a.}'
            result = service.query(query)
            for row in result.fetchone():
                self.graph.add_edge(entity, row[1], attr=row[0])

    def save_graph(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self.graph, f)

    def load_graph(self, path):
        with open(path, 'rb') as f:
            self.graph = pickle.load(f)

    def get_relations(self, entity1, entity2):
        links = self.graph[self.kb + entity1]
        direct_links = {}
        for entity in links:
            if unicode(entity) == (self.kb + entity2):
                direct_links[entity] = links[entity]
        return links

    def get_properties(self, entity):
        return self.graph[self.kb + entity]
