__author__ = 'Lorenzo De Mattei'
__license__ = 'GPL'
__email__ = 'lorenzo.demattei@gmail.com'


import Graph


def main():
    graph = Graph.Graph('http://it.dbpedia.org/resource/')

    # graph.build_graph('tagme_out/', 'http://it.dbpedia.org/sparql')
    # graph.save_graph('graph.pickle')

    graph.load_graph('graph.pickle')
    # relations = graph.get_relations('Luigi_Cadorna', 'Armando_Diaz')
    # degree_distribution = graph.degree_distribution()
    print graph.components()
    print graph.average_shortest_path()
    # print graph.clustering_coefficient()
    # graph.closeness()
    graph.betweenness()
    graph.page_rank()

if __name__ == '__main__':
    main()