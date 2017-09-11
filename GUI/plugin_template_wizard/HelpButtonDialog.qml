import QtQuick 2.6
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Layouts 1.3
import QtQuick.Dialogs 1.2

import '.'

MessageDialog {
    id: help_dialog
    title: 'Help'
    icon: StandardIcon.Question
    text: {
        
        if (n == 1){
          'Please input the pattern of the input plugin dataset, if passed from plugin select pass parameter.'    ;
        }else if (n== 2){
          'Please input the no of frames for the plugin dataset.';
        } else {
          'No documents selected.'    
        }
    } 
    standardButtons: StandardButton.Ok
    onAccepted : visible = false

} 