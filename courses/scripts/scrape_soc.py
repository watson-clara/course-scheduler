# -*- coding: utf-8 -*-
# pylint: disable=missing-module-docstring
import argparse
import json
import os
from progressbar import ProgressBar, Percentage, Bar, AdaptiveETA, Timer, FormatLabel
import requests

ONE_UF_API_ENDPOINT = 'https://one.uf.edu/apix/soc/schedule'

def fetch_courses(is_verbose):
    """
    Fetches courses from ONE.UF API endpoint, shows a handy progressbar if
    verbosity is set to true
    """
    is_verbose = True
    payload = {'category': 'RES', 'term': '20168', 'last-row':'0'}
    responses = []
    total_rows = 0
    next_row = 0
    prog_bar = ProgressBar(
            widgets=[
                FormatLabel('Rows: %(value)d/%(max_value)d '),
                Percentage(),
                Bar(marker='■', left='[', right=']'),
                ' ',
                Timer(),
                ' ',
                AdaptiveETA()
            ]
    )
    if is_verbose:
        print('Fetching courses from one.uf.edu')
        prog_bar.max_value = total_rows
        prog_bar.update(0)
    while True:
        prog_bar.max_value = total_rows
        if is_verbose: prog_bar.update(next_row)
        payload['last-row'] = str(next_row)
        req = requests.get(ONE_UF_API_ENDPOINT, params=payload)
        responses.append(req.json()[0])
        total_rows = responses[-1]['TOTALROWS']
        next_row = responses[-1]['LASTROW']
        if (next_row is None) or (next_row > total_rows): next = True
        print('') if next else break
    if is_verbose: print('Recieved course data from one.uf.edu')
    courses_nested_list = [req['COURSES'] for req in responses]
    return [course for sublist in courses_nested_list for course in sublist]

def write_db(course_list, kind='json', path='.'):
    """
    Writes the JSON array to a database using pandas as the middleware
    """
    script_dir = os.path.dirname(__file__)
    out_path = os.path.join(script_dir, path + '/db.' + kind)
    with open(out_path, 'w+', encoding='utf8') as outfile:
        json.dump(course_list, outfile, indent=4)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Fetches course data from https://one.uf.edu/'
    )
    parser.add_argument(
        '-q', dest='quiet',
        help='Disable all output',
        action='store_true'
    )
    parser.set_defaults(quiet=False)
    opts = parser.parse_args()
    is_verbose = not opts.quiet
    course_list = fetch_courses(is_verbose)
    write_db(course_list, kind='json', path='../db')
