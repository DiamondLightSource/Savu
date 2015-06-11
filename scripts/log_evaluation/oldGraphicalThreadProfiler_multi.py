
def set_template_string(chart_width):
    template_string = '''
        <script type="text/javascript" src="https://www.google.com/jsapi?autoload={'modules':[{'name':'visualization',
       'version':'1','packages':['timeline']}]}"></script>

        <script type="text/javascript" src="http://canvg.googlecode.com/svn/trunk/rgbcolor.js"></script> 
        <script type="text/javascript" src="http://canvg.googlecode.com/svn/trunk/StackBlur.js"></script>
        <script type="text/javascript" src="http://canvg.googlecode.com/svn/trunk/canvg.js"></script>

        <script type="text/javascript">

        google.setOnLoadCallback(drawChart);

        function drawChart() {
        var dataTable = new google.visualization.DataTable();
        dataTable.addColumn({ type: 'string', id: 'Room' });
        dataTable.addColumn({ type: 'string', id: 'Name' });
        dataTable.addColumn({ type: 'number', id: 'Start' });
        dataTable.addColumn({ type: 'number', id: 'End' });
        dataTable.addRows([
        {% for val in vals %}
        [ '{{val[0]}}' , '{{val[1]}}', {{val[2]}}, {{val[3]}} ], 
         {% endfor %}
         ]);

      var options = {
      timeline: { colorByRowLabel: true },
        backgroundColor: '#ffd'
        };

      var chart = new google.visualization.Timeline(document.getElementById('gantt_div'));
      chart.draw(dataTable, options);

    }
    </script>

    <div id="gantt_div">

    <style> #gantt_div {width:1000px; height:1000px;}

    '''
    return template_string
    

def convert(filename):
    from jinja2 import Template
    import sys
    import pandas

    machine_out = ""#CPU0"

    threads = {}

    print("***",sys.argv)

    print type(sys.argv)
    
    
    ff = open(filename, 'r')
    
    for line in ff:         
        s = line.split()
        key = s[2]+s[3]
        if not threads.has_key(key):
            threads[key] = []
        if "DEBUG" in s[4]:
            threads[key].append((s[1], line.split(s[4])[1] ) )
            
    test = []

    kk = threads.keys()
    kk.sort()
    idx = -1
    for key in kk:
        idx+=1
        if machine_out in kk[idx]:
            timeShift = int(threads[key][0][0])
            for i in range(len(threads[key])-1):
                try :
    #                test.append(( key, threads[key][i][1].strip().replace("'",""),
    #                    'new Date(0,0,0,%d,%d,%d,%d)'%(get_time(int(threads[key][i][0])-timeShift)),
    #                    'new Date(0,0,0,%d,%d,%d,%d)'%(get_time(int(threads[key][i+1][0])+1-timeShift))))
                    test.append(( key, threads[key][i][1].strip().replace("'",""),
                        int(threads[key][i][0])-timeShift, int(threads[key][i+1][0])+1-timeShift))
                except:
                    print "Failed to work with line"
                    print threads[key][i]

    f_out = open(filename+'.html','w')
    template = Template(set_template_string(100))
    f_out.write(template.render(vals=test))
    f_out.close()

    return test

    
    
def get_time(ms):
    
    s,ms = divmod(ms,1000)
    m,s = divmod(s,60)
    h,m = divmod(m,60)
    d,h = divmod(h,24) 
    
    return h,m,s,ms
    
    
if __name__ == "__main__":
    import optparse
    usage = "%prog [options] input_file"
    parser = optparse.OptionParser(usage=usage)
    
    (options, args) = parser.parse_args()
    
    convert(args[0])

