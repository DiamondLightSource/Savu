import QtQuick 2.6
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Layouts 1.3
import QtQuick.Dialogs 1.2

import '.'

ComboBox { 
  id: combo
  textRole: "text"
  implicitWidth: 300
  height: parent.height
  visible : ptype == 1 
  //style : ComboBoxStyle{}
  model: [{text:'pass'},{text: 'process'}]
}
  
