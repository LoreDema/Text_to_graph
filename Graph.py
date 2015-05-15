__author__ = 'Lorenzo De Mattei'
__license__ = 'GPL'
__email__ = 'lorenzo.demattei@gmail.com'


import networkx as nx
import pickle
import json
import codecs
import os
import sparql
import matplotlib.pyplot as plt
import operator


class Graph:
    def __init__(self, kb):
        self.graph = nx.MultiDiGraph()
        self.kb = kb

    def build_graph(self, data_folder, endpoint, treshold=0.1):
        entities = {}
        for tagme in os.listdir(data_folder):
            if tagme.endswith('.json'):
                obj = codecs.open(data_folder + tagme, 'r', 'utf-8')
                obj = obj.read()
                obj = json.loads(json.loads(obj, encoding='utf-8'))
                for entity in obj['annotations']:
                    if float(entity['rho']) > treshold:
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

    def degree_distribution(self, plot=True, folder='./', color='b'):
        distribution = nx.degree_histogram(self.graph)
        for i, value in enumerate(distribution):
            distribution[i] = (float(value)/float(len(self.graph.nodes())))

        if plot:
                plt.loglog(distribution[1:], color=color)
                plt.ylabel('frequency')
                plt.xlabel('degree')
                plt.savefig(folder + 'degree_distribution.png', format='png')
                plt.close()

        return distribution[1:]

    def components(self):
        # FIXME: networkx.exception.NetworkXNotImplemented: not implemented for directed type
        return len(nx.strongly_connected_component_subgraphs(self.graph))
        # return len(self.graph.edges())

    def average_shortest_path(self):
        # FIXME: networkx.exception.NetworkXNotImplemented: not implemented for directed type
        paths = []
        try:
            paths.append(nx.average_shortest_path_length(self.graph))
        except nx.networkx.exception.NetworkXError:
            for i, g in enumerate(nx.strongly_connected_component_subgraphs(self.graph)):
                paths.append(nx.average_shortest_path_length(g))

    def clustering_coefficient(self):
        # FIXME: networkx.exception.NetworkXError: ('Clustering algorithms are not defined ', 'for directed graphs.')
        return nx.average_clustering(self.graph)

    def closeness(self,  plot=True, folder='./', color='b'):
        net_clc = nx.closeness_centrality(self.graph)

        net_clc = sorted(net_clc.items(), key=operator.itemgetter(1))
        if plot:
            plt.plot([i[1] for i in net_clc], color=color)
            plt.ylabel('centrality')
            plt.xlabel('rank')
            plt.savefig(folder + 'closeness_centrality.png', format='png')
            plt.close()

        return net_clc

    def betweenness(self,  plot=True, folder='./', color='b'):
        net_clc = nx.betweenness_centrality(self.graph)

        net_clc = sorted(net_clc.items(), key=operator.itemgetter(1))
        if plot:
            plt.plot([i[1] for i in net_clc], color=color)
            plt.ylabel('centrality')
            plt.xlabel('rank')
            plt.savefig(folder + 'closeness_centrality.png', format='png')
            plt.close()

        return net_clc

    def page_rank(self,  plot=True, folder='./', color='b'):
        # FIXME: networkx.exception.NetworkXNotImplemented: not implemented for directed type
        net_pr = {}
        for g in nx.strongly_connected_component_subgraphs(self.graph):
            sub_pr = nx.pagerank(g)
            net_pr.update(sub_pr)

        net_pr = sorted(net_pr.items(), key=operator.itemgetter(1))

        if plot:
            plt.plot([i[1] for i in net_pr], color=color)
            plt.legend()
            plt.ylabel('centrality')
            plt.xlabel('rank')
            plt.savefig('net_analysis/page_rank.png', format='png')
            plt.close()

        return net_pr