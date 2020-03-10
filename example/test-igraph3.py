# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 09:08:38 2020

@author: Jean
"""

from igraph import *
import random
import numpy as np

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


# def table_from_frame(df, *, force_nominal=False):
#     """
#     Convert pandas.DataFrame to Orange.data.Table

#     Parameters
#     ----------
#     df : pandas.DataFrame
#     force_nominal : boolean
#         If True, interpret ALL string columns as nominal (DiscreteVariable).

#     Returns
#     -------
#     Table
#     """

#     from pandas.api.types import (
#         is_categorical_dtype, is_object_dtype,
#         is_datetime64_any_dtype, is_numeric_dtype,
#     )
#     from Orange.data import (
#         Table, Domain, DiscreteVariable, StringVariable, TimeVariable,
#         ContinuousVariable,
#     )

#     def _is_discrete(s):
#         return (is_categorical_dtype(s) or
#                 is_object_dtype(s) and (force_nominal or
#                                         s.nunique() < s.size**.666))

#     def _is_datetime(s):
#         if is_datetime64_any_dtype(s):
#             return True
#         try:
#             if is_object_dtype(s):
#                 pd.to_datetime(s, infer_datetime_format=True)
#                 return True
#         except Exception:  # pylint: disable=broad-except
#             pass
#         return False

#     # If df index is not a simple RangeIndex (or similar), put it into data
#     if not (df.index.is_integer() and (df.index.is_monotonic_increasing or
#                                        df.index.is_monotonic_decreasing)):
#         df = df.reset_index()

#     attrs, metas = [], []
#     X, M = [], []

#     # Iter over columns
#     for name, s in df.items():
#         name = str(name)
#         if _is_discrete(s) or name in("id","source","target","isDirected"):
#             discrete = s.astype('category').cat
#             attrs.append(DiscreteVariable(name, discrete.categories.astype(str).tolist()))
#             X.append(discrete.codes.replace(-1, np.nan).values)
#         elif _is_datetime(s):
#             tvar = TimeVariable(name)
#             attrs.append(tvar)
#             s = pd.to_datetime(s, infer_datetime_format=True)
#             X.append(s.astype('str').replace('NaT', np.nan).map(tvar.parse).values)
#         elif is_numeric_dtype(s):
#             attrs.append(ContinuousVariable(name))
#             X.append(s.values)
#         else:
#             metas.append(StringVariable(name))
#             M.append(s.values.astype(object))

#     return Table.from_numpy(Domain(attrs, None, metas),
#                             np.column_stack(X) if X else np.empty((df.shape[0], 0)),
#                             None,
#                             np.column_stack(M) if M else None)



air = Graph.Read("USAir97.net")
summary(air)
random.seed(42)
plot(air,bbox=(500,300))
print(air.is_directed())

# test orange network with node attributes
vstb,estb = graph2tables(air, name="air")
print(vstb.name,estb.name)
print(estb.name[estb.name.index("*"):])
print(estb.name[:estb.name.index("*")])
import sys
from Orange.canvas import __main__ as OrangeMain
sys.exit(OrangeMain.main(datasets = [vstb, estb]))


# Just for inspecting Orange network with spyder debugger
# import sys
# from Orange.canvas import __main__ as OrangeMain
# sys.exit(OrangeMain.main())
