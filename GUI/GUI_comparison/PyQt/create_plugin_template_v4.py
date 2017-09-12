#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 10:12:15 2017

@author: jdn93577
"""

import sys
import PyQt5.QtWidgets as pw
import PyQt5.QtGui as pg
import shutil 
import os 



class PluginTemplateCreator(pw.QWidget):
    
    def __init__(self):
        super(PluginTemplateCreator, self).__init__()
        self.content = {}
        self._setup_dictionary()
        self.initUI()
        
    def _setup_dictionary(self):
        self.content = {}
        self.content['mod'] = {'label':'plugin template name', 'edit': None, 'position':1, 'type': 1} # the position corresponds to the row it appears in the grid layout 
        self.content['user_name']= {'label':'Your name:',  'edit': None,'position':2,'type': 1}# type determines whether a textbox or  a dropdown item is added
        self.content['e_mail'] = {'label':'Your e-mail:', 'edit': None, 'position':3,'type': 1}
        self.content['pre_processing_selection']={'label':'preProcessingSelection','edit': None,'position':4,'type': 2}
        self.content['process']={'label':'process:', 'edit': None,'position':5,'type': 2}
        self.content['post_processing_selection']={'label':'postProcessingSelection', 'edit': None,'position':6,'type': 2}        
        self.content['number_of_inputs']={'label':'No. of input data sets:', 'edit': None,'position':7,'type': 1}
        self.content['number_of_outputs']={'label':'No. of output data sets:', 'edit': None,'position':8,'type': 1}        
        
    def createTextBox(self,entry):# Function that creates a label with a text input box to the right of it 
        entry['edit'] = pw.QLineEdit()# when textBox is edited it will add the entry to the  content dictionary 
        pg.grid.addWidget(pw.QLabel(entry['label'] ), entry['position'], 0)
        pg.grid.addWidget(entry['edit'], entry['position'], 1)     
        
    def createDropdown(self,entry):#  Function that creates a label with a dropdown menu to the right of it 
        entry['edit'] = pw.QComboBox()        
        entry['edit'].addItems(['pass','process'])# gives the options for the dropdown menu
        pg.grid.addWidget(pw.QLabel(entry['label']),entry['position'],0)
        pg.grid.addWidget(entry['edit'],entry['position'],1)
        
    def initUI(self):# constructor for the layout of the GUI
        
        pw.QToolTip.setFont(pg.QFont('SansSerif', 10))
        
        pg.grid = pw.QGridLayout() 
        pg.grid.setSpacing(10)
        
        for key in self.content: # adds all elements of GUI specified in the dictionary 
          if (self.content[key]['type'] == 1): 
            self.createTextBox( self.content[key])   
          else :
            self.createDropdown(self.content[key])
          
        
        qbtn = pw.QPushButton('Create plugin template', self)       
        qbtn.clicked.connect(self.CreateModule) # calls the template writing function when create template is clicked
        qbtn.setToolTip('This is a creates a plugin template as a .py file ')	# when buttons is hovered over tip on what is does pops up 
  
        pg.grid.addWidget(qbtn, 9,0)
        
        self.setLayout(pg.grid)
        
        self.setWindowTitle('Create plugin template')    
        self.show() 
        
      
    # This function deals with writing the plugin template, using the input from the user 
    def CreateModule(self): 
        modname = self.content['mod']['edit'].text()
        modname = modname if len(modname.split('.py')) > 1 else modname + '.py'  
        
        #print(self.dictionary)
        
        with open(modname, 'a+') as f:
             shutil.copyfile('intro.py',modname)# starts the file with the things that are constant 
             f.write('\n\n    def pre_process(self):\n       ' + self.content['pre_processing_selection']['edit'].currentText())
             
             f.write('\n\n    def process_frames(self,data):\n       ' + self.content['process']['edit'].currentText())
             
             f.write('\n\n    def post_process(self):\n       ' + self.content['post_processing_selection']['edit'].currentText())
             
             f.write('\n\n    def setup(self):\n       pass')
             
             f.write('\n\n    def nInput_datasets(self):\n       return ')
             f.write( self.content['number_of_inputs']['edit'].text())
             
             f.write('\n\n    def nOutput_datasets(self):\n       return ')
             f.write( self.content['number_of_outputs']['edit'].text())  
             f.write("\n\n    def get_max_frames(self):\n       return 'multiple'")
             

        f.close
        print 'done, go to :  '+ os.path.dirname(os.path.realpath(__file__)) + '/' + modname


# creates the GUI window, with specifications given above 
        
if __name__ == '__main__':
    
    app = pw.QApplication(sys.argv)
    ex = PluginTemplateCreator()
    sys.exit(app.exec_())
    
