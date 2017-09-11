import QtQuick 2.6
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.3
import QtQuick.Dialogs 1.2

import '.'

ApplicationWindow {

    id: mainWindow
    title: 'Savu plugin template auto-creation ' 

    width: 750
    height: 400

    signal createTemplate(variant value)


    Rectangle {
        id: top 
        width: 750
        height: 400

        StackLayout {
          id: handler
          anchors.fill : parent
          currentIndex : 0

          // All the pages are loaded, the current index determines which is shown 
          
          Page1 {
              id: page1
              onNextScreen : handler.currentIndex += 1
          }
          
          Page2 {
              id: page2
              onNextScreen : handler.currentIndex += 1
              onPrevScreen :handler.currentIndex -= 1
            
              onNoDatasetsIn : page3.addInElements(INvalue)//tells page 3 how many in datasets, calls function that creates a model based no. in 
              onNoDatasetsOut : page4.addOutElements(OUTvalue) //tells page 3 how many out datasets  
          }
              
          Page3 {
              id: page3
              onNextScreen : handler.currentIndex += 1
              onPrevScreen :handler.currentIndex -= 1
          }     
              
          Page4 {
              id: page4
              onNextScreen : {
                  handler.currentIndex += 1;
                  page5.updateModel();
              }              
              onPrevScreen :handler.currentIndex -= 1
          } 
              
          Page5 {
              id: page5
              onPrevScreen :  handler.currentIndex -= 1
            
          } 
       }
    }
}                
