The Orange3_Glueviz package

Orange add-on for calling Glueviz within Orange.

Please uncomment the lines in setup.py to install required libraries.

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
