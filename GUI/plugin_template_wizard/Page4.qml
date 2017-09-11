import QtQuick 2.6
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.3
import QtQuick.Dialogs 1.2


import '.'

Screen {

    title: 'Out data'
    
    Component {
        id: pg4_model_Delegate
            

        RowLayout {
            id: row
            width: parent.width
            height: 30                      
            spacing: 50
            
            StandardTextLabel{ 
                  font.bold: ptype == 2
            }     
            
            StandardTextField{
                id: textfield
                onTextChanged: {
                    if( isInt(parseInt(textfield.text))== true){ // check if the iput is an integer
                        noDatasets(parseInt(textfield.text)); // sends a signal thats tells the next page how to populate 
                    } else{
                        warning.visible = true 
                        void remove(0,1) 
                    }   
                    GModel.pluginInfo[label] = textfield.text;
                }                 
            }
            
            StandardComboBox{
                id: combo
                onCurrentIndexChanged: {
                    GModel.pluginInfo[label] =  combo.currentText;
                    if( combo.currentText == 'int'){
                        textfield.visible = true // if integer no. of max frames is selected a text input box becomes visible note: can't come back from this 
                        // having a textfield  appear below, can't communicate between delegate objects => can't tell it to appear ??
                        combo.visible = false  
                    }
                }    
            }  
                    
            function isInt(n){
                return n === +n && n === (n|0) && n != 0;
            }               
            
            MessageDialog {
                id: warning
                title: 'Attention!'
                icon: StandardIcon.Warning
                text: 'Please input an integer'         
                standardButtons: StandardButton.Ok
                onAccepted : visible = false
            }
        }
    }        
    
    ListView {
        anchors.fill: parent
        model: mymodel4
        delegate: pg4_model_Delegate
    }
    
    ListModel {
        id: mymodel4
    }

    // function to create a model with the number of elements determined by user input 
    function addOutElements(n) {
        mymodel4.clear();
        
        // The following creates a list of the possible in datasets an ot dataset can match to, also gives the option to match to none.
        var same_as = []; 
        var nIN = parseInt(GModel.pluginInfo["Number of in datasets "]) +1;
        for ( var i = 1; i < nIN; i++ ) {
            same_as.push({text: 'dataset ' + i }); // adds elements to the lsit
        } 
        same_as.push({text: 'None'})    
        
        for ( var i = 0; i < n; i++ ) {
            mymodel4.append({label: 'Out dataset ' + (i+1), ptype: 2, combo_options: [], placeholder: ''});
            mymodel4.append({label: 'data '+ (i+1) + ' out same as:', ptype:1, combo_options: same_as, placeholder: ''}) 
            mymodel4.append({label: 'out plugin pattern ' + (i+1), ptype:1, combo_options:[{text: 'SINOGRAM'},{text: 'PROJECTION'},{text:'TIMESERIES'},{text:'pass as parameter'}], placeholder: ''})
            mymodel4.append({label: 'No. of frames, out plugin dataset ' + (i+1), ptype:1, combo_options: [{text: 'single'},{text: 'multiple'}, {text: 'int'}], placeholder: 'Please input an integer'})
        }
    }
    Component.onCompleted: addOutElements(1)        
}        
      
      