import QtQuick 2.6
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Layouts 1.3
import QtQuick.Dialogs 1.2

import '.'

Rectangle {
    id: root
    width: 750
    height: 400 
    color: 'steel blue'


    property alias hasBackButton: backButton.visible
    property alias hasNextButton: nextButton.visible   
    property alias hasCreateButton: create.visible    
    property alias title: text.text

    default property alias children: columnlayout.data // each element of a page with screen as is a child of column layout 
    
    signal nextScreen()
    signal prevScreen()
    
    Text{
        id: text// title asigned in  page files
        text: ''
        font.bold : true
        font.pointSize : 15
        anchors{horizontalCenter: root.horizontalCenter; top: root.top; margins: 10 }
    }
    
    ColumnLayout {
        id: columnlayout
        anchors{fill: parent; margins: 40}

    }
        
    Button {
        id: nextButton
        text: 'Next'
        onClicked: nextScreen()
        style: StandardStyle{}
        anchors{bottom: root.bottom; right: root.right; margins: 10}
    }         
    Button {
        id: backButton
        text: 'Back'
        onClicked: prevScreen()
        style: StandardStyle{}
        anchors{bottom: root.bottom; left: root.left; margins: 10}
    }       
    Button {
        id: create
        text: "Create template"
        onClicked: createTemplate(GModel.pluginInfo)
        style: StandardStyle{}
            
        anchors{bottom: root.bottom; right: root.right; margins: 10}
        visible: false 
    }        
}