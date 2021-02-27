import os

import numpy as np
import pandas as pd

from . import GraphicalThreadProfiler as gtp


def convert(filename):
    the_key = ""  # CPU0"
    the_interval = 0.8  # millisecs

    all_frames = []
    for files in filename:
        frame = gtp.get_frame(files, the_key, 'DEBUG')
        [index, nth] = get_index(frame)
        frame.Time_end[frame.index[np.cumsum(nth) - 1]] = frame.Time.max()
        frame = frame.reset_index(drop=True)
        temp = pd.DataFrame(np.array(frame.Time_end - frame.Time),
                            columns=['Time_diff'])
        temp['Key'] = frame.Key
        temp['index'] = [item for sublist in index for item in sublist]
        temp = temp.pivot(index='index', columns='Key', values='Time_diff')

        all_frames.append(temp)

    avg_duration = get_average_duration(all_frames)
    stats = output_stats(all_frames, filename)

    frame.Time_end = avg_duration
    frame.Time = frame.Time_end.shift(1)
    frame.Time.iloc[0] = 0

    render_template(frame, the_interval, set_file_name(filename),
                    get_links(filename), stats)
    return frame


def get_index(frame):
    nth = []
    index = []
    for i in range(np.size(frame.Key.unique())):
        nth.append(frame[frame.Key == frame.Key.unique()[i]].count()[0])
        index.append(list(range(nth[i])))

    return [index, nth]


def get_average_duration(frames):
    avg_frames = pd.Panel({n: df for n, df in enumerate(frames)})
    avg_frames = (avg_frames.mean(axis=0)).cumsum(0)
    avg_frames = avg_frames.as_matrix(columns=avg_frames.columns[:])
    avg_frames = np.reshape(np.transpose(avg_frames),
                            np.prod(avg_frames.shape))
    avg_frames = avg_frames[~np.isnan(avg_frames)]

    return avg_frames


def set_file_name(filename):
    [dir_path, name] = get_base_path(filename)

    name = name[0].split('.')[0] + '_avg' + repr(filename) + '.html'
    outfilename = dir_path + name

    return outfilename


def get_links(filename):
    [dir_path, fname] = get_base_path(filename)

    name = [gtp.set_file_name(file) for file in fname]
    links = [(dir_path + n) for n in name]

    return links


def render_template(frame, the_interval, outfilename, theLinks, theStats):
    from jinja2 import Template

    frame = frame[(frame.Time_end - frame.Time) > the_interval].values

    f_out = open(outfilename, 'w')
    dirname = os.path.dirname(__file__)
    style = os.path.join(dirname, 'style_sheet.css')
    with open(os.path.join(dirname, 'string_single.html'), 'r') as template_file:
        template = Template(template_file.read())
    f_out.write(template.render(chart_width=1300, position=[16, 9],
                                vals=map(list, frame[:, 0:4]), links=theLinks,
                                stats=theStats, style_sheet=style))
    f_out.close()

    return frame


def output_stats(frames, filename):
    temp = []
    for frame in frames:
        temp.append(frame.sum())

    total = pd.concat([i for i in temp], axis=0)
    total_stats = total.describe()

    [dir_path, name] = get_base_path(filename)
    name = name[0].split('.')[0] + '_avg' + repr(len(filename)) + '_stats.csv'
    outfilename = dir_path + name

    total_stats.to_csv(outfilename)

    return total_stats


def get_machine_names(all_frames):
    pass


def get_base_path(filename):
    if len(filename[0].split('/')) == 0:
        dir_path = os.getcwd()
    else:
        dir_path = os.path.dirname(filename[0])
        filename = [(os.path.basename(f)) for f in filename]

    return [dir_path + '/', filename]


if __name__ == "__main__":
    import optparse

    usage = "%prog [options] input_file"
    parser = optparse.OptionParser(usage=usage)

    (options, args) = parser.parse_args()
    print(args)
    filename = [(os.getcwd() + '/' + file) for file in args]
    convert(filename)
