import QtQuick 2.6
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Layouts 1.3
import QtQuick.Dialogs 1.2

import '.'


Screen {

    title: 'Input data'

    Component {
        id: multi_in_infoDelegate
        
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
                onCurrentIndexChanged: {
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
            }

            
            MessageDialog {
                id: warning
                title: 'Attention!'
                icon: StandardIcon.Warning
                text: 'Please input an integer'         
                standardButtons: StandardButton.Ok
                onAccepted : visible = false
            }
            
            ListModel {
                id: combo_model    
            }
        }
    }

    ScrollView {
      anchors.fill: parent
      frameVisible: false
      ListView {
        anchors.fill: parent
        anchors.rightMargin: 10
        model: myModel
        delegate: multi_in_infoDelegate
      }    
    }
        
    ListModel {
        id: myModel
    }
       
    function addInElements(n) {
        myModel.clear();
        for ( var i = 0; i < n; i++ ) {
            //var mylist = [{text: "option1"}, {text:"option2"}];
            myModel.append({label: 'in dataset' + (i+1), ptype: 2, n: 0, combo_options : [], placeholder: ''});
            myModel.append({label: 'in plugin pattern '+ (i+1), ptype: 1, n: 1, combo_options: [{text: 'SINOGRAM'},{text: 'PROJECTION'},{text:'TIMESERIES'},{text:'pass as parameter'}], placeholder: '' });
            myModel.append({label:'No. of frames, in plugin dataset '+ (i+1), ptype: 1, n:2, combo_options: [{text: 'single'},{text: 'multiple'}, {text: 'int'}], placeholder:'Please input an integer'});           // 'single','multiple', 'int' 
        }
    }
    Component.onCompleted: addInElements(1)// creates a model to use before user input     
}        



