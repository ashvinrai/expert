import argparse
import sys

from expert.expert import Expert

parser = argparse.ArgumentParser(prog="expert", description='Compares and scores the contributers of a git repository')
parser.add_argument('path', metavar='path', help='the path of the directory to score relative to the root of the project')
parser.add_argument('-v', '--verbose', help='returns all the information used to score the contributers', action='store_true')
parser.add_argument('-c', '--compare', help='compares the requested directory commits to the commits for the passed in file path')
parser.add_argument('-r', '--repo', help='path to the desired repo', default="/")

args = parser.parse_args()
if args.path:
    directory = args.repo
    expert = Expert(directory)
    expert.scoreDirectory(args.path, args.verbose, args.compare)
