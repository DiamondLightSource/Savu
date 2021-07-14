
def set_template_string_multi(chart_width):

    pos = [16, 9]

    template_string = '''
        <html>
        <head>
        <link rel="stylesheet" type="text/css" href="{{style_sheet}}">

        <script src="https://www.gstatic.com/charts/loader.js"></script>
        <script type="text/javascript" src="http://canvg.googlecode.com/svn/trunk/rgbcolor.js"></script>
        <script type="text/javascript" src="http://canvg.googlecode.com/svn/trunk/StackBlur.js"></script>
        <script type="text/javascript" src="http://canvg.googlecode.com/svn/trunk/canvg.js"></script>
        <script type="text/javascript">

        google.setOnLoadCallback(drawChart);

        function drawChart() {
        var dataTable = new google.visualization.DataTable();
        dataTable.addColumn({ type: 'string', id: 'Core' });
        dataTable.addColumn({ type: 'string', id: 'Message' });
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

    {% set position = ''' + str(pos) + ''' %}
    <div id="gantt_div" style="position: absolute; left: {{position[0]}}%; top:{{position[1]}}%;
        width: ''' + str(chart_width) + '''px; height: 1000px;"></div>


    </head>
    <body>
        <h1> Savu MPI performance tests </h1>
        <div class="boxedLink">
            {% for link in links %}
            <br>Run {{loop.index}} : <a href={{link}}>here</a></br>
            {% endfor %}
        </div>
    </body>
    </html>
    '''
    return template_string


def set_template_string_vis(nVals, title, size, params, header_shift):
    import numpy as np

    total_size = list(size[0])
    total_size[1] = total_size[1]
    sub_size = list(size[1])

    plot_per_x = (1 if nVals == 1 else 2)
    nSubplots = int(np.ceil(float(nVals)/plot_per_x))*plot_per_x

    size = [total_size[0]/plot_per_x, total_size[1]/(nSubplots/plot_per_x)]
    size = [size[i]*(sub_size[i]/100.0) for i in range(len(size))]

    start = [(100 - t)/2 for t in total_size]
    gap_x = (total_size[0] - plot_per_x*size[0])/2
    gap_y = (total_size[1] - (nSubplots/plot_per_x)*size[1])/2

    right = [(start[0] + (i*2 + 1)*gap_x + i*size[0]) for i in range(plot_per_x)]*(nSubplots/plot_per_x)
    top = [(start[1] + (i*2 + 1)*gap_y + i*size[1] + header_shift) for i in range(plot_per_x)]
    top = np.reshape(np.transpose(np.tile(np.asarray(top), (nSubplots/plot_per_x, 1))), nSubplots).tolist()

    data_names = []
    chart_names = []
    for i in range(nVals):
        data_names.append('data' + str(i))
        chart_names.append('chart' + str(i))

    chartsize = [85 for s in size]

    template_string = '''
        <html>
        <head>
         <link rel="stylesheet" type="text/css" href="{{style_sheet}}">

        <title> Savu MPI performance tests </title>

        <script src="https://www.gstatic.com/charts/loader.js"></script>
        <script type="text/javascript" src="http://canvg.googlecode.com/svn/trunk/rgbcolor.js"></script>
        <script type="text/javascript" src="http://canvg.googlecode.com/svn/trunk/StackBlur.js"></script>
        <script type="text/javascript" src="http://canvg.googlecode.com/svn/trunk/canvg.js"></script>
        <script type="text/javascript">
        google.setOnLoadCallback(drawSeriesChart);

        function drawSeriesChart() {
            {% set title = ''' + str(title) + ''' %}

            {% for vals in frame %}
            var data{{loop.index0}} = google.visualization.arrayToDataTable([
            ['file system', '#Cores', 'Time (mean)', '#Nodes', 'Time (std)', 'link'],
              {% for val in vals %}
                [ '', {{val[1]}}, {{val[2]}}, {{val[3]}}, {{val[4]}}, '{{val[5]}}'],
              {% endfor %}
            ]);

        var view{{loop.index0}} = new google.visualization.DataView(data{{loop.index0}});
        view{{loop.index0}}.setColumns([0, 1, 2, 3, 4]);


        var options{{loop.index0}} = {
        {% set chartsize = ''' + str(chartsize) + '''%}
        chartArea: {'width': '{{chartsize[0]}}%', 'height': '{{chartsize[1]}}%'},
        colorAxis: {colors: ['yellow', 'red']},
        title: '{{title[loop.index0]}}',
        titleTextStyle: {fontSize: '15'},
        hAxis:
	  {
          title: 'Total cores',
          titleTextStyle: {fontSize: '15'},
          viewWindow: {min: 0, max: 50},
        },
        vAxis:
        {
          title: 'Mean time (seconds)',
          titleTextStyle: {fontSize: '15'},
        },
        bubble: {textStyle: {fontSize: 13}},
        sizeAxis: {maxValue: {{max_bubble}}, minValue: 0, maxSize: 40, minSize: 5}
      };

            var chart{{loop.index0}} = new google.visualization.BubbleChart(document.getElementById('chart{{loop.index0}}'));
            chart{{loop.index0}}.draw(view{{loop.index0}}, options{{loop.index0}});

         var selectHandler{{loop.index0}} = function(e) {
         window.location = data{{loop.index0}}.getValue(chart{{loop.index0}}.getSelection()[0]['row'], 5 );
        }

        google.visualization.events.addListener(chart{{loop.index0}}, 'select', selectHandler{{loop.index0}});

        {% endfor %}
        }
        </script>

        {% for vals in frame %}
        {% set right = ''' + str(right) + ''' %}
        {% set top = ''' + str(top) + ''' %}
        <div id="chart{{loop.index0}}" style="position: absolute; left: {{right[loop.index0]}}%; top:{{top[loop.index0]}}%;
        width: ''' + str(size[0]) + '''%; height: ''' + str(size[1]) + '''%;"></div>
        {% endfor %}

    </head>
    <body>
        <h1> Savu MPI performance tests </h1>
        {% set dict = ''' + str(params) + ''' %}
        {% set nDict = ''' + str(len(params)) + '''%}
        {% if nDict > 0 %}
        <div class="boxed">
            ---------
            {% for key in dict %}
            {{key}} : {{dict[key]}} ---------
            {% endfor %}
        </div>
        {% endif %}
    </body>
    </html>
    '''

    return template_string
