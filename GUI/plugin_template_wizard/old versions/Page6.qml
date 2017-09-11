import QtQuick 2.6
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.3


Screen {

    title: 'Review'
    hasNextButton: false


    CollectedInfo {// this is the list Model
        id: collected_info
    }


    TableView {
        anchors.fill: parent

        __verticalScrollBar.visible: false
        __horizontalScrollBar.visible: false              
        
        TableViewColumn{
            role : 'label'
            width: 300
        }
        TableViewColumn{
            role : 'input'
            width: 300
            //delegate: TextEdit {anchors.fill: parent}
        }              
      model: collected_info
    }
 
    
              
     

}
     
    