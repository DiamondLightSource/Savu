import QtQuick 2.6
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.3
import QtQuick.Dialogs 1.2

import '.'


TextField {
      id: textfield
      implicitWidth: 300
      height: parent.height
      visible: ptype == 0  // will appear if ptype property in model = 0
      placeholderText: placeholder
}      