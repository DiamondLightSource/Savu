import QtQuick 2.6
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.3


ListModel {
    id: collected_info
    ListElement{
        label: 'Plugin name'
        input: ''
    }
    ListElement{
        label: 'Class name'
        input: ''
    }

    ListElement{
        label: 'Your name'
        input: ''
    }

    ListElement{
        label: ' Your e-mail'
        input: ''
    }

    ListElement{
        label: 'No. of input datasets'
        input: ''
    }    
    
    ListElement{
        label: 'Pattern of input'
        input: ''
    }    
    
    ListElement{
        label: 'No. of output datasets'
        input: ''
    }  
   
    
    ListElement{
        label: 'pattern of output'
        input: ''
    }    
  
    ListElement{
        label: 'Shape change?'
        input: ''
    }
    
    ListElement{
        label: 'No. frames'
        input: ''
    }    
}    