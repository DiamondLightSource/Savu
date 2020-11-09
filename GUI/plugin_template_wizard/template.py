import os 
class Template:

  
          # functions used to write template 

      def add_on(self,f,openfile):# adds openfile onto main file f 
          with open(openfile) as input:
            f.write(input.read())
            input.close        
            
      def pdata_setup(self, f,plugin_info,InOrOut,n ): # creates plugin datasets
          patternN =  InOrOut + ' plugin pattern ' + str(n +1) 
          pat = "'" + plugin_info[patternN] + "'"
          if pat == "'pass as parameter'":
              pat = 'pattern'
          f.write("        "+ InOrOut +"_pData[" + str(n) + "].plugin_data_setup( " + str(pat) + ", ' " + plugin_info['No. of frames, '+ InOrOut + ' plugin dataset ' + str(n+1)] + "')\n" )

      def change_to_index(self,indata):# recieves:  "data n out same as:" dataset y, returns: y-1 
           x,y = indata.split('dataset')
           Nin = str(int(y)-1)
           return Nin
         

  
      def write_template(self,plugin_info):
          modname = plugin_info["Plugin template name:"]
          modname = modname if len(modname.split('.py')) > 1 else modname + '.py'  # checks has .py format
          
          
          x,y = modname.split('.py')# checking that there isn't already a file with this name 
          original = x
          n = 1
          while os.path.isfile(modname) == True:
            modname = original + str(n) + '.py'
            n +=1
           
          with open(modname, 'a+') as f:
            
              self.add_on(f,'fixed_template_elements/copyright.py' )


              f.write('"""\n.. module::'+ plugin_info["Plugin template name:"])
              f.write('\n   :platform: Unix\n   :synopsis:\n.. moduleauthor::')
              f.write(plugin_info["Your name:"] + ' <' + plugin_info["Your e-mail:"] + '>\n\n"""\n')
              
              
              self.add_on(f,'fixed_template_elements/imports.py' )
               
              
              f.write('\nclass ' + plugin_info["Plugin class name:"] + '(Plugin, CpuPlugin):\n')
              
              
              self.add_on(f,'fixed_template_elements/description.py' )
                       
              
              f.write('\n    def __init__(self):')
              f.write('\n        super(' + plugin_info["Plugin class name:"])
              f.write( ', self).__init__("' + plugin_info["Plugin class name:"] + '")\n\n')   
              
              
              self.add_on(f,'fixed_template_elements/process_and_setup_intro.py')

              # creating the out  datasets 
              for n in range(0, int(plugin_info["Number of out datasets "])):
                  a= "data " + str(n +1) + " out same as:"
                  if plugin_info[a] == 'None':     
                      f.write("\n        out_dataset[" + str(n) + "].create_dataset() # shape, axis labels,... etc need to be added")                  
                  else :
                      f.write("\n        out_dataset[" + str(n) +  "].create_dataset(in_dataset[" + self.change_to_index(plugin_info[a]) + "])")  
                 
              
              f.write("\n\n        in_pData, out_pData = self.get_plugin_datasets()\n\n")
              
              for n in range(0, int(plugin_info["Number of in datasets "])): # creates the in plugin datasets 
                  self.pdata_setup(f, plugin_info,'in',n)
                  f.write('\n')
                  
              for n in range(0, int(plugin_info["Number of out datasets "])): # creates out plugin datasets 
                  self.pdata_setup(f, plugin_info,'out',n)    
                  f.write('\n')                  
         
            
              f.write("\n\n    def nInput_datasets(self):\n        return ")
              f.write( str(plugin_info["Number of in datasets "]))
      
              f.write("\n\n    def nOutput_datasets(self):\n        return ")
              f.write( str(plugin_info["Number of out datasets "]))

              
          f.close        
          print('done, go to :  '+ os.path.dirname(os.path.realpath(__file__)) + '/' + modname)
