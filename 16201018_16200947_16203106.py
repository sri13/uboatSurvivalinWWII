import networkx as nx
import matplotlib.pyplot as plt
from geopy.distance import vincenty

#minimum number of nodes required for communication
# 1- HQ; 1- CC and 1 - Uboat
minNumNodes = 3

minTransRange = 300
minViewRange = 50


def set_edges(graph):
    
    for eachNode in graph.nodes():
        
        for nextNode in graph.nodes():
            
            # not same node in two loops and no conncetion
            if (eachNode != nextNode) and \
             not graph.has_edge(eachNode, nextNode):
                 
                 # for HQ node
                 if (graph.node[eachNode]["type"] == "HQ"):
                    if (graph.node[nextNode]["type"] == "CC"):
                        graph.add_edge(eachNode,nextNode)
                        graph.edge[eachNode][nextNode]["weight"] = 1
                
                # for Command Center node
                 elif(graph.node[eachNode]["type"] == "CC"):
                     if (graph.node[nextNode]["type"] == "HQ") or \
                            (graph.node[nextNode]["type"] == "CC") or \
                                  ( (graph.node[nextNode]["type"] == "Uboat") \
                                     and (graph.node[nextNode]["listeningZone"] == 0) ):
                        graph.add_edge(eachNode,nextNode)
                        graph.edge[eachNode][nextNode]["weight"] = 1

                # for Uboat node
                 elif(graph.node[eachNode]["type"] == "Uboat"):
                     
                     eachNodeLoc= (graph.node[eachNode]["lat"],graph.node[eachNode]["lon"])
                     nextNodeLoc= (graph.node[nextNode]["lat"],graph.node[nextNode]["lon"])
                        
                     if(graph.node[nextNode]["type"] == "Uboat") and \
                        ( vincenty(eachNodeLoc, nextNodeLoc).kilometers <= minTransRange ):
                        graph.add_edge(eachNode,nextNode)
                        graph.edge[eachNode][nextNode]["weight"] = 1

                     elif(graph.node[nextNode]["type"] == "convoy") and \
                          (vincenty(eachNodeLoc, nextNodeLoc).kilometers <= minViewRange ):
                            graph.add_edge(eachNode,nextNode)
                            graph.edge[eachNode][nextNode]["weight"] = 1
    return graph


def set_HQ_CC(graph, HQNode, CCNode):

    # Sanity checks for input
    if(graph.number_of_nodes() < minNumNodes):
        raise ValueError("Graph doesnt contain sufficient number of nodes to continue.")

    if not graph.has_node(HQNode):
        raise ValueError("HQ Node " + str(HQNode) + " not present")

    if not graph.has_node(CCNode):
        raise ValueError("CC node " + str(CCNode) + " not present")

    #HQ setup
    graph.node[HQNode]["lat"] = 52.51
    graph.node[HQNode]["lon"] = 13.39
    graph.node[HQNode]["type"] = "HQ"

    #CC Setup
    graph.node[CCNode]["lat"]=50.74
    graph.node[CCNode]["lon"]=-3.36
    graph.node[CCNode]["type"] = "CC"

    #add edge between HQ and CC
    graph.add_edge(HQNode,CCNode)
    graph[HQNode][CCNode]["weight"] = 1
    
    return graph

def set_convoy(graph, ConvoyNode):

    # Sanity checks for input
    if not graph.has_node(ConvoyNode):
        raise ValueError("Convoy Node " + str(ConvoyNode) + " not present")

    #Convoy setup
    graph.node[ConvoyNode]["lat"] = 52.48
    graph.node[ConvoyNode]["lon"] = -59.98
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
    UboatLocations = ([52.48, -59.28], # Node -2
                      [52.00, -55.78], # Node -3
                      [54.50, -57.78], # Node -4
                      [53.68, -54.28], # Node -5
                      [53.48, -50.58], # Node -6
                      [53.00, -46.98], # Node -7
                      [52.98, -43.26], # Node -8
                      [51.50, -39.65], # Node -9
                      [52.45, -35.98], # Node -10
                      [52.43, -32.31], # Node -11
                      [51.10, -28.67], # Node -12
                      [54.18, -28.96], # Node -13
                      [52.91, -35.21], # Node -14
                      [52.50, -26.00]) # Node -15

    numOfUboats = 14

    graph = set_Uboats(graph, numOfUboats, UboatLocations)

    #set convoy node
    graph = set_convoy(graph,16)
    
    #set edges
    graph = set_edges(graph)
    
    return graph

def draw_graph(graph):
    
    pos = {}

    for eachNode in graph.nodes():
        pos[eachNode]=(graph.node[eachNode]["lon"],graph.node[eachNode]["lat"])
        
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
    
    nx.draw_networkx_nodes(graph, pos, nodelist=HQ_node, node_color="m")
    nx.draw_networkx_nodes(graph, pos, nodelist=convoy_node, node_color="r")
    nx.draw_networkx_nodes(graph, pos, nodelist=CC_nodes, node_color="c")
    nx.draw_networkx_nodes(graph, pos, nodelist=Uboat_lz_nodes, node_color="b")
    nx.draw_networkx_nodes(graph, pos, nodelist=Uboat_nlz_nodes, node_color="g")
    nx.draw_networkx_nodes(graph, pos, nodelist=empty_nodes, node_color="w")

    nx.draw_networkx_labels(graph, pos)
    
    nx.draw_networkx_edges(graph, pos)
#    nx.draw_networkx_edge_labels(graph, pos)

    plt.savefig("UboatSurvival.png") 
    plt.close()

        
if __name__ == "__main__":
    
    plt.figure(figsize=(15,15))
    
    graph  = get_graph(17)
    
    print(graph.nodes(data=True))

    print(graph.edges(data=True))

    draw_graph(graph)
    
    print("Shortest Path - " ,nx.dijkstra_path(graph,16,0))
    
    print("Shortest path Length - ",nx.dijkstra_path_length(graph,16,0))
        
    print("Single Source Shortest Path - " ,nx.dijkstra_path(graph,16,0))
    