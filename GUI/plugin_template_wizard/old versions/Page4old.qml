import QtQuick 2.6
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.3

Screen {

    title:'Number of output datasets'
    hasCreateButton: false        
    
    NoOut{
        id: no_out
    }
    Component {
        id: no_out_Delegate
        
        
        RowLayout {
            id: row
            width: parent.width
            height: 30                      
            spacing: 50
            
            
            Text { 
                  Layout.fillWidth: true
                  height: parent.height
                  verticalAlignment: Text.AlignVCenter
                  text:label
                  
            }                      
            
            TextField {
                  id: textfield
                  implicitWidth: 300
                  height: parent.height
                  placeholderText: placeholder
                  onTextChanged: {
                      if( isInt(parseInt(textfield.text))== true){
                          noDatasets(parseInt(textfield.text));
                      } else{
                          console.log('please input an integer') ;
                      }   
                      pluginInfo(label,text)

                  }                  
            }
            function isInt(n){
                return n === +n && n === (n|0) && n != 0;
            }                      
            
        }
    }     


    ListView {
        anchors.fill: parent
        model: no_out
        delegate: no_out_Delegate
    }
    
          
}     
    
    
