#!/usr/bin/python2

import argparse
import os
import re
import sys
from subprocess import Popen, PIPE, STDOUT

tests = ['calc', 'syntax', 'syntax-ext']
not_error = re.compile(r"^[\d\s]*$")
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
colors = {
    'SUCCESS': GREEN,
    'INFO': BLUE,
    'FAIL': RED
}

#following from Python cookbook, #475186
def has_colours(stream):
    if not hasattr(stream, "isatty"):
        return False
    if not stream.isatty():
        return False # auto color only on TTYs
    try:
        import curses
        curses.setupterm()
        return curses.tigetnum("colors") > 2
    except:
        # guess false in case of error
        return False

parser = argparse.ArgumentParser(description='Automatic tester for Advanced ' +
                                 'Programming assignment 2, NoVA edition')
parser.add_argument('jar', action='store', nargs='?',
                    default='build/libs/AP2-1.0.jar', type=str,
                    help="location of jar to execute")
parser.add_argument('-v', '--verbose', action='count', default=0,
                    help="output more details of the tests executed")
parser.add_argument('-e', '--errors', action='store_true', default=False,
                    help="output errors being tested")
parser.add_argument('-c', '--color', action='store_true', dest='color',
                    help="force color output")
parser.add_argument('-n', '--no-color', action='store_false', dest='color',
                    help="force disable color output")
parser.add_argument('-t', '--test', action='store', choices=tests,
                    help="specify single test to run")
parser.add_argument('-r', '--run', action='store',
                    help="specify command used to run your program (arbitrary)")
parser.set_defaults(color=has_colours(sys.stdout))

args = parser.parse_args()

def main():
    global tests
    if args.test:
        tests = [args.test]
    try:
        for test in tests:
            input, expected = get_tests(test);
            output, stderr = get_output(args.jar, input)
            if len(stderr) > 0:
                raise TestFailure("Program outputted errors:\n%s" % stderr)
            compare(output, expected)
            log("Passed test %s!" % test, "SUCCESS")
        log("All tests passed!", "SUCCESS")
    except TestFailure as fail:
        log(fail, "FAIL")

def get_tests(test):
    return map(lambda x: open("io/%s.%s" % (test, x)).read(), ["in", "out"])

def get_output(prog, input):
    cmd = ['java', '-jar', prog]
    if args.run:
        cmd = args.run.split()
    log("Running command `%s`" % ' '.join(cmd), lvl=1)
    p = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE)
    return p.communicate(input=input)

def compare(output, expected):
    map(lambda x: match(x[0], x[1]), map(None, output.splitlines(), expected.splitlines()))

def match(output, expected):
    if expected[:5] == 'error':
        return match_err(output, expected[6:])
    else:
        return match_set(output, expected)

def match_err(output, error):
    log("Matching `%s` for error `%s`" % (output, error), lvl=0 if args.errors else 2)
    if not_error.match(output):
        raise TestFailure("Expected error for %s but got `%s`" % (error, output))
    log("Error match!", "SUCCESS", 1)

def match_set(output, expected):
    log("Matching set `%s` to `%s`" % (expected, output), lvl=2)
    if not str_to_set(output) == str_to_set(expected):
        raise TestFailure("Expected set `%s` but got `%s`" % (expected, output))
    log("Set match!", "SUCCESS", 1)

def str_to_set(s):
    try:
        l = map(int, s.split())
    except ValueError:
        raise TestFailure('Expected `%s` to be a set!' % s)
    r = set(l)
    if len(l) != len(r):
        raise TestFailure('Set `%s` is not unique!' % s)
    return r

def log(s, type='INFO', lvl=0):
    color = WHITE
    if type in colors:
        color = colors[type]
    if args.verbose >= lvl:
        sys.stdout.write("[")
        printout("%07s" % type, color)
        sys.stdout.write("] %s\n" % s)

def printout(text, colour=WHITE):
    if args.color:
        seq = "\x1b[1;%dm" % (30+colour) + text + "\x1b[0m"
        sys.stdout.write(seq)
    else:
        sys.stdout.write(text)

class TestFailure(Exception):
    pass

if __name__ == "__main__":
    main()
