pragma Singleton
import QtQuick 2.6
// this is where the user input is stored 
Item {
    property var pluginInfo: {
        "Plugin template name:" : 'plugin_name',
        "Your name:" : 'Developer name',
        "Your e-mail:" : '@diamond.ac.uk',
        "Number of in datasets " : '1' ,
        "Number of out datasets " : '1' ,
        "pre-processing selection:" : 'pass',
        "processing" : 'pass',
        "post-processing selection:" : 'pass'
    }
}
    
