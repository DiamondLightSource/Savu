import os 

class Template:

  
      def add_on(self,f,openfile):# adds openfile onto main file f 
          with open(openfile) as input:
            f.write(input.read())
            input.close        
            
      def pdata_setup(self, f,plugin_info,InOrOut,n ): # maybe would be better if didnt input f and plugin_info
          patternN =  InOrOut + ' plugin pattern ' + str(n +1) 
          pat = "'" + plugin_info[patternN] + "'"
          if pat == "'pass as parameter'":
              pat = 'pattern'
          f.write("        "+ InOrOut +"_pData[" + str(n) + "].plugin_data_setup( " + str(pat) + "," + plugin_info['No. of frames, '+ InOrOut + ' plugin dataset ' + str(n+1)] + ')\n' )

      def change_to_dataset(self,indata):
           x,y = indata.split('dataset')
           y = int(y)
           Nin = str(y-1)
           return Nin
         
        
      
      def write_template(self,plugin_info):

          modname = plugin_info["Plugin template name:"]
          modname = modname if len(modname.split('.py')) > 1 else modname + '.py'  # checks has .py format
           
          with open(modname, 'a+') as f:
            
              self.add_on(f,'copyright.py' )

              f.write('"""\n.. module::'+ plugin_info["Plugin template name:"])
              f.write('\n   :platform: Unix\n   :synopsis:\n.. moduleauthor::' + plugin_info["Your name:"] + ' <' + plugin_info["Your e-mail:"] + '>\n\n"""\n')
              
              self.add_on(f,'imports.py' )
               
              f.write('\nclass ' + plugin_info["Plugin class name:"] + '(Plugin, CpuPlugin):\n')
              
              self.add_on(f,'description.py' )
                       
              f.write('\n    def __init__(self):')
              f.write('\n        super(' + plugin_info["Plugin class name:"] + ', self).__init__("' + plugin_info["Plugin class name:"] + '")\n\n')   
              
              self.add_on(f,'process_and_setup_intro.py')

              for n in range(0, int(plugin_info["Number of in datasets "])):  # creates the out  datasets 
                  if plugin_info["data 1 out same as:"] == 'None':     
                      f.write("\n        out_dataset[" + str(n) + "].create_dataset()")# shape, axis labels,... etc                   
                  else :
                      a= "data " + str(n +1)+ " out same as:"

                  f.write("\n        out_dataset[" + str(n) +  "].create_dataset(in_dataset[" + self.change_to_dataset(plugin_info[a]) + "])")  
                 
              
              f.write("\n\n        in_pData, out_pData = self.get_plugin_datasets()\n\n")
              
              for n in range(0, int(plugin_info["Number of in datasets "])): # creates the in and out plugin datasets 
                  self.pdata_setup(f, plugin_info,'in',n)
                  self.pdata_setup(f, plugin_info,'out',n)
                  f.write('\n')
         
            
              f.write("\n\n    def nInput_datasets(self):\n        return " + str(plugin_info["Number of in datasets "]))
      
              f.write("\n\n    def nOutput_datasets(self):\n        return " + str(plugin_info["Number of out datasets "]))# the base dictionary doesnt like the out datasets entry ??? 

              
          f.close        
          print 'done, go to :  '+ os.path.dirname(os.path.realpath(__file__)) + '/' + modname
