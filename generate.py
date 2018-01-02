"""
Generate funny things with barkov
"""

import glob
import csv
from collections import defaultdict
import json
import random

import markovify


def pull_file(filename, lines=None):
    """Pull a file into a dictionary
    
    Parameters
    ----------
    filename : str
        Filename to open
    lines : dict, optional
        An existing dictionary.  Keys are characters, values are lists of lines.

    Returns
    -------
    dict
        Updated dict with the new file
    """
    if lines is None:
        lines = defaultdict(list)
    with open(filename) as file_open:
        reader = csv.DictReader(file_open, fieldnames=['time', 'speaker', 'line'], delimiter='|')
        for row in reader:
            if row['line'] is not None and row['line'].strip() != '':
                lines[row['speaker']].append(row['line'])
    return lines

def pull_all_files():
    lines = None
    for filename in glob.glob('transcripts/*.csv'):
        lines = pull_file(filename, lines)
    return lines

def generate_line(speaker, lines):
    try:
        if speaker in ('(Scene)', 'Pups', 'Everyone'):
            to_join = [line.replace('(', '').replace(')', '') for line in lines[speaker]]
            text_model = markovify.Text(' '.join(to_join))
        else:
            to_join = lines[speaker]
            text_model = markovify.Text(' '.join(to_join))
        to_return = text_model.make_sentence(tries=100)
        if speaker == '(Scene)':
            to_return = '(' + to_return + ')'
        return to_return
    except:
        raise ValueError('Bad generating')

def is_short_line(line):
    if len(line.split()) == 1:
        return True
    if line[0] == '(' and line[-1] == ')' and line.count('(') == line.count(')') == 1:
        return True
    else:
        return False

def grab_short_line(speaker, lines):
    all_lines = lines[speaker]
    short_lines = [line for line in all_lines if is_short_line(line)]
    if len(short_lines) > 3:
        return random.choice(short_lines)
    else:
        raise ValueError('No good short lines')

def get_top_speakers(lines):
    top_speakers = sorted(lines.items(), key=lambda i: len(i[1]), reverse=True)[:20]
    for speaker in top_speakers:
        print(speaker[0], len(speaker[1]))
    return [speaker[0] for speaker in top_speakers]

def choose_line(speaker, lines):
    if random.random() > 0.6 and speaker != '(Scene)':
        try:
            return grab_short_line(speaker, lines)
        except:
            return generate_line(speaker, lines)
    else:
        try:
            return generate_line(speaker, lines)
        except:
            return grab_short_line(speaker, lines)

def make_a_scene(lines, top_speakers):
    p1, p2 = random.sample(top_speakers, 2)
    return '\n'.join([
        p1 + ': ' + choose_line(p1, lines),
        p2 + ': ' + choose_line(p2, lines),
        p1 + ': ' + choose_line(p1, lines),
        p2 + ': ' + choose_line(p2, lines)])


if __name__ == '__main__':
    #filename = 'transcripts/Pup_Pup_and_Away.csv'
    #d = pull_file(filename)
    #print(d)
    lines = pull_all_files()
    top_speakers = get_top_speakers(lines)
    for speaker in top_speakers:
        print(speaker + ':')
        try:
            print('  ' + generate_line(speaker, lines))
        except ValueError:
            print('  No good lines found')
        try:
            print('  ' + grab_short_line(speaker, lines))
        except ValueError:
            print('  No short lines found')
    for _ in range(10):
        print('----------')
        print(make_a_scene(lines, top_speakers))