# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 15:18:05 2020

@author: Jean
"""

# Prepare datasets in Orane Table format with Spyder.
from Orange.data import Table
table1 = Table("iris")
# set name to be displayed in Glueviz
table1.name = "iris"
table2 = Table("titanic")
# set name to be displayed in Glueviz
table2.name = "titanic"

# Call Orange and pass in the prepared data sets
import sys
from Orange.canvas import __main__ as OrangeMain
sys.exit(OrangeMain.main(datasets = [table1,table2]))

# Do some data mining works with Orange.
# Call Glueviz to explore data sets with the "Glueviz Explorer" widget in Orange.