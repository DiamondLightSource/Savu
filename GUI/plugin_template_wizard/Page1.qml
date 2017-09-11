import QtQuick 2.6
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.3
import QtQuick.Dialogs 1.2

import '.'

Screen {
    
    title: 'User information'
    hasBackButton: false
                
    Pg1Model{
        id: pg1_model    // loads in the model(content) of the page, which will populate the Delegate component
    }
      
    Component{// describes the frame(delegate) that the model will fill
        id: pg1_model_Delegate

        RowLayout{
            id: row
            width: parent.width
            height: 30                      
            spacing: 50
            
            Text { // StandardTextLabel in other pages  left in long form here so it is easy to see what it's doing ???????
                id : textLabel
                  Layout.fillWidth: true
                  height: parent.height
                  verticalAlignment: Text.AlignVCenter
                  visible: ptype == 0 
                  text: label // label is a property of the model 
            }   
            TextField {// SatndardTextField on other pages 
                  id: textfield
                  implicitWidth: 300
                  height: parent.height                    
                  placeholderText: placeholder //property of the model ( gives a text hint to the user, visible before they inout anything )
                  onTextChanged: {
                      GModel.pluginInfo[label] = textInput.text;
                  }
            }
        }
    }
            
    ListView {// this combines the model with the frame(delegate) defined in component 
        anchors.fill: parent
        model: pg1_model
        delegate: pg1_model_Delegate                      
    }
}                      
    
////// INFO ON PTYES//////
/*
ptype: 0  is a text field
ptype: 1  is a combo box
ptype: 2  is a title text label 
*/
///////////////////////////    