#!/usr/bin/python2

import argparse
import os
import re
import sys
import itertools
from subprocess import Popen, PIPE, STDOUT

# check python version
if sys.version_info >= (3,0):
    print("This script requires python2.7")
    exit(1)


tests = ['calc', 'syntax', 'syntax-ext']
not_error = re.compile(r"^[\d\s]*$")
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
colors = {
    'SUCCESS': GREEN,
    'INFO': BLUE,
    'WARN': YELLOW,
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
parser.add_argument('-f', '--force', action='store_true', dest='force',
                    help="fore execution even if stderr output", default=False)
parser.set_defaults(color=has_colours(sys.stdout))

args = parser.parse_args()

def main():
    global tests
    if args.test:
        tests = [args.test]
    try:
        for test in tests:
            input, raw_expected = get_tests(test);
            expected = split_tests(raw_expected)
            output, stderr = get_output(args.jar, input)
            if len(stderr) > 0:
                if args.force:
                    log("Program outputted errors, forcing\n%s" % stderr, 'WARN' )
                else:
                    raise TestFailure("Program outputted errors:\n%s" % stderr)
            if output is None:
                raise TestFailure("Program did not return any output")
            compare(output, expected)
            log("Passed test %s!" % test, "SUCCESS")
        log("All tests passed!", "SUCCESS")
    except TestFailure as fail:
        log(fail, "FAIL")
        if (fail.lines):
            log("Input:", "INFO")
            for i in range(*fail.lines):
                log("%s:%-3d > %s"% ("%s.in"%test, i+1, input.splitlines()[i]), "INFO")

def get_tests(test):
    return map(lambda x: open("io/%s.%s" % (test, x)).read(), ["in", "out"])

def split_tests(tests):
    line, output = zip(*map(lambda x: x.split(":"), tests.splitlines()))
    line = pairwise([0] + list(map(int, line)))
    return zip(line, output)

def pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b, None)
    return list(itertools.izip(a, b))

def get_output(prog, input):
    cmd = ['java', '-jar', prog]
    if args.run:
        cmd = args.run.split()
    log("Running command `%s`" % ' '.join(cmd), lvl=1)
    p = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE)
    return p.communicate(input=input)

def compare(output, expected):
    map(lambda x: match(x[0], x[1]), map(None, output.splitlines(), expected))

def match(output, expected):
    if expected is None:
        raise TestFailure("Expected no more output, got `%s`" % output)
    if expected[1][:5] == 'error':
        return match_err(output, expected)
    else:
        return match_set(output, expected)

def match_err(output, error):
    log("Matching `%s` for error `%s`" % (output, error[1]), lvl=0 if args.errors else 2)
    if not_error.match(output):
        raise TestFailure("Expected error for %s but got `%s`" % (error[1], output), error[0])
    log("Error match!", "SUCCESS", 1)

def match_set(output, expected):
    log("Matching set `%s` to `%s`" % (expected[1], output), lvl=2)
    if not str_to_set(output, expected[0]) == str_to_set(expected[1], expected[0]):
        raise TestFailure("Expected set `%s` but got `%s`" % (expected[1], output), expected[0])
    log("Set match!", "SUCCESS", 1)

def str_to_set(s, lines):
    if s is None:
        raise TestFailure('Expected output, got none!', lines)
    try:
        l = map(int, s.split())
    except ValueError:
        raise TestFailure('Expected `%s` to be a set! Did you make sure your output format is "1 2 3"?' % s, lines)
    r = set(l)
    if len(l) != len(r):
        raise TestFailure('Set `%s` is not unique!' % s, lines)
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
    def __init__(self, message, lines=False):
        super(TestFailure, self).__init__(message)
        self.lines = lines

if __name__ == "__main__":
    main()
