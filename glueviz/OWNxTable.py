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
from Orange.widgets.settings import Setting, ContextSetting

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
        edges = Output("Edges", Table)

       
    want_main_area = False
    # Remove nodes without any edge
    removeNodes = Setting(1)

    def __init__(self):
        super().__init__()
        # Design copied from orangecontrib.network.widgets.OWNxFile.py
        self.vertices = None
        self.edges = None
        self.auto_data = None        
        self.network = None       
        self.original_nodes = None
        self.verticesDeleted = 0
        self.edgesDeleted = 0

        # GUI
        box = gui.widgetBox(self.controlArea, "Info")
        self.infoa = gui.widgetLabel(box, "No vertex on input.")
        self.infob = gui.widgetLabel(box, "No edge on input.")       
        self.infoc = gui.widgetLabel(box, "Please connect to vertices and edges widgets.")
        self.infod = gui.widgetLabel(box, "No vertex deleted on output.")       
        self.infoe = gui.widgetLabel(box, "No edge deleted on output.") 
        self.infof = gui.widgetLabel(box, "")               
              
        gui.checkBox(box, self, "removeNodes", "Remove nodes without any edge.")

    @Inputs.vertices
    def set_vertices(self, vertices):
        # TODO: try to change it to int, not successed yet
        # it seems that numpy array must be the same type, both float and int is impossible.        
        # if vertices is not None:
        #     vertices.X[:,0].astype(np.int)
        if self.verticesDeleted>0:
            self.infof.setText("Vertices ids are recoded, please delete & create the widget again!")
            return
        self.vertices = vertices
        self.auto_data = vertices
        if self.vertices is not None:
            self.infoa.setText("%d vertices on input." % self.vertices.X.shape[0])
        else:
            self.infoa.setText("No vertex on input.")
            self.infod.setText("No vertex deleted on output.")
            self.infoe.setText("No edge deleted on output.")        

        self.update_network()
        self.send_output()

    @Inputs.edges
    def set_edges(self, edges):
        # TODO: try to change it to int, not successed yet
        # it seems that numpy array must be the same type, both float and int is impossible.        
        # if edges is not None:
        #     edges.X[:,0].astype(np.int)
        #     edges.X[:,1].astype(np.int)
        if self.verticesDeleted>0:
            self.infof.setText("Vertices ids are recoded, please delete & create the widget again!")
            return           
        self.edges = edges
        if self.edges is not None:
            self.infob.setText("%d edges on input." % self.edges.X.shape[0]) 
        else:
            self.infob.setText("No edge on input." )
            self.infod.setText("No vertex deleted on output.")
            self.infoe.setText("No edge deleted on output.")
            
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
        
        # delete the edges without nodes or nodes without any edge
        self.clean_network()
        
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
            self.infod.setText("No vertex deleted on output.")
            self.infoe.setText("No edge deleted on output.")
        else:
            self.infoc.setText("A network named %s is created." % self.network.name)
            if self.verticesDeleted>0:
                self.infod.setText("%d vertices without any edge are deleted on output, ids're recoded." % self.verticesDeleted)
            else:
                self.infod.setText("No vertex deleted on output.")
            if self.edgesDeleted>0:
                self.infoe.setText("%d edges with vertex out of range are deleted on output." % self.edgesDeleted)
            else:
                self.infoe.setText("No edge deleted on output.")
           

    # delete the edges without nodes and nodes without any edge if reuired
    def clean_network(self):
        vertices_tb = self.vertices
        edges_tb = self.edges
        verticesDeleted = 0
        edgesDeleted = 0
        # delete edges without nodes
        nodes = set(list(vertices_tb.X[:,0]))
        X1=edges_tb.X; Y1=edges_tb.Y; W1=edges_tb.W; metas1 = edges_tb.metas
        todelete=[]
        try:
            for i in range(X1.shape[0]):
                if X1[i,0] not in nodes or X1[i,1] not in nodes:
                    todelete.append(i)
            if len(todelete)>0:
                X1 = np.delete(X1, todelete, axis = 0)
                if metas1 is not None:
                    metas1 = np.delete(metas1, todelete, axis = 0)
                if Y1 is not None:
                    Y1 = np.delete(Y1, todelete, axis = 0)
                if W1 is not None:
                    W1 = np.delete(W1, todelete, axis = 0)
                edgesDeleted = len(todelete)
        except:
            pass
                
        # delete nodes without any edge
        removeNodes = self.removeNodes
        if removeNodes:
            nodes = set(list(edges_tb.X[:,0])) | set(list(edges_tb.X[:,1]))            
            X2=vertices_tb.X; Y2=vertices_tb.Y; W2=vertices_tb.W; metas2 = vertices_tb.metas            
            todelete=[]
            try:
                for i in range(X2.shape[0]):
                    if X2[i,0] not in nodes:
                        todelete.append(i)
                if len(todelete)>0:
                    X2 = np.delete(X2, todelete, axis = 0)
                    if metas2 is not None:
                        metas2 = np.delete(metas2, todelete, axis = 0)
                    if Y2 is not None:
                        Y2 = np.delete(Y2, todelete, axis = 0)
                    if W2 is not None:
                        W2 = np.delete(W2, todelete, axis = 0) 
                verticesDeleted = len(todelete)
            except:
                pass
                        
            # Recode vertices ids and edges source and target
            XV = X2[:,0].astype(np.int) ; XE = X1[:,[0,1]].astype(np.int)
            # sort is important for recoding
            nodes = list(XV)
            nodes.sort()
            for i in range(len(nodes)):
                XE[XE==nodes[i]] = i
                XV[i] = i
            X1[:,0] = XE[:,0]
            X1[:,1] = XE[:,1]
            X2[:,0] = XV
            
            vertices_tb2 = Table.from_numpy(vertices_tb.domain,X2,Y2,metas2,W2)            
            self.vertices = vertices_tb2
        
        edges_tb2 = Table.from_numpy(edges_tb.domain,X1,Y1,metas1,W1)
        self.edges = edges_tb2
        self.edgesDeleted = edgesDeleted
        self.verticesDeleted = verticesDeleted
           
                    
    # send the network created to output signal    
    def send_output(self):
        if self.network is None:
            self.Outputs.network.send(None)
            self.Outputs.vertices.send(None)
            self.Outputs.edges.send(None)
            return
        self.Outputs.network.send(self.network)
        self.Outputs.vertices.send(self.network.nodes)
        self.Outputs.edges.send(self.edges)

        
        
if __name__ == "__main__":
    # Just for widget debugging
    WidgetPreview(OWNxTable).run(
       set_vertices=Table("D:/JetBrains/IdeaProjects/MyPyhton38/scripts/air-vertices2"),
       set_edges=Table("D:/JetBrains/IdeaProjects/MyPyhton38/scripts/air-edges2")
    )
