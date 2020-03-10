# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 09:04:53 2020
@author: Jean
Widget to create a network from vertices and edges orange data tables.
"""

import numpy as np
import scipy.sparse as sp
from Orange.data import Table
from Orange.widgets import gui
from Orange.widgets.utils.widgetpreview import WidgetPreview
from Orange.widgets.widget import OWWidget, Input, Output
from orangecontrib.network.network.base import Network, EdgeType

class OWNxTable(OWWidget):
    name = "Network From Tables"
    description = "Create a network from vertices and edges data tables."
    icon = "icons/NetworkFile.svg"
    priority = 200

    class Inputs:
        vertices = Input("Vertices", Table, default=True)
        edges = Input("Edges", Table)

    class Outputs:
        network = Output("Network", Network)
        vertices = Output("Vertices", Table)
       
    want_main_area = False

    def __init__(self):
        super().__init__()
        # Design copied from orangecontrib.network.widgets.OWNxFile.py
        self.vertices = None
        self.edges = None
        self.auto_data = None        
        self.network = None       
        self.original_nodes = None

        # GUI
        box = gui.widgetBox(self.controlArea, "Info")
        self.infoa = gui.widgetLabel(box, "No vertices on input.")
        self.infob = gui.widgetLabel(box, "No edges on input.")       
        self.infoc = gui.widgetLabel(box, "Please connect to vertices and edges widgets.")

    @Inputs.vertices
    def set_vertices(self, vertices):
        # TODO: try to change it to int, not successed yet
        # it seems that numpy array must be the same type, both float and int is impossible.        
        # if vertices is not None:
        #     vertices.X[:,0].astype(np.int)
        self.vertices = vertices
        self.auto_data = vertices
        if self.vertices is not None:
            self.infoa.setText("%d vertices on input." % self.vertices.X.shape[0])
        else:
            self.infoa.setText("No vertices on input.")
        self.update_network()
        self.send_output()

    @Inputs.edges
    def set_edges(self, edges):
        # TODO: try to change it to int, not successed yet
        # it seems that numpy array must be the same type, both float and int is impossible.        
        # if edges is not None:
        #     edges.X[:,0].astype(np.int)
        #     edges.X[:,1].astype(np.int)            
        self.edges = edges
        if self.edges is not None:
            self.infob.setText("%d edges on input." % self.edges.X.shape[0]) 
        else:
            self.infob.setText("No edges on input." )
        self.update_network()
        self.send_output()

    # Create a network from input vertices and edges tables
    def update_network(self):
        if self.edges is None or self.vertices is None:
            if self.vertices is None:
                self.infoc.setText("Please connect to a vertices widget." )
            if self.edges is None:
                self.infoc.setText("Please connect to an edges widget." )
            if self.edges is None and self.vertices is None:
                self.infoc.setText("Please connect to vertices and edges widgets." )                
            self.network = None
            self.original_nodes = None
            return
        # get labels of vertices
        vertices_tb = self.vertices
        namecol = None
        for i,meta in enumerate(vertices_tb.domain.metas):
            if meta.name=="name":
                namecol=meta
                break
        if namecol is None:
            labels = vertices_tb.X[:,0].astype(np.int)
        else:
            labels = vertices_tb.metas[:,i]
        # get weights of edges
        nvertices = len(labels)            
        edges_tb = self.edges
        edges = []        
        weightcol = None
        for i,attr in enumerate(edges_tb.domain.attributes):
            if attr.name=="weight":
                weightcol=attr
                break
        if weightcol is None:
            weights = np.array([1.0]*edges_tb.X.shape[0])
        else:
            weights = edges_tb.X[:,i].astype(np.float64)
        # create a sparce mattrix of the network
        co_matrix = sp.coo_matrix((weights, 
                (edges_tb.X[:,0].astype(np.int), edges_tb.X[:,1].astype(np.int))),
                shape=(nvertices, nvertices))
        # determin whether it's directed
        isDirectedCol = None        
        for i,attr in enumerate(edges_tb.domain.attributes):
            if attr.name=="isDirected":
                isDirectedCol=attr
                break
        edges_tb.X[:,i].astype(np.int)
        isDirected = edges_tb.X[0,i]
        edges.append(EdgeType[isDirected>0](co_matrix))
        # if there's a name of the network
        try:
            netname = edges_tb.name[:edges_tb.name.index("*")]
        except:
            netname = "UNKNOWN"
        # create the network
        try:
            network = Network(labels, edges, netname, None)
            self.network = network
            # set node attributes here, so that network explorer can reference later
            # it's the vertices' Orange Table directly
            self.network.nodes = self.vertices
            self.original_nodes = self.network.nodes
        except:
            self.network = None
            self.original_nodes = None
        if self.network is None:
            self.infoc.setText("Wrong data, no network is created." )
        else:
            self.infoc.setText("A network named %s is created." % self.network.name)
                      
    # send the network created to output signal    
    def send_output(self):
        if self.network is None:
            self.Outputs.network.send(None)
            self.Outputs.vertices.send(None)
            return
        self.Outputs.network.send(self.network)
        self.Outputs.vertices.send(self.network.nodes)
        
        
if __name__ == "__main__":
    # Just for widget debugging
    WidgetPreview(OWNxTable).run(
       set_vertices=Table("D:/JetBrains/IdeaProjects/MyPyhton38/scripts/vertices"),
       set_edges=Table("D:/JetBrains/IdeaProjects/MyPyhton38/scripts/edges")
    )
