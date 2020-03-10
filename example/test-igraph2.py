# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 09:04:53 2020

@author: Jean
"""

from igraph import *
import random
import numpy as np

# test for export and rebuild a graph with igraph Graph.DictList() and Graph.TupleList()
def graph2dic(g):
    # if there's a name attribute of a vertex, the source and target column
    # should be the name of a node, else should be the value of id    
    try:
        vertex_names = g.vs["name"]
    except KeyError:
        vertex_names = []
    vs=[]; es=[]
    for vertex in g.vs:
        vt = vertex.attributes()
        vt["id"] = vertex.index
        vs.append(vt)
    if len(vertex_names) == 0:
        for edge in g.es:
            ed = {}
            ed["source"]=edge.tuple[0]
            ed["target"]=edge.tuple[1]
            ed.update(edge.attributes())
            es.append(ed)
    else:
        for edge in g.es:
            ed = {}
            ed["source"]=vertex_names[edge.tuple[0]]
            ed["target"]=vertex_names[edge.tuple[1]]
            ed.update(edge.attributes())
            es.append(ed)
    return(vs,es)


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


# karate net with only node ids and edges
karate = Graph.Read_GML("karate.gml")
summary(karate)
random.seed(42)
plot(karate,bbox=(500,300))
print(karate.is_directed())
# export the graph to dictionaries
vs,es = graph2dic(karate)
vattrs=karate.vs.attribute_names()
print(vattrs)
eattrs = karate.es.attribute_names()
print(eattrs)
# rebuild with Graph.DictList()
karate2 = Graph.DictList(vs,es, vertex_name_attr="id")
random.seed(42)
plot(karate2,bbox=(500,300))
print(karate2.isomorphic(karate))
# add attributes to vertices and edges
for idx,vertex in enumerate(karate.vs):
    vertex["name"]="Jean"+str(vertex.index)
for edge in karate.es:
    edge["weight"]=edge.index
 # export the graph to dictionaries  
vs,es = graph2dic(karate)
vattrs=karate.vs.attribute_names()
print(vattrs)
eattrs = karate.es.attribute_names()
print(eattrs)
# rebuild with Graph.TupleList()
est=[list(edge.values()) for edge in es]
karate3 = Graph.TupleList(est,edge_attrs=eattrs)
random.seed(42)
plot(karate3,bbox=(500,300))
print(karate3.isomorphic(karate))
# rebuild with Graph.DictList()
karate4 = Graph.DictList(vs,es, vertex_name_attr="name")
random.seed(42)
plot(karate3,bbox=(500,300))
print(karate4.isomorphic(karate))


# test orange networks with net only get ids and edges
vstb,estb = graph2tables(karate,name="karate")
print(vstb.name,estb.name)
print(estb.name[estb.name.index("*"):])
print(estb.name[:estb.name.index("*")])
import sys
from Orange.canvas import __main__ as OrangeMain
sys.exit(OrangeMain.main(datasets = [vstb, estb]))

# test orange networks with net get vertices attributes and edges attributes
vstb,estb = graph2tables(karate4, name="karate")
import sys
from Orange.canvas import __main__ as OrangeMain
sys.exit(OrangeMain.main(datasets = [vstb, estb]))

# Write to karate.net, then change the "*Edges" type to "*Arcs" for testing directed graph
# karate4.write_pajek("karate.net")
karate5 = Graph.Read("karate.net")
summary(karate5)
random.seed(42)
plot(karate5,bbox=(500,300))
print(karate5.is_directed())

# test orange network with directed network
vstb,estb = graph2tables(karate5, name="karate")
print(vstb.name,estb.name)
print(estb.name[estb.name.index("*"):])
print(estb.name[:estb.name.index("*")])
import sys
from Orange.canvas import __main__ as OrangeMain
sys.exit(OrangeMain.main(datasets = [vstb, estb]))


# Just for inspecting Orange network with spyder debugger
import sys
from Orange.canvas import __main__ as OrangeMain
sys.exit(OrangeMain.main())

