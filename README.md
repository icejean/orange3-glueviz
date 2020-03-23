The Orange3_Glueviz package

Orange add-on for calling Glueviz within Orange.

Please uncomment the lines in setup.py to install required libraries. As I'm 
not really sure of the earliest versions required, I just list the versions in use,
and comment out it in case of breaking down your python package environment. 
Please decide which version to be installed on your need.

Required libraries:

    # install_requires=["orange3>=3.24.1",
    #                   "anyqt>=0.0.10",
    #                   "sortedcollections>=1.1.2",
    #                   "sip>=4.19.8",
    #                   "glueviz>=0.15.2",
    #                   "orange3-network>=1.5.0",
    #                   "numpy>=1.17.4",
    #                   "scipy>=1.3.2"],

Install:

    python setup.py install
    
There's an example in ./example/example.py

If you need to pass data sets to Orange from Spyder,
read the documents in ./doc and hack Orange as it is mentioned.
The two files of Orange need to be modified is there already, just copy and past.

Mar,10,2020

Add a widget named "network from tables" to connect Spyder igraph-python to
orange3-network add on. Please refer to ./example for examples and ./docs for
documents in detail.

First of all, call the function graph2tables() to transform an igraph into two
orange table vertices & edges, then call orange and pass in the tables, and
connect the "network from tables" widget to the two data table widgets to rebuild
the graph.

There's a bug in orangecontrib.network.network.base.py, in the degrees() function
of the DirectedEdges() class, you can copy the file in ./spyder-orange3 directly:

    def degrees(self, *, weighted=False):
        return self._compute_degrees(self.edges, weighted) \
               + self._compute_degrees(self.in_edges, weighted)
               # the original line is wrong
               # + self.compute_degrees(self.in_edges, weighted)

Mar,15,2020

Add support of vertices & edges selection to the "Network From Tables" widget
through a checkbox on widget GUI and a clean_network() function to verify
vertices ids are in range, remove wrong edges and null vertices if it's necessary,
reindex the ids of vertices if it's necessary. Please refer to the example workflow
 of airtraffic.net in ./docs.
 
If you select a subset of the vertices, the widget will check the "Remove nodes without
any edge" check box automatically to force reindexing the ids of vertices, or you may get an 
index out of range exception when creating the network, as the id values may exceed
the range of the underlying sparse array.
 
Mar,16,2020

Address the issue of displaying vertices ids as real through setting the decimal
of orange.data.variable.ContinuousVariable to 0, now it's integer as required.

        # set the number of decimals to 0 for ids of vertices, source & target of edges
        # to display as integer
        self.vertices.domain.attributes[0].number_of_decimals = 0
        self.edges.domain.attributes[0].number_of_decimals = 0
        self.edges.domain.attributes[1].number_of_decimals = 0

Mar,18,2020
        
Add a widget "Network To Tables" to transform a network into vertices & edges data
tables.
Add check to "Network From Tables" widget to check inputs and create an id column
for vertices table if it's necessary.
Update the icons for these two widgets.

Mar,21,2020

Modify the "Network From Tables" widget to accept changes from the inputs,
without deleting and creating a new widget again. 

Modify the messages from the widget to give important Information, Warning and Error
message icons on the canvas widget icon of Orange workflow.

Fix a bug of the Network From Tables widget in clean_network():

        if removeNodes:
            # nodes = set(list(edges_tb.X[:,0])) | set(list(edges_tb.X[:,1])) 
            nodes = set(list(X1[:,0])) | set(list(X1[:,1]))

Mar,22,2020

Modify the "Network To Tables" widget to add important information icon upon widget icon 
in canvas workflow.

Add an example to construct a network with igraph-python from the scratch, then
transform into vertices and edges tables, pass to Orange,read ./example/test1-igraph1.py
 and python.ows for details.
 
There's an issue of igraph-python that labels wouldn't be shown in Spyder(Ipython inline),
it's mentioned here: https://github.com/igraph/python-igraph/issues/185, and the 
 work around is here: https://stackoverflow.com/questions/30640489/issue-plotting-vertex-labels-using-igraph-in-ipython.
 
Mar,23,2020

Modify the "Network From Tables" widget to remember original vertices and edges input,
so that when vertices ids are reindexed and vertices or edges input is changed later,
the widget can reference and recompute again, no need to delete and reconnect the other one's
input to get the original data again.

       