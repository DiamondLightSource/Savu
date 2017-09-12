import QtQuick 2.6
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.3

import '.'

ApplicationWindow {


    width: 500
    height: 600
    
    signal createTemplate(variant value)
    
    ColumnLayout {
          anchors.fill: parent
          anchors.margins: 10
          
          Content{// this is a list Model, contains info about the different categories saved as Content.qml (in same folder)
              id: content
          }
      
          Component {//  the model information will be passed into this 
              id: contentDelegate
              RowLayout {
                  width: parent.width
                  height: 30                      
                  spacing: 50
                  
                  StandardTextLabel {}
                  
                  StandardTextField {
                      id: textfield
                      onTextChanged: GModel.pluginInfo[label] = textinput.text
                  }
                  
                  StandardComboBox { 
                      id: combo
                      onCurrentIndexChanged: GModel.pluginInfo[label] = combo.currentText
                  }
              }
          }
               
      
          ListView {// this combines the model in Content with the info in component 
              anchors.fill: parent
              model: content
              delegate: contentDelegate
          }
          Button {// the second object in the colum layout is the button which conects to .py and ceates template 
              id:butn1
              activeFocusOnPress: true
              text: "Create template"
              onClicked: createTemplate(GModel.pluginInfo)
          }        
    }
}              