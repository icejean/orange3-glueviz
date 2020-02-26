# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 10:42:20 2020

@author: Jean
"""

from collections import OrderedDict
import Orange.data
from Orange.data import Table
from Orange.widgets.widget import OWWidget, Input
from Orange.widgets.utils.widgetpreview import WidgetPreview
from Orange.widgets import gui
from Orange.data.pandas_compat import table_to_frame
from AnyQt.QtWidgets import QTableWidget, QTableWidgetItem


class OWGlueviz(OWWidget):
    name = "Glueviz Explorer"
    description = "Explore data sets with Glueviz."
    icon = "icons/gluevizapp_icon.png"
    priority = 100

    class Inputs:
        data = Input("Data", Orange.data.Table, multiple=True)
    
    want_main_area = False

    def __init__(self):
        super().__init__()

        #: A {input_id: table} mapping of current tables from input channel
        self.tables = OrderedDict()

        # GUI
        box = gui.widgetBox(self.controlArea, "Info")
        self.infoa = gui.widgetLabel(box, "No data on input.")
        self.infob = gui.widgetLabel(box, "Please connect to other widgets.")

        gui.separator(self.controlArea)

        self.tablesbox = gui.widgetBox(self.controlArea, "Table List")
        gui.button(self.tablesbox, self, "Run Glueviz", callback=self.commit)
        self.tablesbox.setDisabled(True)

        gui.separator(self.controlArea)
        
        # table widget for statistic data of input tables
        self.tablelist = gui.table(self.controlArea, selectionMode=QTableWidget.NoSelection)

        
    @Inputs.data
    def set_data(self, data, id):
        """Set the input data for channel id."""
        if id in self.tables:
            if data is None:
                del self.tables[id]
            else:
                df = table_to_frame(data,include_metas=True)
                df.name = data.name
                self.tables[id] = df
        else:
            if data is not None:
                df = table_to_frame(data,include_metas=True)
                df.name = data.name
                self.tables[id] = df
        if len(self.tables):
            self.infoa.setText("%d tables on input." % len(self.tables))
            self.infob.setText("Please click the button below to run Glueviz.")
            self.tablesbox.setDisabled(False)           
        else:
            self.infoa.setText("No data on input.")
            self.infob.setText("Please connect to other widgets.")            
            self.tablesbox.setDisabled(True)
        self._update_tablelist()


    def _update_tablelist(self):
        self.tablelist.setRowCount(0)
        self.tablelist.setRowCount(len(self.tables))
        self.tablelist.setColumnCount(3)

        self.tablelist.setHorizontalHeaderLabels(["Name","Columns","Rows"])
        for row, table in enumerate(self.tables.values()):
            self.tablelist.setItem(row, 0, QTableWidgetItem(table.name))
            self.tablelist.setItem(row, 1, QTableWidgetItem(str(table.shape[1])))
            self.tablelist.setItem(row, 2, QTableWidgetItem(str(table.shape[0])))

        for i in range(len(self.tables)):
            sh = self.tablelist.sizeHintForColumn(i)
            cwidth = self.tablelist.columnWidth(i)
            self.tablelist.setColumnWidth(i, max(sh, cwidth))

    # ------------------------------------------------------------------
    # Very important!!! Can't open another QMainWindow without this line
    # Keep a reference to the new QMainWindow in the widget
    windowList = []
    gluvizapp = None
    
    def commit(self):
        # Test if Glueviz is running or closed already
        if self.gluvizapp is not None:
            import sip
            app = self.gluvizapp
            if sip.isdeleted(app):
                # Clear last instance closed
                self.gluvizapp = None
                self.infob.setText("Please click the button below to run Glueviz.")
                return
            # Glueviz is running
            else:
                return
        
        from glue.core import DataCollection
        from glue.qglue import parse_data
        
        dc = DataCollection()
        for table in self.tables.values():
            gd = parse_data(table, table.name)            
            dc.append(gd[0])

        # start Glue
        from glue.app.qt.application import GlueApplication
        self.gluvizapp = GlueApplication(dc)
        # ------------------------------------------------------------------
        # Very important!!! Can't open another QMainWindow without this line
        self.windowList.append(self.gluvizapp)
        self.close()
        self.gluvizapp.start()
        self.infob.setText("Glueviz is running.")


if __name__ == "__main__":
    WidgetPreview(OWGlueviz).run(
        [(Table("iris"), "iris"),
        (Table("brown-selected"), "brown-selected"),
        (Table("housing"), "housing")
        ]
    )     


        

