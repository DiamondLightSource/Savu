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
  dataTable.addColumn({ type: 'date', id: 'Start' });
  dataTable.addColumn({ type: 'date', id: 'End' });
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

<div id="gantt_div" style="width: 10000px; height: 2000px;"></div>
'''

def convert(filename):
    from jinja2 import Template

    threads = {}

    ff = open(filename, 'r')
    for line in ff:
        #print(line)
        s = line.split()
        key = s[1]
        print(key)
        if not threads.has_key(key):
            threads[key] = []
        threads[key].append( (s[0].split(':') , line.split(s[2])[1] ) )

    test = []

    kk = threads.keys()
    kk.sort()
    for key in kk:
        print key
        for i in range(len(threads[key])-1):
            try :
                print 'p  %s' % (threads[key][i][1].strip())
                test.append(( key, threads[key][i][1].strip(),
                    'new Date(0,0,0,%s,%s,%s,%s)'%(threads[key][i][0][0],threads[key][i][0][1],threads[key][i][0][2].split('.')[0], threads[key][i][0][2].split('.')[1]),
                    'new Date(0,0,0,%s,%s,%s,%d)'%(threads[key][i+1][0][0],threads[key][i+1][0][1],threads[key][i+1][0][2].split('.')[0], int(threads[key][i+1][0][2].split('.')[1])+1) ))
            except:
                print "Failed to work with line"
                print threads[key][i]

    f2 = open(filename+'.html','w')

    template = Template(template_string)
    f2.write(template.render(vals=test))

    f2.close()
    
    return test


if __name__ == "__main__":
    import optparse
    usage = "%prog [options] input_file"
    parser = optparse.OptionParser(usage=usage)
    
    (options, args) = parser.parse_args()
    
    convert(args[0])

