import networkx as nx
import matplotlib.pyplot as plt
from geopy.distance import vincenty
import random

#minimum number of nodes required for communication
# 1- CC; 1- convoy and 1 - Boat
minNumNodes = 3

minTransRange = 300
minViewRange = 50


def set_edges(graph):
    
    for eachNode in graph.nodes():
        
        for nextNode in graph.nodes():
            
            # not same node in two loops and no conncetion
            if (eachNode != nextNode) and \
             not graph.has_edge(eachNode, nextNode):
                                 
                # for Command Center node
                 if(graph.node[eachNode]["type"] == "CC"):
                     if (graph.node[nextNode]["type"] == "CC") or \
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


def set_CC(graph, CCNode):

    # Sanity checks for input
    if(graph.number_of_nodes() < minNumNodes):
        raise ValueError("Graph doesnt contain sufficient number of nodes to continue.")
        
    if not graph.has_node(CCNode):
        raise ValueError("CC node " + str(CCNode) + " not present")


    #CC Setup
    graph.node[CCNode]["lat"]=50.74
    graph.node[CCNode]["lon"]=-3.36
    graph.node[CCNode]["type"] = "CC"

    return graph


def set_convoy(graph, ConvoyNode, location):

    # Sanity checks for input
    if not graph.has_node(ConvoyNode):
        raise ValueError("Convoy Node " + str(ConvoyNode) + " not present")

    #Convoy setup
    graph.node[ConvoyNode]["lat"] = location[0]
    graph.node[ConvoyNode]["lon"] = location[1]
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

def get_graph(numOfNodes=16):
    graph = nx.Graph()

    # Generate a graph and intialize node attributes
    graph.add_nodes_from(range(numOfNodes))
    graph = initalize(graph)

    #Set Nodes as CC location
    graph = set_CC(graph,graph.nodes()[0])

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
    graph = set_convoy(graph,graph.nodes()[-1],(52.48,-59.98))
    
    #set edges
    graph = set_edges(graph)
    
    return graph
    
def gen_rand_coord():
    
    lon=random.uniform(-63.44, -5.93)
    lat=random.uniform(60.52,42.09)
    
    return((lat,lon))
    
def gen_rand_coord_dist(ptlat, ptlon, distrange):
    
    flag=0
    
    while(flag!=1):
        
    
        lon=random.uniform(-63.44, -5.93)
        lat=random.uniform(ptlat,42.09)
        
        dist=vincenty((lat,lon),(ptlat,ptlon)).kilometers
        
        if(distrange==50 and (40<=dist<=50)):
            print(lat,lon,dist)
            flag=1
        elif(distrange==300 and (250<=dist<=300)):
            print(lat,lon,dist)
            flag=1
        else:
            flag=0
            
    return ((lat,lon))
    
def draw_graph(graph):
    
    pos = {}

    for eachNode in graph.nodes():
        pos[eachNode]=(graph.node[eachNode]["lon"],graph.node[eachNode]["lat"])
        
    # get three subsets of nodes: susceptible, infected, removed
    convoy_node = [n for n in graph.nodes() if graph.node[n]["type"] == "convoy"]
    CC_nodes = [n for n in graph.nodes() if graph.node[n]["type"] == "CC"]
    Uboat_lz_nodes = [n for n in graph.nodes() if ( graph.node[n]["type"] == "Uboat" and \
                     graph.node[n]["listeningZone"] == 1 ) ]
    Uboat_nlz_nodes = [n for n in graph.nodes() if ( graph.node[n]["type"] == "Uboat" and \
                     graph.node[n]["listeningZone"] == 0 ) ]
    empty_nodes = [n for n in graph.nodes() if graph.node[n]["type"] == ""]
    

    # draw edges, then draw each subset in different colour
    nx.draw_networkx_nodes(graph, pos, nodelist=convoy_node, node_color="r")
    nx.draw_networkx_nodes(graph, pos, nodelist=CC_nodes, node_color="c")
    nx.draw_networkx_nodes(graph, pos, nodelist=Uboat_lz_nodes, node_color="y")
    nx.draw_networkx_nodes(graph, pos, nodelist=Uboat_nlz_nodes, node_color="g")
    nx.draw_networkx_nodes(graph, pos, nodelist=empty_nodes, node_color="w")

    nx.draw_networkx_labels(graph, pos)
    
    nx.draw_networkx_edges(graph, pos)
    nx.draw_networkx_edge_labels(graph, pos)

    plt.savefig("UboatSurvival.png") 
    plt.close()


def draw_graphER(graph):
    
