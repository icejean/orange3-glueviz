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

Mar,10th,2020

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

Mar,15th,2020

Add support of vertices & edges selection to the "Network From Tables" widget
through a checkbox on widget GUI and a clean_network() function to verify
vertices ids are in range, remove wrong edges and null vertices if it's necessary,
reindex the ids of vertices if it's necessary. Please refer to the example workflow
 of airtraffic.net in ./docs.
 
If you select a subset of the vertices, the widget will check the "Remove nodes without
any edge" check box automatically to force reindexing the ids of vertices, or you may get an 
index out of range exception when creating the network, as the id values may exceed
the range of the underlying sparse array.
 
Mar,16th,2020

Address the issue of displaying vertices ids as real through setting the decimal
of orange.data.variable.ContinuousVariable to 0, now it's integer as required.

        # set the number of decimals to 0 for ids of vertices, source & target of edges
        # to display as integer
        self.vertices.domain.attributes[0].number_of_decimals = 0
        self.edges.domain.attributes[0].number_of_decimals = 0
        self.edges.domain.attributes[1].number_of_decimals = 0

Mar,18th,2020
        
Add a widget "Network To Tables" to transform a network into vertices & edges data
tables.
Add check to "Network From Tables" widget to check inputs and create an id column
for vertices table if it's necessary.
Update the icons for these two widgets.

Mar,21th,2020

Modify the "Network From Tables" widget to accept changes from the inputs,
without deleting and creating a new widget again. 

Modify the messages from the widget to give important Information, Warning and Error
message icons on the canvas widget icon of Orange workflow.

Fix a bug of the Network From Tables widget in clean_network():

        if removeNodes:
            # nodes = set(list(edges_tb.X[:,0])) | set(list(edges_tb.X[:,1])) 
            nodes = set(list(X1[:,0])) | set(list(X1[:,1]))

Mar,22th,2020

Modify the "Network To Tables" widget to add important information icon upon widget icon 
in canvas workflow.

Add an example to construct a network with igraph-python from the scratch, then
transform into vertices and edges tables, pass to Orange,read ./example/test-igraph1.py
 and python.ows for details.
 
There's an issue of igraph-python that labels wouldn't be shown in Spyder(IPython inline),
it's mentioned here: https://github.com/igraph/python-igraph/issues/185, and the 
 workaround is here: https://stackoverflow.com/questions/30640489/issue-plotting-vertex-labels-using-igraph-in-ipython.
 
Mar,23th,2020

Modify the "Network From Tables" widget to remember original vertices and edges input,
so that when vertices ids are reindexed and vertices or edges input is changed later,
the widget can reference and recompute again, no need to delete and reconnect the other one's
input to get the original data again.


May,22th,2020

Add modifications to Orange Geo, all is in the ./geo directory. 

Notes:

1. Modification_to_orange_geo.txt, details of the modifications.

2. mapper.py and widgets/plotutils.py, widgets/owchoropleth.py, programs modified already. You should
replace the access key of tile provider www.tianditu.gov.cn with your own in plotutils.py.

3. geojson/admin0.json, geojson/admin1-CHN.json, geojson/admin1-IND.json, the GeoJSON file modified
already for use in China, you can replace those in Anaconda3\Lib\site-packages\orangecontrib\geo\geojson
 with them directly, and delete admin1-TWN.json, admin1-HKG.json, admin1-MAC.json at the same time.

4. You can download vector maps of China from https://www.gadm.org/download_country_v3.html, for admin2
 and admin3 level, transform into geojson format and named them as admin2-CHN.json and admin3-CHN.json, 
 then copy to the Anaconda3\Lib\site-packages\orangecontrib\geo\geojson directory for use.
 
5. If you want admin4 support of China, you can buy map data from third party such as 
http://www.dsac.cn/DataProduct/Index/2019, then named it as admin4-CHN.json, and copy it to the directory
above.

6. The file ChinaMap.py is the source to check and modify admin0.json and admin1-CHN.json, 
admin1-IND.json for use in China.

7. The file AddressSeg.py is examples of geocoding with several major providers in China, you should
replace the access key of provider www.tianditu.gov.cn with your own in it.

8. There're  five examples of Orange Geo in the ./geo/example directory. covid-19.py prepares data for 
covid-19-CN-Cities.ows with admin0-2, and ChinaCountyExample.py prepares data for ChinaCountyExample.ows
 with admin0-3 and GuangDongTownsExample.ows with admin0-4. The covid-19-USA.ows is admin0-2 in animation.
 Data needed for the examples is in ./geo/example/data, you may need to modify the ows files for the 
 change of data directory. 
 
 ChinaCountyExample.py also transforms the admin3-4 shp files of China into GeoJSON format Orange Geo required,
 and covid-19.py transforms admin2 shp file of China. Note that you need to buy the admin4-CHN.json data by yourself, 
 it's illegal to publish it here without authorisation. As to the admin0 and admin1 files, they come from
 natrual earth at http://www.naturalearthdata.com/downloads/ , and is free to be modified and published.
   
 The covid-19.ows example is a big example showing how to integrate all kinds of Orange widget components 
 together, which is directly from three articles of the Orange team, and data is from https://github.com/CSSEGISandData/COVID-19 .
 
 A. Data Mining COVID-19 Epidemics: Part 1 : https://orange.biolab.si/blog/2020/2020-04-02-covid-19-basic/
 
 B. Data Mining COVID-19 Epidemics: Part 2 : https://orange.biolab.si/blog/2020/2020-04-09-covid-19-part-2/
 
 C. Data Mining COVID-19 Epidemics: Part 3 : https://orange.biolab.si/blog/2020/2020-4-015-covid-19-part-3/

May,26th,2020

Add an example of customized business map for taxation data base on admin4-CHN.json of GuangDong province.