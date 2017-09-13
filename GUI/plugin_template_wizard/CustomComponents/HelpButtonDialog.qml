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
    text: "" 
    standardButtons: StandardButton.Ok
    onAccepted : visible = false

} 