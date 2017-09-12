import QtQuick 2.6
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.3
import QtQuick.Dialogs 1.2


import '.'

Screen {

    title: 'Out datasets'
    
    Component {
        id: pg4_model_Delegate
            

        RowLayout {
            id: row
            width: parent.width
            height: 30                      
            
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
                onPressedChanged: {
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
            
            HelpButton{ // Stored in a separate file 
                id: help_button
            }
            
            HelpButtonDialog{
                id: help_dialog
                text:{
                    if (n == 2){
                      "Select an in dataset to match the current out dataset with. If it doesn't match any selcet None."   ;
                    }else if (n== 3){
                      "Please input the pattern of the out plugin dataset, if passed from plugin select pass parameter." ;
                    }else if (n==4){
                      "Please input the no of frames for the plugin dataset."
                    }else {
                      'No documents selected.'    
                    }
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
        }
    }        
    
    ListView {
        anchors.fill: parent
        anchors.rightMargin: 10
        model: page4Model
        delegate: pg4_model_Delegate
    }
    
    ListModel {
        id: page4Model
    }

    // function to create a model with the number of elements determined by user input 
    function addOutElements(n) {
        page4Model.clear();
        
        // The following creates a list of the possible in datasets an out dataset can match to, also gives the option to match to none.
        var same_as = []; 
        var nIN = parseInt(GModel.pluginInfo["Number of in datasets "]) +1;
        for ( var i = 1; i < nIN; i++ ) {
            same_as.push({text: 'dataset ' + i }); // adds elements to the list
        } 
        same_as.push({text: 'None'})    
        
        for ( var i = 0; i < n; i++ ) {
            page4Model.append({label: 'Out dataset ' + (i+1), ptype: 2, combo_options: [], placeholder: '', n: 1});
            page4Model.append({label: 'data '+ (i+1) + ' out same as:', ptype:1, combo_options: same_as, placeholder: '', n:2}) 
            page4Model.append({label: 'out plugin pattern ' + (i+1), ptype:1, combo_options:[{text: 'SINOGRAM'},{text: 'PROJECTION'},{text:'TIMESERIES'},{text:'pass as parameter'}], placeholder: '',n:3})
            page4Model.append({label: 'No. of frames, out plugin dataset ' + (i+1), ptype:1, combo_options: [{text: 'single'},{text: 'multiple'}, {text: 'int'}], placeholder: 'Please input an integer', n:4})
        }
    }
    Component.onCompleted: addOutElements(1)        
}        
      
      