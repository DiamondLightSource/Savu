
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
      timeline: { colorByRowLabel: false },
        backgroundColor: '#ffd',
        avoidOverlappingGridLines: true
        };

      var chart = new google.visualization.Timeline(document.getElementById('gantt_div'));
      chart.draw(dataTable, options);

    }
    </script>

    <div id="gantt_div">

    <style> #gantt_div {width:1300px; height:1000px;}

    '''
    return template_string
    
import pandas as pd
import numpy as np    

def convert(filename):
    
    the_key = ""#CPU0"
    the_interval = 50 # millisecs

    all_frames = []
    
    for files in filename:
        print files
        frame = get_frame(files, the_key)
        [index, nth] = get_index(frame)
        frame.Time_end[frame.index[np.cumsum(nth)-1]] = frame.Time.max()
        frame = frame.reset_index(drop=True)

        temp = pd.DataFrame(np.array(frame.Time_end - frame.Time), columns=['Time_diff'])
        temp['Key'] = frame.Key
        temp['index'] = [item for sublist in index for item in sublist]
        temp = temp.pivot(index='index', columns='Key', values='Time_diff')
        
        all_frames.append(temp)
    
    avg_duration = get_average_duration(all_frames)
    output_stats(all_frames, filename)

    frame.Time_end = avg_duration
    frame.Time = frame.Time_end.shift(1)
    frame.Time.iloc[0] = 0

    render_template(frame, the_interval, filename)
    
    return frame


def get_frame(file, the_key):
    names= ['L', 'Time', 'Machine', 'CPU', 'Type', 'Message']
    data = pd.io.parsers.read_fwf(file, widths=[2, 13, 5, 5, 6, 1000], names=names)
    data['Key'] = data['Machine'] + data['CPU']
    frame = ((data[data.Type == "DEBUG"])[data.columns[[6,5,1]]]).sort('Key')  
    
    frame = frame[frame.Key.str.contains(the_key)]
    frame.insert(3,"Time_end", frame.Time.shift(-1))
    frame.Message = frame.Message.str.strip('\n')
    frame.Message = frame.Message.str.replace("'","")
  
    return frame
    

def get_index(frame):
    nth = []
    index = []
    for i in range(np.size(frame.Key.unique())):
        nth.append(frame[frame.Key == frame.Key.unique()[i]].count()[0])
        index.append(range(nth[i]))
    
    return [index, nth]
    
    
def get_average_duration(frames):
    avg_frames = pd.Panel({n: df for n, df in enumerate(frames)})
    avg_frames = (avg_frames.mean(axis=0)).cumsum(0)
    avg_frames = avg_frames.as_matrix(columns=avg_frames.columns[:])
    avg_frames = np.reshape(np.transpose(avg_frames), np.prod(avg_frames.shape))
    avg_frames = avg_frames[~np.isnan(avg_frames)]

    return avg_frames


def render_template(frame, the_interval, filename):  
    from jinja2 import Template
    frame = frame[(frame.Time_end - frame.Time) > the_interval].values

    f_out = open(filename[0].split('.')[0] + '_avg' + `len(filename)` + '.html','w')
    print filename[0].split('.')[0] + '_avg' + `len(filename)` + '.html'
    template = Template(set_template_string(100))

    f_out.write(template.render(vals = map(list, frame[:,0:4])))    
    f_out.close()
    
    return frame
    
    
def output_stats(frames, filename):
    temp = []
    for frame in frames:
        temp.append(frame.max())
    
    total = pd.concat([i for i in temp], axis = 0)
    total_stats = total.describe()
    print total_stats  
    
    fname = filename[0].split('.')[0] + '_avg' + `len(filename)` + '_stats.csv'
    print filename[0].split('.')[0] + '_avg' + `len(filename)` + '_stats.csv'
    total_stats.to_csv(fname)

    return     
    
    
if __name__ == "__main__":
    import optparse
    usage = "%prog [options] input_file"
    parser = optparse.OptionParser(usage=usage)
    
    (options, args) = parser.parse_args()
    
    convert(args)

