import QtQuick 2.6
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.3


ListModel {
    id: content

    ListElement {
        label:"plugin template name:"
        placeholder: "Must be of the form: plugin_template "
        ptype: 0
        //combo_options: ''

    }
    
    ListElement {
        label: "Your name:"
        placeholder: ""
        ptype: 0
    }   
    
    ListElement {
        label: "Your e-mail:"
        placeholder: ""
        ptype: 0
    }
    
    ListElement {
        label: "pre-processing selection:"
        placeholder: ""
        ptype:1
    }
    
    ListElement {
        label: "processing"
        placeholder: ""
        ptype:1
    }
    
    ListElement {
        label: "post-processing selection:"
        placeholder: ""
        ptype:1
    }
    
    ListElement {
        label: "No. of inputs:"
        placeholder: ""
        ptype: 0
    }    
    
    ListElement {
        label: "No. of outputs:"
        placeholder: ""
        ptype: 0
    } 
}
    
