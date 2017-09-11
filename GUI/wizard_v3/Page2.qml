import QtQuick 2.6
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.3
import QtQuick.Dialogs 1.2

import '.'

Screen {

    title: 'Number of input and output datasets'
    
    signal noDatasets1(int INvalue)
    signal noDatasets2(int OUTvalue)

    Pg2Model {// list Model, contains content to fill delegate
        id: pg2_model
    }
    
    Component {
        id: pg2_model_Delegate
        
        RowLayout {
            id: row
            width: parent.width
            height: 30                      
            spacing: 50
                
            StandardTextLabel{}                 
            
            StandardTextField{
                id: textfield
                onTextChanged: {
                    if( isInt(parseInt(textfield.text))== true){ // checks if the input is an integer
                        if (n == 1){
                          noDatasets1(parseInt(textfield.text)); //  tells page 3 (in info)  how to populate 
                        }else {
                          noDatasets2(parseInt(textfield.text) )// tells page 4 (out info)
                        }
                    } else{
                        warning.visible = true  
                        void remove(0,1)// Removes inout if not an inetger     
                        // note: it cannot tell that the input contains a string if  it starts with an integer e.g 12g wouldn't raise an error  
                    }   
                    GModel.pluginInfo[label] = textfield.text;
                }
            }
                
            
            MessageDialog {
                id: warning
                title: 'Attention!'
                icon: StandardIcon.Warning
                text: 'Please input an integer'         
                standardButtons: StandardButton.Ok
                onAccepted : visible = false
            
            }
               
            function isInt(n){
                return n === +n && n === (n|0) && n != 0;
            }                  
        }
    }
    
    ListView {
        anchors.fill: parent
        model: pg2_model
        delegate: pg2_model_Delegate
    } 
}