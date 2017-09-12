#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 17 13:37:15 2017

@author: jdn93577
"""

import sys

from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine
import shutil 

import os 

if __name__ == '__main__':
  

    def on_create_template(plugin_info):
        final = plugin_info.toVariant()
        #print final
        modname = final["Plugin template name:"]
        modname = modname if len(modname.split('.py')) > 1 else modname + '.py'  
        
        
        with open(modname, 'a+') as f:
             shutil.copyfile('intro.py',modname)
             # still need to see if i can add to a specific line so can add name nd email 
             f.write('\n\n    def pre_process(self):\n       ')
             f.write(final["pre-processing selection:"])
             
             f.write('\n\n    def filter_frames(self,data):\n       ')
             f.write(final["processing"])
             
             f.write('\n\n    def post_process(self):\n       ')
             f.write(final["post-processing selection:"])
             
             f.write('\n\n    def setup(self):\n       pass')
             f.write('\n\n    def nInput_datasets(self):\n       return ')
             
             f.write( final["No. of inputs:"])
             f.write('\n\n    def nOutput_datasets(self):\n       return ')
             
             f.write( final["No. of outputs:"])  
             f.write("\n\n    def get_max_frames(self):\n       return 'multiple'")

        f.close    
        print 'done, go to :  '+ os.path.dirname(os.path.realpath(__file__)) + '/' + modname
             
    QGuiApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    myApp = QApplication(sys.argv)
    # Create a label and set its properties
    engine = QQmlApplicationEngine()
    engine.load(QUrl.fromLocalFile('plugin_template_v6.qml'))
    window = engine.rootObjects()[0]

    window.createTemplate.connect(on_create_template)# connects the signal from teh qml file
    window.show()


    sys.exit(myApp.exec_())