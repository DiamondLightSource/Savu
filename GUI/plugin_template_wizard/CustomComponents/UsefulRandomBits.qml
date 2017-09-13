Material.primary: Material.Indigo;
Material.accent: Material.Turquoise;
// if updated to QtQuick.Controls 2, this would change the style of the GUI


signal params(var values)

params({
    value1: 10,
    value2: 50
})  
    // passes a dictionary 



 onParams : function(params) {
    console.log(JSON.stringify(params));
}
          
Component.onCompleted : {  //shows firsrt time completed 
    console.log(JSON.stringify(GModel.pluginInfo));
}   