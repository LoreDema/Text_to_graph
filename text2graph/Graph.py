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
import numpy as np


class Graph:
    def __init__(self, kb):
        self.graph = nx.MultiDiGraph()
        self.kb = kb

    def build_graph(self, data_folder, endpoint, treshold=0.1,  rel_type=1):
        entities = {}
        for tagme in os.listdir(data_folder):
            if tagme.endswith('.json'):
                obj = codecs.open(os.path.join(data_folder, tagme), 'r', 'utf-8')
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
            try:
                result = service.query(query)
            except sparql.SparqlException:
                print 'Sparql exception for', entity
                continue
            if rel_type == 1:
                for row in result.fetchone():
                    self.graph.add_edge(entity, unicode(row[1]), attr=unicode(row[0]))
            elif rel_type == 2:
                for row in result.fetchone():
                    if unicode(row[1]) in entities:
                        print 'cool'
                        self.graph.add_edge(entity, unicode(row[1]), attr=unicode(row[0]))

    def save_graph(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self.graph, f)

    def load_graph(self, path):
        with open(path, 'rb') as f:
            self.graph = pickle.load(f)

    def get_relations(self, entity1, entity2):
        links = self.graph[self.kb + entity1]
        return links[self.kb + entity2]

    def get_properties(self, entity):
        return self.graph[self.kb + entity]

    def degree_distribution(self, plot=True, folder='./', color='b'):
        distribution = nx.degree_histogram(self.graph)
        for i, value in enumerate(distribution):
            distribution[i] = (float(value)/float(len(self.graph.nodes())))
        if plot:
            values, base = np.histogram(distribution[1:], bins=50)
            # evaluate the cumulative
            cumulative = np.cumsum(values)
            print max(distribution[1:])
            print min(distribution[1:])
            print values
            print base
            # plot the cumulative function
            plt.plot(base[:-1], cumulative, color=color)
            plt.ylabel('frequency')
            plt.xlabel('degree')
            plt.savefig(folder + 'degree_distribution.png', format='png')
            plt.close()

        return distribution[1:]

    def components(self):
        undirected = self.graph.to_undirected()
        undirected = nx.MultiGraph(undirected)
        return nx.number_connected_components(undirected)

    def average_shortest_path(self):
        undirected = self.graph.to_undirected()
        paths = []
        try:
            paths.append(nx.average_shortest_path_length(self.graph))
        except nx.networkx.exception.NetworkXError:
            for i, g in enumerate(nx.connected_component_subgraphs(undirected)):
                if len(g.nodes()) != 1:
                    paths.append(nx.average_shortest_path_length(g))
        return paths

    def clustering_coefficient(self):
        undirected = self.graph.to_undirected()
        undirected = nx.Graph(undirected)
        return nx.average_clustering(undirected)

    def closeness(self,  plot=True, folder='./', color='b'):
        net_clc = nx.closeness_centrality(self.graph)

        net_clc = sorted(net_clc.items(), key=operator.itemgetter(1))
        if plot:
            plt.plot([i[1] for i in net_clc], color=color)
            plt.ylabel('centrality')
            plt.xlabel('rank')
            plt.savefig(folder + 'closeness_centrality.png', format='png', reverse=True)
            plt.close()

        return net_clc

    def betweenness(self,  plot=True, folder='./', color='b'):
        net_clc = nx.betweenness_centrality(self.graph)

        net_clc = sorted(net_clc.items(), key=operator.itemgetter(1), reverse=True)
        if plot:
            plt.plot([i[1] for i in net_clc], color=color)
            plt.ylabel('centrality')
            plt.xlabel('rank')
            plt.savefig(folder + 'betweenness_centrality.png', format='png')
            plt.close()

        return net_clc

    def page_rank(self,  plot=True, folder='./', color='b'):
        dir_graph = nx.DiGraph(self.graph)

        net_pr = nx.pagerank(dir_graph)

        net_pr = sorted(net_pr.items(), key=operator.itemgetter(1), reverse=True)

        if plot:
            plt.loglog([i[1] for i in net_pr], color=color)
            plt.ylabel('centrality')
            plt.xlabel('rank')
            plt.savefig(folder + 'page_rank.png', format='png')
            plt.close()

        return net_pr