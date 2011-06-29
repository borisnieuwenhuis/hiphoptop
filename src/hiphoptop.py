#!/usr/bin/python
import curses.wrapper, time, sys, getopt
from random import randint
from hiphopstats import HiphopStats

SCREEN_WIDTH_LAYOUT = [0, 10, 20, 30, 50]

options = {"refresh": 1, "sort": "hits", "server": "127.0.0.1", "port": 1970}
the_screen = None;

def key_handler(stdscr):
    c = stdscr.getch()
    if c == ord('c'): options["sort"] = "cpu"
    elif c == ord('h'): options["sort"] = "hits"
    elif c == ord('e'): options["sort"] = "err"
    elif c == ord('o'): options["sort"] = "ok"
    elif c == ord('n'): options["sort"] = "name"
    elif c == ord('q'): return False
    draw_screen()
    return True

def get_daemons():

    daemons = []
    stats = HiphopStats(options["server"], options["port"])

    for name, data in stats.getLatestInfo().iteritems():
        daemons.append(Daemon(name, data['code_500'], data['code_200'], data['page.cpu.all']))

    return daemons

def draw_screen():

    value = str(time.time())
    global the_screen
    the_screen.clear()
    the_screen.addstr(0, SCREEN_WIDTH_LAYOUT[0], "hit", curses.A_UNDERLINE)
    the_screen.addstr(0, SCREEN_WIDTH_LAYOUT[1], "err", curses.A_UNDERLINE)
    the_screen.addstr(0, SCREEN_WIDTH_LAYOUT[2], "ok", curses.A_UNDERLINE)
    the_screen.addstr(0, SCREEN_WIDTH_LAYOUT[3], "cpu", curses.A_UNDERLINE)
    the_screen.addstr(0, SCREEN_WIDTH_LAYOUT[4], "script", curses.A_UNDERLINE)

    daemons = get_daemons()
    daemons = sorted(daemons, key=lambda daemon: getattr(daemon, options["sort"]), reverse=True)
    #print daemons

    i = 1
    for daemon in daemons:
        the_screen.addstr(1*i, SCREEN_WIDTH_LAYOUT[0], str(daemon.hits))
        the_screen.addstr(1*i, SCREEN_WIDTH_LAYOUT[1], str(daemon.err))
        the_screen.addstr(1*i, SCREEN_WIDTH_LAYOUT[2], str(daemon.ok))
        the_screen.addstr(1*i, SCREEN_WIDTH_LAYOUT[3], str(daemon.cpu))
        the_screen.addstr(1*i, SCREEN_WIDTH_LAYOUT[4], str(daemon.name))
        i = i + 1
        if i>10:
            break

    the_screen.refresh()

class Daemon():
    def __init__(self, name, err, ok, cpu):
        self.name = name
        self.hits = err + ok
        self.err = err
        self.ok = ok
        self.cpu = cpu

    def __repr__(self):
        return repr((self.name, self.instance, self.cpu, self.mem))

def _main(stdscr):
    try:
        stdscr.nodelay(1)

        global the_screen
        the_screen = stdscr
        while key_handler(stdscr):
            draw_screen()
            time.sleep(options["refresh"])
    except KeyboardInterrupt:
        pass

def usage():
    print "-i --interval refresh rate in seconds -s --server server host"
    print "xcellent by Boris"

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hi:s:p:", ["help", "interval=", "server=", "port="])

        for opt, arg in opts:
            if opt in ("-h", "--help"):
                usage()
                sys.exit()
            elif opt in ("-i", "--interval"):
                options["refresh"] = int(arg)
            elif opt in ("-s", "--server"):
                options["server"] = arg
            elif opt in ("-p", "--port"):
                options["port"] = arg
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    curses.wrapper(_main)

if __name__=='__main__':
    main(sys.argv[1:])




