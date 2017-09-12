import QtQuick 2.6
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Layouts 1.3
import QtQuick.Dialogs 1.2

import '.'

  
ButtonStyle {
    background: Rectangle {
        implicitWidth : 70
        border.width: control.activeFocus ? 2 : 1
        border.color: "#888"
        radius : 4 
        gradient: Gradient {
            GradientStop { position: 0 ; color: control.pressed ? "#ccc" : "#eee" }
            GradientStop { position: 1 ; color: control.pressed ? "#aaa" : "#ccc" }
        } // create a qml file lwith this in 
    }
} 
         