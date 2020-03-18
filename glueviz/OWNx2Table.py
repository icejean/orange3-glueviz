# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 10:40:39 2020

@author: Jean
"""

import numpy as np
from Orange.widgets import gui
from Orange.widgets.utils.widgetpreview import WidgetPreview
from Orange.widgets.widget import OWWidget, Input, Output
from orangecontrib.network.network.base import Network
from orangecontrib.network.network.readwrite import read_pajek
from Orange.data import (
    Table, Domain, StringVariable, 
    ContinuousVariable
)

class OWNx2Table(OWWidget):
    name = "Network To Tables"
    description = "Transform a network to vertices and edges data tables."
    icon = "icons/NetworkToTables.svg"
    priority = 300

    class Inputs:
        network = Input("Network", Network)

    class Outputs:
        vertices = Output("Vertices", Table)
        edges = Output("Edges", Table)

       
    want_main_area = False

    def __init__(self):
        super().__init__()
        self.vertices = None         # Output vertices
        self.edges = None            # Output edges
        self.network = None          # Input network    

        # GUI
        box = gui.widgetBox(self.controlArea, "Info")
        self.infoa = gui.widgetLabel(box, "Please connect to a network.")
        self.infob = gui.widgetLabel(box, "No vertex on output.")       
        self.infoc = gui.widgetLabel(box, "No edge on output.") 

    @Inputs.network
    def set_network(self, network):
        self.network = network
        if self.network is None:
            self.vertices =None
            self.edges =None
            self.infoa.setText("Please connect to a network.")
            self.infob.setText("No vertex on output.")
            self.infoc.setText("No edge on output.")
        else:
            self.network2tables()
            self.infoa.setText("A network is connected on input.")
            if self.vertices is not None:
                self.infob.setText("%d vertices on output." % self.vertices.X.shape[0])
            else:
                self.infob.setText("No vertex on output.")
            if self.edges is not None:
                self.infoc.setText("%d edges on output." % self.edges.X.shape[0])
            else:
                self.infoc.setText("No edge on output.")
                
        self.send_output()


    # Transform a network to vertices and edges data tables
    def network2tables(self):
        network = self.network
        # create the vertices data table
        nodes = network.nodes
        if isinstance(nodes,Table):                 # if it's a data table already
            if len(nodes.domain.attributes) == 0:   # no attribute column, so no id column
                X = np.array(range(nodes.metas.shape[0]))   # add an id column for it
                X = X.reshape(len(X),1)
                domain = Domain([ContinuousVariable("id")], nodes.domain.class_vars, nodes.domain.metas)
                vertices = Table.from_numpy(domain,X,nodes.Y,nodes.metas,nodes.W)
                self.vertices = vertices
            else:                                   # check if there's an id column
                idcol = None
                for i,attr in enumerate(nodes.domain.attributes):
                    if attr.name=="id":
                        idcol=attr
                        break
                if idcol is None:   # no id column, add an id column for it
                    X1 = np.array(range(nodes.X.shape[0]))
                    X = nodes.X
                    X = np.insert(X, 0, values=X1, axis=1)
                    attrs = []
                    for attr in nodes.domain.attributes:
                        attrs.append(attr)
                    attrs.insert(0,ContinuousVariable("id"))
                    domain = Domain(attrs,nodes.domain.class_vars,nodes.domain.metas)
                    vertices = Table.from_numpy(domain,X,nodes.Y,nodes.metas,nodes.W)
                    self.vertices = vertices
                else:               # there's an id column already
                    self.vertices = nodes
        else:                       # it's an label array of nodes, so add an id column
            nodes = nodes.reshape(len(nodes),1)                    #  and a name column
            ids = np.array(range(len(nodes)))
            if network.coordinates is None:                        # no coordinates
                ids = ids.reshape(len(ids),1)
                domain = Domain([ContinuousVariable("id")], None, [StringVariable("name")])
                vertices = Table.from_numpy(domain,ids,None,nodes,None)
            else:                                                  # with coordinates
                X = np.array([ids,network.coordinates[:,0],network.coordinates[:,1]]).T
                domain = Domain([ContinuousVariable("id"),ContinuousVariable("x"),\
                                 ContinuousVariable("y")], None, [StringVariable("name")])
                vertices = Table.from_numpy(domain,X,None,nodes,None)
                
            self.vertices = vertices
        
        # create the edges data table from sparse matrix
        edges = network.edges
        source = []; target = []; weight = []
        isDirected = 0
        for edge in edges:
            es = edge.edges
            if edge.directed:
                isDirected = 1
            for i in range(es.shape[0]):
                matrix = es[i].tocoo()
                weight += matrix.data.tolist()
                source += [i]*matrix.nnz
                target += [r+c for r,c in zip(matrix.row, matrix.col)]
        directed = np.array([isDirected]*len(source))
        X =np.array([source,target,weight,directed]).T
        domain = Domain([ContinuousVariable("source"),ContinuousVariable("target"),\
                          ContinuousVariable("weight"),ContinuousVariable("isDirected")],\
                        None, None)
        edges = Table.from_numpy(domain,X,None,None,None)
        self.edges = edges


    # send the vertices & edges data table created to output signal    
    def send_output(self):
        self.Outputs.vertices.send(self.vertices)
        self.Outputs.edges.send(self.edges)


if __name__ == "__main__":
    # Just for widget debugging
    WidgetPreview(OWNx2Table).run(
        read_pajek("D:/JetBrains/IdeaProjects/MyPyhton38/scripts/USAir97.net")
    )
              