
import argparse
import itertools
import os
import re
import tempfile

import numpy as np
import pandas as pd


def reset_first_entry(memory_data):
    """
    Resets the first memory entry for each unique component in the series
    """

    def _reset(s):
        try:
            for i in range(64):
                memory_data.Memory[memory_data.Key.str.contains(s.format(i))].iloc[0][1] = '0'
        except IndexError:
            pass

    _reset("CPU{}")
    _reset("GPU{}")

    return memory_data


def get_memory_data(frame):
    memory_data = frame[frame.Message.str.contains("memory usage")]
    number_finder = re.compile('[0-9]+')
    memory_data.insert(4, "Memory", [list(itertools.chain(msg.split()[0:1], number_finder.findall(msg))) for msg in
                                     memory_data.Message])

    memory_data = pd.concat([memory_data.Key, memory_data.Memory], axis=1, join="outer")
    return reset_first_entry(memory_data)


def convert(log_file_list, path, log_level):
    for log_file in log_file_list:
        the_key = ""
        the_interval = 0  # millisecs
        frame = get_frame(log_file, the_key, 'DEBUG')
        machine_names = get_machine_names(frame)
        memory_data = get_memory_data(frame)
        if log_level != 'DEBUG':
            frame = get_frame(log_file, the_key, log_level)
        html_filename = \
            set_file_name('/'.join([path, os.path.basename(log_file)]))
        render_template(frame, machine_names, memory_data, the_interval, html_filename)
        print("html file created:", html_filename)
        print("Open the html file in your browser to view the profile.")

    return frame


def get_frame(log_file, the_key, log_level):
    import itertools

    names = ['L', 'Time', 'Machine', 'CPU', 'Type', 'Message']
    data = pd.io.parsers.read_fwf(log_file, widths=[2, 13, 6, 6, 7, 1000],
                                  names=names)

    data['Key'] = data['Machine'] + data['CPU']
    frame = ((data[data.Type == log_level])[data.columns[[6, 5, 1]]])
    frame.insert(0, 'Index', list(range(len(frame))))
    frame = frame.sort_values(by=['Key', 'Index'])
    del frame['Index']

    frame.Time = frame.Time.astype(np.int32)
    startTime = (frame.groupby('Key').first()).Time
    nElems = frame.groupby('Key').size()

    shift = []
    for i in range(len(nElems)):
        shift.append([startTime[i]] * nElems[i])
    shift = list(itertools.chain(*shift))

    frame.Time = frame.Time - shift
    frame = frame[frame.Key.str.contains(the_key)]
    frame.insert(3, "Time_end", frame.Time.shift(-1))
    frame.Message = frame.Message.str.strip('\n')
    frame.Message = frame.Message.str.replace("'", "")

    return frame


def get_machine_names(frame):
    machine_names = frame.copy(deep=True)
    machine_names = machine_names[frame.Message.str.contains('Rank').replace(np.nan, False)]
    machine_names.Message = [m.split(':')[-1].strip() for m in frame.Message if isinstance(m, str) and 'Rank' in m]
    machine_names = machine_names.drop(['Time', 'Time_end'], axis=1)
    machine_names.Key = [k.split('CPU')[0] for k in machine_names.Key]
    machine_names.Key = [k.split('GPU')[0] for k in machine_names.Key]
    machine_names = machine_names.groupby('Key').first()
    machine_names['Machine'] = machine_names.index.values

    return machine_names


def render_template(frame, machine_names, memory_data, the_interval, outfilename):
    from jinja2 import Template

    frame = frame[(frame.Time_end - frame.Time) > the_interval].values

    f_out = open(outfilename, 'w')
    dirname = os.path.dirname(__file__)
    style = os.path.join(dirname, 'style_sheet.css')
    with open(os.path.join(dirname, 'string_single.html'), 'r') as template_file:
        template = Template(template_file.read())

    f_out.write(template.render(chart_width=1300, position=[16, 9],
                                vals=map(list, frame[:, 0:4]),
                                machines=map(list, machine_names.values),
                                memory=map(list, memory_data.values),
                                style_sheet=style))
    f_out.close()

    return frame


def set_file_name(filename):
    dir_path = os.path.dirname(filename)
    temp = os.path.basename(filename).split('.')
    filename = temp[0] + '_' + temp[1] + '.html'
    outfilename = dir_path + '/' + filename

    return outfilename


def __option_parser(doc=True):
    """ Option parser for command line arguments.
    """
    parser = argparse.ArgumentParser(prog='savu_profile')

    parser.add_argument('file', help='Savu output log file')
    parser.add_argument('-l', '--loglevel', default='INFO',
                        help='Set the log level.')
    parser.add_argument('-f', '--find', nargs='*', default=[],
                        help='Find lines containing these entries')
    parser.add_argument('-i', '--ignore', nargs='*', default=[],
                        help='Ignore lines containing these entries')
    return parser if doc == True else parser.parse_args()


def main():
    args = __option_parser(doc=False)

    filename = os.path.abspath(args.file)

    # create the log file for profiling
    name, ext = os.path.splitext(os.path.basename(filename))
    log_filename = os.path.join(tempfile.mkdtemp(), '{}_{}.log'.format(name, ext))

    lfilter = ['L '] + args.find
    with open(filename, 'r') as finput:
        with open(log_filename, 'w') as foutput:
            for line in finput:
                filter_line = [True if t in line else False for t in lfilter]
                keep_line = [False if t in line else True for t in args.ignore]
                line = False if False in filter_line + keep_line else line
                if line:
                    foutput.write(line)

    convert([log_filename], os.path.dirname(filename), args.loglevel)


if __name__ == "__main__":
    main()
