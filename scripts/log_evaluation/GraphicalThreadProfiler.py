import pandas as pd
import os


def convert(filename):

    for file in filename:
        print file
        the_key = ""  # CPU0"
        the_interval = 0.8  # millisecs
        frame = get_frame(file, the_key)

        machine_names = get_machine_names(frame)
        render_template(frame, machine_names, the_interval,
                        set_file_name(file))

    return frame


def get_frame(file, the_key):
    import itertools

    names = ['L', 'Time', 'Machine', 'CPU', 'Type', 'Message']
    data = pd.io.parsers.read_fwf(file, widths=[2, 13, 5, 5, 6, 1000],
                                  names=names)
    data['Key'] = data['Machine'] + data['CPU']
    frame = ((data[data.Type == "DEBUG"])[data.columns[[6, 5, 1]]]).sort('Key')

    frame = frame.sort('Key')
    startTime = (frame.groupby('Key').first()).Time
    nElems = frame.groupby('Key').size()

    shift = []
    for i in range(len(nElems)):
        shift.append([startTime[i]]*nElems[i])
    shift = list(itertools.chain(*shift))

    frame.Time = frame.Time - shift
    frame = frame[frame.Key.str.contains(the_key)]
    frame.insert(3, "Time_end", frame.Time.shift(-1))
    frame.Message = frame.Message.str.strip('\n')
    frame.Message = frame.Message.str.replace("'", "")

    return frame


def get_machine_names(frame):
    machine_names = frame.copy(deep=True)
    machine_names = machine_names[frame.Message.str.contains('Rank')]
    machine_names.Message = [m.split(':')[-1].strip() for m in frame.Message
                             if 'Rank' in m]
    machine_names = machine_names.drop(['Time', 'Time_end'], axis=1)
    machine_names.Key = [k.split('CPU')[0] for k in machine_names.Key]
    machine_names = machine_names.groupby('Key').first()
    machine_names['Machine'] = machine_names.index.values

    return machine_names


def render_template(frame, machine_names, the_interval, outfilename):
    from jinja2 import Template
    import template_strings as ts

    frame = frame[(frame.Time_end - frame.Time) > the_interval].values

    f_out = open(outfilename, 'w')
    print outfilename
    style = os.path.dirname(__file__) + '/style_sheet.css'
    template = Template(ts.set_template_string_single(1300))
    f_out.write(template.render(vals=map(list, frame[:, 0:4]),
                                machines=map(list, machine_names.values),
                                style_sheet=style))
    f_out.close()

    return frame


def set_file_name(filename):

    dir_path = os.path.dirname(filename)
    temp = os.path.basename(filename).split('.')
    filename = temp[0] + '_' + temp[1] + '.html'
    outfilename = dir_path + '/' + filename

    return outfilename


if __name__ == "__main__":
    import optparse

    usage = "%prog [options] input_file"
    parser = optparse.OptionParser(usage=usage)

    (options, args) = parser.parse_args()

    filename = [os.getcwd() + '/' + args[0]]
    convert(filename)
