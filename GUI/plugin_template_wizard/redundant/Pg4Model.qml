import QtQuick 2.6
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.3


ListModel{
    id: pg4_model
    
    ListElement{
        label: "Out dataset 1"
        placeholder: ''
        ptype: 2
        option1: ''
        option2: ''
        option3: ''
        option4: ''
        n: 1           
        
    }

    ListElement{
        label:"data 1 out same as:"// same what ?????? i.e create dataset(in_dataset[0])
        placeholder: ''
        ptype: 1
        option1: 'dataset 1'
        option2: 'dataset 2'
        option3: 'dataset 3' // these will as blank options, could be clicked !!!!! 
        option4: 'No'
        n: 2    
    }   

    ListElement{
        label:"out plugin pattern 1" // pattern of plugin data set out_pdata  MAYBE say out plugin dataset pattern ?
        placeholder: ''
        ptype: 1
        option1: 'pass as parameter'
        option2: 'SINOGRAM'
        option3: 'PROJECTION'
        option4: 'TIMESERIES'
        n: 3    
    }  
    ListElement{
        label: "No. of frames, out dataset 1"
        placeholder: 'Please input an integer'
        ptype: 1
        option1: "'single'"
        option2: "'multiple'"
        option3: 'int'
        option4:''
        n:4
    }
        
    ListElement{
        label: "Out dataset 2"
        placeholder: ''
        ptype: 2
        option1: ''
        option2: ''
        option3: ''
        option4: ''
        n: 5       
        
    }

    ListElement{
        label:"data 2 out same as:"
        placeholder: ''
        ptype: 1
        option1: 'dataset 1'// (pattern in 1) note: this wold effect the spliting in template 
        option2: 'dataset 2'
        option3: 'dataset 3' // these will as blank options, could be clicked !!!!! 
        option4: 'No'
        n: 6   
    }   


    ListElement{
        label:"out plugin pattern 2"
        placeholder: ''
        ptype: 1
        option1: 'pass as parameter'
        option2: 'SINOGRAM'
        option3: 'PROJECTION'
        option4: 'TIMESERIES'
        n: 7
    }  
    ListElement{
        label: "No. of frames, out dataset 2"
        placeholder: 'Please input an integer'
        ptype: 1
        option1: "'single'"
        option2: "'multiple'"
        option3: "'int'"
        option4:''
        n:8
    }    
      
/*    ListElement{
        label:"Has the shape of the data changed? "
        placeholder: ''
        ptype: 1
        option1: 'Yes'
        option2: 'No'
        option3: ''
        option4: ''
        n: 8   
    } */      
    
}