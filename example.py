__author__ = 'Lorenzo De Mattei'
__license__ = 'GPL'
__email__ = 'lorenzo.demattei@gmail.com'


import Graph


def main():
    graph = Graph.Graph('http://it.dbpedia.org/resource/')

    # graph.build_graph('tagme_out/', 'http://it.dbpedia.org/sparql')
    # graph.save_graph('graph.pickle')

    graph.load_graph('graph.pickle')
    reletions = graph.get_relations('Luigi_Cadorna', 'Armando_Diaz')

if __name__ == '__main__':
    main()