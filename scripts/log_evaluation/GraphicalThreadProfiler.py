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

#    read_lines = 2000
#    with open(filename, 'r') as ff:
#        for _ in range(read_lines):
#            line = ff.readline()
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
    for key in kk:
        timeShift = int(threads[key][0][0])
        for i in range(len(threads[key])-1):
            try :
                test.append(( key, threads[key][i][1].strip().replace("'",""),
                    'new Date(0,0,0,%d,%d,%d,%d)'%(get_time(int(threads[key][i][0])-timeShift)),
                    'new Date(0,0,0,%d,%d,%d,%d)'%(get_time(int(threads[key][i+1][0])+1-timeShift))))
            except:
                print "Failed to work with line"
                print threads[key][i]

    f2 = open(filename+'.html','w')

    template = Template(template_string)
    f2.write(template.render(vals=test))

    f2.close()
        
    return test


def evaluate(selected_data):
    starts = selected_data[selected_data[5].str.startswith("Start::")]
    ends = selected_data[selected_data[5].str.startswith("Finish::")]

    summed = {}
    count = {}

    for i in range(len(starts)):
        start = starts[i:i+1]
        aa = ends[ends[1] >= start[1].base[0]]
        key = start[5].base[0].split("Start::")[1].strip()
        end = aa[aa[5].str.contains(key)]
        if key not in summed:
            summed[key] = 0
            count[key] = 0
        elapsed = end[1].base[0] - start[1].base[0]
        summed[key] += elapsed
        count[key] += 1
    return (summed, count)
    
    
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

