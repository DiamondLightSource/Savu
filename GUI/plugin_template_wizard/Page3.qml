import QtQuick 2.6
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Layouts 1.3
import QtQuick.Dialogs 1.2

import '.'


Screen {

    title: 'In datasets'

    Component {
        id: page3_model_Delegate
        
        RowLayout {
            id: row
            width: parent.width
            height: 30                      
            
            StandardTextLabel{ 
                  font.bold: ptype == 2 // if not a text box or dropdown its a title 
            }  
            
            StandardTextField{
                id: textfield
                onTextChanged: {
                    if( isInt(parseInt(textfield.text))== true){ // check if the input is an integer
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
                onPressedChanged: { // HAVE TO ACTUALLY CLICK ON THE DROP DOWN EVEN IF THE ONE SHOWING IS THE ONE YOU WANT 
                    GModel.pluginInfo[label] =  combo.currentText;
                    if( combo.currentText == 'int'){
                        textfield.visible = true 
                        combo.visible = false  ;
                    }
                }
            }
            
            function isInt(n){
                return n === +n && n === (n|0) && n != 0;
            }   
            
            HelpButton{ 
                id: help_button
            }
            
            HelpButtonDialog{
                id: help_dialog
                text:{
                    if (n == 1){
                      'Please input the pattern of the in plugin dataset, if passed from plugin select pass parameter.'    ;
                    }else if (n== 2){
                      'Please input the no. of frames for the plugin dataset.';
                    } else {
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

    ScrollView { // adds a scroll bar if The no. of datasets means list is longer than window
      anchors.fill: parent
      frameVisible: false
      ListView {
        anchors.fill: parent
        anchors.rightMargin: 10
        model: myModel
        delegate: page3_model_Delegate
      }    
    }
        
    ListModel {
        id: myModel
    }
       
    function addInElements(n) {
        myModel.clear();
        for ( var i = 0; i < n; i++ ) {
            myModel.append({label: 'in dataset' + (i+1), ptype: 2, n: 0, combo_options : [], placeholder: ''});
            myModel.append({label: 'in plugin pattern '+ (i+1), ptype: 1, n: 1, combo_options: [{text: 'SINOGRAM'},{text: 'PROJECTION'},{text:'TIMESERIES'},{text:'pass as parameter'}], placeholder: '' });
            myModel.append({label:'No. of frames, in plugin dataset '+ (i+1), ptype: 1, n:2, combo_options: [{text: 'single'},{text: 'multiple'}, {text: 'int'}], placeholder:'Please input an integer'});           // 'single','multiple', 'int' 
        }
    }
    Component.onCompleted: addInElements(1)// creates a model to use before user input     
}        



