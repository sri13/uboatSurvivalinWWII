import networkx as nx
import matplotlib.pyplot as plt


#minimum number of nodes required for communication
# 1- HQ; 1- CC and 1 - Uboat
minNumNodes = 3

# from geopy.distance import vincenty
# newport_ri = (41.49008, -71.312796)
# cleveland_oh = (41.499498, -81.695391)
# print(vincenty(newport_ri, cleveland_oh).kilometers)

def set_HQ_CC(graph, HQNode, CCNode):

    # Sanity checks for input
    if(graph.number_of_nodes() < minNumNodes):
        raise ValueError("Graph doesnt contain sufficient number of nodes to continue.")

    if not graph.has_node(HQNode):
        raise ValueError("HQ Node " + str(HQNode) + " not present")

    if not graph.has_node(CCNode):
        raise ValueError("CC node " + str(CCNode) + " not present")

    #HQ setup
    graph.node[HQNode]["lat"] = 52.518912
    graph.node[HQNode]["lon"] = 13.398652
    graph.node[HQNode]["type"] = "HQ"

    #CC Setup
    graph.node[CCNode]["lat"]=47.748208
    graph.node[CCNode]["lon"]=-3.369157
    graph.node[CCNode]["type"] = "CC"

    #add edge between HQ and CC
    graph.add_edge(HQNode,CCNode)
    graph[HQNode][CCNode] = 1
    
    return graph

def set_convoy(graph, ConvoyNode):

    # Sanity checks for input
    if not graph.has_node(ConvoyNode):
        raise ValueError("Convoy Node " + str(ConvoyNode) + " not present")

    #Convoy setup
    graph.node[ConvoyNode]["lat"] = 52.486730
    graph.node[ConvoyNode]["lon"] = -45.983332
    graph.node[ConvoyNode]["type"] = "convoy"

    return graph
    
    
def set_Uboats(graph, numOfUboats, UboatLocations=()):

    # Sanity checks for input
    if(graph.number_of_nodes() < numOfUboats):
        raise ValueError("Graph doesnt contain sufficient number of Uboat nodes to continue.")

    # check enough location points sent for Uboats
    if (len(UboatLocations) != numOfUboats):
        raise ValueError("Enough Locations not provided for Uboats.")

    #Uboat setup
    UboatCount = 0

    for eachNode in graph.nodes():
        if(graph.node[eachNode]["type"] == ""):
            graph.node[eachNode]["lat"] = UboatLocations[UboatCount][0]
            graph.node[eachNode]["lon"] = UboatLocations[UboatCount][1]
            graph.node[eachNode]["type"] = "Uboat"
            graph.node[eachNode]["listeningZone"] = 1
            UboatCount = UboatCount+1

        if(UboatCount == numOfUboats):
            graph.node[eachNode]["listeningZone"] = 0
            break

    return graph

def initalize(graph):

    for eachNode in graph.nodes():
        graph.node[eachNode]["lat"] = 0.0
        graph.node[eachNode]["lon"] = 0.0
        graph.node[eachNode]["type"] = ""
        graph.node[eachNode]["state"] = "standBy"
        graph.node[eachNode]["listeningZone"] = 0

    return graph

def get_graph(numOfNodes=10):
    graph = nx.Graph()

    # Generate a graph and intialize node attributes
    graph.add_nodes_from(range(numOfNodes))
    graph = initalize(graph)

    #Set Nodes as HQ, CC locations
    graph = set_HQ_CC(graph,0,1)

    #set Nodes as Uboats
    UboatLocations = ([52.526676, -45.983332],
                      [51.026676, -44.983332],
                      [54.026676, -44.983332],
                      [52.7, -43.98564],
                      [54.0, -42.0],
                      [52.7, -40.98564],
                      [50.0, -42.0])

    numOfUboats = 7

    graph = set_Uboats(graph, numOfUboats, UboatLocations)

    #set convoy node
    graph = set_convoy(graph,9)
    
    return graph

def draw_graph(graph):

    pos = nx.layout.random_layout(graph)

    # get three subsets of nodes: susceptible, infected, removed
    HQ_node = [n for n in graph.nodes() if graph.node[n]["type"] == "HQ"]
    convoy_node = [n for n in graph.nodes() if graph.node[n]["type"] == "convoy"]
    CC_nodes = [n for n in graph.nodes() if graph.node[n]["type"] == "CC"]
    Uboat_lz_nodes = [n for n in graph.nodes() if ( graph.node[n]["type"] == "Uboat" and \
                     graph.node[n]["listeningZone"] == 1 ) ]
    Uboat_nlz_nodes = [n for n in graph.nodes() if ( graph.node[n]["type"] == "Uboat" and \
                     graph.node[n]["listeningZone"] == 0 ) ]
    empty_nodes = [n for n in graph.nodes() if graph.node[n]["type"] == ""]
    

    # draw edges, then draw each subset in different colour
    nx.draw_networkx_edges(graph, pos)
    nx.draw_networkx_nodes(graph, pos, nodelist=HQ_node, node_color="m")
    nx.draw_networkx_nodes(graph, pos, nodelist=convoy_node, node_color="r")
    nx.draw_networkx_nodes(graph, pos, nodelist=CC_nodes, node_color="c")
    nx.draw_networkx_nodes(graph, pos, nodelist=Uboat_lz_nodes, node_color="b")
    nx.draw_networkx_nodes(graph, pos, nodelist=Uboat_nlz_nodes, node_color="g")
    nx.draw_networkx_nodes(graph, pos, nodelist=empty_nodes, node_color="w")
    plt.savefig("UboatSurvival.png") # pad filename with zeros
    plt.close()


        
if __name__ == "__main__":
    graph  = get_graph(10)

    print(graph.nodes(data=True))

    print(graph.edges())

    draw_graph(graph)
    