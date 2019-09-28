#!/usr/bin/env python
import os
import sys
from numpy import floor, ceil
import itertools
from towerlist import get_towers
from subprocess import Popen, PIPE
from settings import config, build_logger
from time import sleep
from rc import build_array


log = build_logger('muxinator')
tmux_running = ( 'TMUX' in os.environ.keys() )
numpanes = config.rows * config.columns
#session_name = config.get('session_name', 'tmuxify')

def tmux(command):
    log.debug('tmux command:  %s' % command)
    proc = Popen('tmux {0}'.format(command), shell=True, stdout=PIPE)
    return proc.communicate()[0].strip().decode()

def current_pane():
    return tmux('display-message -p -F "#S:#I.#P"')

def screensize():
    return tuple([int(x) for x in Popen(['stty', 'size'], stdout=PIPE).communicate()[0].split()])

def build_screen(max_rows=2, max_columns=5):
    startdir = config.directory
    rows, columns = screensize()
    rheight = int(rows / max_rows)
    cwidth = int(columns / max_columns)
    tmux('new-window')
    target = current_pane()
    panes = [target]
    while len(panes) < max_rows:
        panes.append(tmux('split-window -c {2} -v -d -t {0} -l {1} -P'.format(target, rheight, startdir)))
    for row in range(len(panes)):
        if row == 0:
            pass
        else:
            tmux('select-window -t {0}'.format(target))
            tmux('select-pane -D')
            target = current_pane()
        for j in range(max_columns - 1):
            tmux('split-window -c {2} -d -t {0} -h -l {1}'.format(target, cwidth, startdir))
    return tmux('list-panes -F "#S:#I.#P"').splitlines()

def setup():
    if not tmux_running:
        raise "Run from a tmux session"
    start_window = tmux('display-message -p -F "#S:#I"')
    max_rows = config.rows
    max_columns = config.columns
    suffix = config.server.split('.')[0]
    towers = get_towers(config.server)
    screens = []
    if len(towers) > max_rows * max_columns:
        numscreens = int(ceil(len(towers) / ( max_rows * max_columns )))
    else:
        numscreens = 1
    while len(screens) < numscreens:
        screens.append(build_screen(max_rows, max_columns))
    panes = list(itertools.chain.from_iterable(screens))
    windows = dict(zip(towers, panes))
    for tower, target in windows.items():
        tmux('pipe-pane -t {0} -o "cat >>{2}/{1}.log"'.format(target,tower, config.directory))
        tmux('send-keys -t {0} "ssh {1}.{2}"'.format(target, tower, suffix))
    tmux('select-window -t {0}'.format(start_window))
    print("""
        Your windows have been set up.  move to a newly created window and then press Ctrl-S to start synchronization.
        """)

if __name__ == "__main__":
    setup()
#    print(build_array(get_towers(config.server), config.columns, config.rows))

