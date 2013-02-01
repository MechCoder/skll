#!/usr/bin/env python
'''
Script that converts MegaM files to LibSVM format

@author: Dan Blanchard, dblanchard@ets.org,
@date: May 2012
'''

from __future__ import print_function, unicode_literals

import argparse
import sys
from itertools import islice, izip
from operator import itemgetter

from bs4 import UnicodeDammit


class UniqueNumberDict(dict):
    """ Class for creating sequential unique numbers for each key."""

    def __getitem__(self, key):
        if key not in self:
            self[key] = len(self) + 1
        return dict.__getitem__(self, key)


def convert_to_libsvm(lines):
    '''
        Converts a sequence of lines (e.g., a file or list of strings) in MegaM format to LibSVM format.
        @param lines: The sequence of lines to convert.
        @type lines: L{file} or L{list} of L{str}

        @return: A tuple of the newly formatted data, the mappings from class names to numbers, and the mappings from feature names to numbers.
        @rtype: 3-L{tuple} of (L{list} of L{unicode}, L{dict}, and L{dict})
    '''

    # Initialize variables
    field_num_dict = UniqueNumberDict()
    class_num_dict = UniqueNumberDict()

    result_list = []
    # Iterate through MegaM file
    for line in lines:
        line_fields = set()
        # Process encoding
        line = UnicodeDammit(line, ['utf-8', 'windows-1252']).unicode_markup.strip()

        # Ignore comments (and TEST/DEV lines)
        if not line.startswith('#') and not line == 'TEST' and not line == 'DEV':
            result_string = ''
            split_line = line.split()
            result_string += unicode(class_num_dict[split_line[0]])
            # Handle features if there are any
            if len(split_line) > 1:
                del split_line[0]
                # Loop through all feature-value pairs printing out pairs separated by commas (and with feature names replaced with numbers)
                for field_num, value in sorted(izip((field_num_dict[field_name] for field_name in islice(split_line, 0, None, 2)),
                                                    (float(value) if value != 'N/A' else 0.0 for value in islice(split_line, 1, None, 2)))):
                    # Check for duplicates
                    if field_num in line_fields:
                        field_name = (field_name for field_name, f_num in field_num_dict.items() if f_num == field_num).next()
                        raise AssertionError("Field {} occurs on same line twice.".format(field_name))
                    # Otherwise output non-empty features
                    elif value != 'N/A' and float(value):
                        result_string += ' {}:{}'.format(field_num, value)
                        line_fields.add(field_num)
            result_list.append(result_string)

    return result_list, class_num_dict, field_num_dict


def convert_to_libsvm_iter(lines, class_num_dict=None, field_num_dict=None):
    '''
        Iterator-based version of convert_to_libsvm.
        Converts a sequence of lines (e.g., a file or list of strings) in MegaM format to LibSVM format.
        @param lines: The sequence of lines to convert.
        @type lines: L{file} or L{list} of L{str}

        @return: A tuple of the newly formatted data, the mappings from class names to numbers, and the mappings from feature names to numbers.
        @rtype: 2-L{tuple} of (L{list} of L{unicode} and L{dict})
    '''

    # Initialize variables
    field_num_dict = field_num_dict if field_num_dict else UniqueNumberDict()
    class_num_dict = class_num_dict if class_num_dict else UniqueNumberDict()

    # Iterate through MegaM file
    for line in lines:
        line_fields = set()
        # Process encoding
        line = UnicodeDammit(line, ['utf-8', 'windows-1252']).unicode_markup.strip()

        # Ignore comments (and TEST/DEV lines)
        if not line.startswith('#') and not line == 'TEST' and not line == 'DEV':
            result_string = ''
            split_line = line.split()
            result_string += unicode(class_num_dict[split_line[0]])
            # Handle features if there are any
            if len(split_line) > 1:
                del split_line[0]
                # Loop through all feature-value pairs printing out pairs separated by commas (and with feature names replaced with numbers)
                for field_num, value in sorted(izip((field_num_dict[field_name] for field_name in islice(split_line, 0, None, 2)),
                                                    (float(value) if value != 'N/A' else 0.0 for value in islice(split_line, 1, None, 2)))):
                    # Check for duplicates
                    if field_num in line_fields:
                        field_name = (field_name for field_name, f_num in field_num_dict.items() if f_num == field_num).next()
                        raise AssertionError("Field {} occurs on same line twice.".format(field_name))
                    # Otherwise output non-empty features
                    elif value != 'N/A' and float(value):
                        result_string += ' {}:{}'.format(field_num, value)
                        line_fields.add(field_num)
            yield result_string, class_num_dict, field_num_dict


def main():
    ''' Main function '''
    # Get command line arguments
    parser = argparse.ArgumentParser(description="Takes a MegaM-compatible file to be run with the '-fvals' switch and outputs a " +
                                                 "LibSVM/LibLinear-compatible file to STDOUT.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('infile', help='MegaM input file', type=argparse.FileType('r'), default='-', nargs='?')
    parser.add_argument('-m', '--mappingfile', help='File to output mapping of feature/class indices to names to', type=argparse.FileType('w'), default='map.idx')
    args = parser.parse_args()

    if args.infile.isatty():
        print("You are running this script interactively. Press CTRL-D at the start of a blank line to signal the end of your input. For help, run it with --help\n",
              file=sys.stderr)

    line_list, class_num_dict, field_num_dict = convert_to_libsvm(args.infile)

    # Iterate through converted MegaM file
    for line in line_list:
        print(line.encode('utf-8'))

    # Print out mappings to file
    print("CLASS NUM\tCLASS NAME", file=args.mappingfile)
    for class_name, class_num in sorted(class_num_dict.iteritems(), key=itemgetter(1)):
        print("{}\t{}".format(class_num, class_name).encode('utf-8'), file=args.mappingfile)

    print("\n\nFEATURE NUM\tFEATURE NAME", file=args.mappingfile)
    for field_name, field_num in sorted(field_num_dict.iteritems(), key=itemgetter(1)):
        print("{}\t{}".format(field_num, field_name).encode('utf-8'), file=args.mappingfile)

if __name__ == '__main__':
    main()