#    pos = {}
#
#    for eachNode in graph.nodes():
#        pos[eachNode]=(graph.node[eachNode]["lon"],graph.node[eachNode]["lat"])
#   

    pos = nx.layout.random_layout(graph)     
    
    # get three subsets of nodes: susceptible, infected, removed
    convoy_node = [n for n in graph.nodes() if graph.node[n]["type"] == "convoy"]
    CC_nodes = [n for n in graph.nodes() if graph.node[n]["type"] == "CC"]
    Uboat_lz_nodes = [n for n in graph.nodes() if ( graph.node[n]["type"] == "Uboat" and \
                     graph.node[n]["listeningZone"] == 1 ) ]
    Uboat_nlz_nodes = [n for n in graph.nodes() if ( graph.node[n]["type"] == "Uboat" and \
                     graph.node[n]["listeningZone"] == 0 ) ]
    empty_nodes = [n for n in graph.nodes() if graph.node[n]["type"] == ""]
    

    # draw edges, then draw each subset in different colour    
    nx.draw_networkx_nodes(graph, pos, nodelist=convoy_node, node_color="r")
    nx.draw_networkx_nodes(graph, pos, nodelist=CC_nodes, node_color="c")
    nx.draw_networkx_nodes(graph, pos, nodelist=Uboat_lz_nodes, node_color="y")
    nx.draw_networkx_nodes(graph, pos, nodelist=Uboat_nlz_nodes, node_color="g")
    nx.draw_networkx_nodes(graph, pos, nodelist=empty_nodes, node_color="w")

    nx.draw_networkx_labels(graph, pos)
    nx.draw_networkx_edges(graph, pos)
#    nx.draw_networkx_edge_labels(graph, pos)

    plt.savefig("UboatSurvivalER.png") 
    plt.close()

def get_erdos_renyi_graph(numofNodes=16, edgeProb = 0.2):
    
    oceanGraph = nx.erdos_renyi_graph(numofNodes - minNumNodes, edgeProb)
    oceanGraph = initalize(oceanGraph)
    
    #Set Land Graph
    landGraph = nx.Graph()    
    landGraph.add_nodes_from(range(numofNodes-minNumNodes, numofNodes))
    print(landGraph.nodes())
    
    landGraph = initalize(landGraph)
    landGraph = set_CC(landGraph,landGraph.nodes()[0])
    
    #set uboat outside of listening zone
    landGraph.node[landGraph.nodes()[1]]["type"] = "Uboat"
    landGraph.node[landGraph.nodes()[1]]["state"] = "receive"
    landGraph.node[landGraph.nodes()[1]]["listeningZone"] = 0
    
    #set convoy node
    landGraph = set_convoy(landGraph,landGraph.nodes()[-1],gen_rand_coord())
    
    #connecting both graphs
    graph = nx.compose(oceanGraph, landGraph)    
    graph.add_edge(landGraph.nodes()[0],landGraph.nodes()[1])    
    graph.add_edge(oceanGraph.nodes()[0],landGraph.nodes()[-1])    
    graph.add_edge(oceanGraph.nodes()[-1],landGraph.nodes()[1])

    #Set Uboats in listening zone
    for eachNode in oceanGraph.nodes() :
        newPoint = ()
        if(eachNode==0):
            newPoint = gen_rand_coord_dist(graph.node[landGraph.nodes()[-1]]["lat"],graph.node[landGraph.nodes()[-1]]["lon"],minViewRange)
        else:
            newPoint = gen_rand_coord_dist(graph.node[landGraph.nodes()[eachNode-1]]["lat"],graph.node[landGraph.nodes()[eachNode-1]]["lon"],minTransRange)
        
        graph.node[eachNode]["lat"] = newPoint[0]
        graph.node[eachNode]["lon"] = newPoint[1]
        graph.node[eachNode]["type"] = "Uboat"
        graph.node[eachNode]["state"] = "standBy"
        graph.node[eachNode]["listeningZone"] = 1

    return graph

def realWorldScenario():
    plt.figure(figsize=(15,15))
    
    graph  = get_graph(16)
    draw_graph(graph)
    
    print("Real world Scenario Shortest Path - " ,nx.dijkstra_path(graph,graph.nodes()[-2],graph.nodes()[0]))
    print("Shortest path Length - ",nx.dijkstra_path_length(graph,graph.nodes()[-2],graph.nodes()[0]))
    
    print(graph.nodes(data=True))
    print(graph.edges(data=True))      
    
    
def researchQScenario(numOfNodes=17, probability=0.2):
    
    graph = get_erdos_renyi_graph(numOfNodes,probability)
    
    draw_graphER(graph)
    
    #Convoy ship
    
    print("Shortest Path - " ,nx.dijkstra_path(graph,14,15))
    print("Shortest path Length - ",nx.dijkstra_path_length(graph,14,15))

    print(graph.nodes(data=True))
    print(graph.edges(data=True))      
    
    
    
if __name__ == "__main__":

    
    # Real time scenario    
#    realWorldScenario()


#   Probability Version 
    researchQScenario(17, 0.2)
    