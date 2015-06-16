
def set_template_string():

    template_string = '''
        <script type="text/javascript" src="https://www.google.com/jsapi?autoload={'modules':[{'name':'visualization',
       'version':'1','packages':['corechart']}]}"></script>

        <script type="text/javascript" src="http://canvg.googlecode.com/svn/trunk/rgbcolor.js"></script> 
        <script type="text/javascript" src="http://canvg.googlecode.com/svn/trunk/StackBlur.js"></script>
        <script type="text/javascript" src="http://canvg.googlecode.com/svn/trunk/canvg.js"></script>

        <script type="text/javascript">

        google.setOnLoadCallback(drawSeriesChart);

        function drawSeriesChart() {
    
        var data = google.visualization.arrayToDataTable([
        ['ID', 'Life Expectancy', 'Fertility Rate', 'Region',     'Population'],
        ['CAN',    80.66,              1.67,      'North America',  33739900],
        ['DEU',    79.84,              1.36,      'Europe',         81902307],
        ['DNK',    78.6,               1.84,      'Europe',         5523095],
        ['EGY',    72.73,              2.78,      'Middle East',    79716203],
        ['GBR',    80.05,              2,         'Europe',         61801570],
        ['IRN',    72.49,              1.7,       'Middle East',    73137148],
        ['IRQ',    68.09,              4.77,      'Middle East',    31090763],
        ['ISR',    81.55,              2.96,      'Middle East',    7485600],
        ['RUS',    68.6,               1.54,      'Europe',         141850000],
        ['USA',    78.09,              2.05,      'North America',  307007000]
      ]);

      var options = {
        title: 'Title?',
        hAxis: {title: 'Number of Nodes'},
        vAxis: {title: 'Number of Cores'},
        bubble: {textStyle: {fontSize: 11}}
      };

      var chart = new google.visualization.BubbleChart(document.getElementById('series_chart_div'));
      chart.draw(data, options);
    }
    </script>

    <div id="series_chart_div">

    <style> #gantt_div {width:500px; height:500px;}

    '''

    return template_string
    
    
def convert():
    import pandas as pd
    # calculate the mean and std

    for file in get_files():
        temp_frame = pd.read_csv(file)
        print type(temp_frame)
        print temp_frame
        

    frame = []
    
    render_template(frame)
    
    return 


def get_files():
    from os import listdir
    from os.path import isfile, join
    print("Testing get_files()")

    all_files = [ f for f in listdir('.') if isfile(join('.',f)) ]
    files = [f for f in all_files if "stats" in f]

    return files


def render_template(frame):  
    from jinja2 import Template

    f_out = open('bubble_test.html','w')
    template = Template(set_template_string())
    f_out.write(template.render(vals=frame))    
    f_out.close()
    
    return
    
    
if __name__ == "__main__":
    import optparse
    usage = "%prog [options] input_file"
    parser = optparse.OptionParser(usage=usage)
    
    (options, args) = parser.parse_args()
    
    convert()

  