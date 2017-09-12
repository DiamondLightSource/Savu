import QtQuick 2.6
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.3

ListModel{
    id: pg1_model  
    
    ListElement {
        label:"Plugin template name:"
        placeholder: "Must be of the form: plugin_name.py "
        ptype: 0
    }
    ListElement {
        label:"Plugin class name:"
        placeholder: "Must be of the form: PluginName "
        ptype: 0
    } 
    ListElement {
        label:"Your name:"
        placeholder: ""
        ptype: 0
    } 
    ListElement {
        label:"Your e-mail:"
        placeholder:""
        ptype: 0
    }     

    
}