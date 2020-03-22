# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 09:05:26 2020

@author: Jean
"""

from igraph import *
import random
import numpy as np
import pandas as pd

# transform an igraph network to Orange data tables of vertices and edges
# the "id" attribute identifys a node, and "source" and "target" attributes for an edge
def graph2tables(g,name="network"):
    import pandas as pd
    from Orange.data.pandas_compat import table_from_frame
    # vertices data table
    vattrs=g.vs.attribute_names()
    vertices= pd.DataFrame()
    for vattr in vattrs:
        vertices[vattr] = g.vs[vattr]
    # when created with Graph.DictList(), the id,source,target attributes are strings
    vertices["id"] = [vertex.index for vertex in g.vs]  #update a vertex's id to it's index
    vtable = table_from_frame(vertices); vtable.X[:,0].astype(np.int)
    vtable.name = name+"*vertices"
    # edges data table
    source=[]; target=[]
    for edge in g.es:
        source.append(edge.tuple[0])    # index of source vertex
        target.append(edge.tuple[1])    # index of target vertex   
    edges = pd.DataFrame({"source":source,"target":target})
    eattrs = g.es.attribute_names()
    try:    # if an igraph has the "name" attribute, it's built with Graph.DistList()
        vertex_names = g.vs["name"] # there'll be extra "source" and "target" attributes
        eattrs.remove("source")     # then need to get rid or it
        eattrs.remove("target")     # since we'll get it from edge.tuple instead
    except:                         # otherwise, the graph is built with Graph.TupleList()
        pass                        # will get KeyError or ValueError, just pass
    for eattr in eattrs:
        edges[eattr] = g.es[eattr]
    if g.is_directed():
        edges["isDirected"] = 1 # True
    else:
        edges["isDirected"] = 0 # False
    etable=table_from_frame(edges);etable.X[:,0].astype(np.int);etable.X[:,1].astype(np.int)
    etable.name = name+"*edges"
    # return two tables of vertices and edges
    return(vtable,etable)


# vertices, [[id,name,type]]
nodes = []; classes = []
nodes.append("Spyder"); classes.append("software")
nodes.append("Orange"); classes.append("software")
nodes.append("Orange Network"); classes.append("software")
nodes.append("Orange Text"); classes.append("software")
nodes.append("Orange Time Series"); classes.append("software")
nodes.append("Orange Geo"); classes.append("software")
nodes.append("Glueviz"); classes.append("software")
nodes.append("Data Frame"); classes.append("data")
nodes.append("Data Table"); classes.append("data")
nodes.append("Data object"); classes.append("data")
nodes.append("Network"); classes.append("data")
nodes.append("Corpus"); classes.append("data")
nodes.append("Numpy array"); classes.append("data")
nodes.append("Sparse array"); classes.append("data")
vd = pd.DataFrame({"id":range(len(nodes)),"name":nodes,"type":classes})
# edges, [[source id,target id, weight]]
ea = np.array([[0,1,5],[1,0,3],[0,6,5],
               [0,7,5],[0,8,1],[0,9,1],[0,10,1],[0,11,1],[0,12,5],[0,13,3],
               [1,2,8],[1,3,8],[1,4,8],[1,5,8],[1,6,5],
               [1,8,5],[2,10,5],[3,11,5],[6,9,5],
               [7,8,1],[8,7,1],[7,9,1],[9,7,1],[8,10,1],[10,8,1],[8,11,1],[11,8,1],
               [12,13,1],[13,12,1],[7,12,1],[8,12,1],[9,12,1],[10,13,1]])
ed =pd.DataFrame({"source":list(ea[:,0]),"target":list(ea[:,1]),"weight":list(ea[:,2])})

# turn into dictionary and build a graph with Graph.DictList()
vdir = vd.to_dict(orient="records")
edir = ed.to_dict(orient="records")
g = Graph.DictList(vdir,edir, vertex_name_attr="id", directed=True)

# vertices labels
g.vs["label"]=g.vs["name"]
g.vs["label_dist"]=1
# set color for different vertex type
color_dict = {"software": "red", "data": "blue"}
g.vs["color"] = [color_dict[gender] for gender in g.vs["type"]]
# set color for different edges between different vertices
vs = g.vs.select(type_eq="software")
es = g.es.select(_target_in=vs)
es["color"] = "red"
vs2 = g.vs.select(label_in=["Spyder","Glueviz"])
ids=vs["id"]; ids2=vs2["id"]
ids3 = list( set(ids)-set(ids2))
es = g.es.select(_within=ids3)
es["color"] = "orange"
vs = g.vs.select(type_eq="data")
es = g.es.select(_target_in=vs)
es["color"] = "blue"
es = g.es.select(_within=vs)
es["color"] = "darkgreen"
# set edges label and width with weight
g.es["width"] = g.es["weight"]
g.es["label"]=g.es["weight"]
# set layout of the graph
layout = g.layout("kk")
# set random to same to get the same graph next time
random.seed(20)
plot(g,bbox=(500,300),layoyt = layout)
# plot(g,"python_suits.SVG",layoyt = layout)
# test orange network with directed network
vstb,estb = graph2tables(g, name="Python")
import sys
import Orange
from Orange.canvas import __main__ as OrangeMain
sys.exit(OrangeMain.main(datasets = [vstb, estb]))
