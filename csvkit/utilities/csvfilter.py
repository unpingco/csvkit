#!/usr/bin/env python

"""
"""

import itertools

from csvkit import CSVKitReader, CSVKitWriter
from csvkit.cli import CSVKitUtility, parse_column_identifiers
from csvkit.headers import make_default_headers

class CSVFilter(CSVKitUtility):
    description = 'Filter rows based on column-wise condition.'
    def add_arguments(self):
        self.argparser.add_argument('-c', '--columns', dest='columns',
            help='A comma separated list of column indices or names to be extracted. Defaults to all columns.')
        self.argparser.add_argument('-C', '--not-columns', dest='not_columns',
            help='A comma separated list of column indices or names to be excluded. Defaults to no columns.')
        self.argparser.add_argument('--filter-column', dest='filter_column',
            help='Take only rows from specified column. Defaults to all columns.')
        self.argparser.add_argument('--filter-expr', dest='filter_expr',
            help='Take only rows from previously specified column so that expr that evalutes True. Defaults to all columns.')

    def main(self):
        rows = CSVKitReader(self.input_file, **self.reader_kwargs)
        if self.args.no_header_row:
            row = next(rows)
            column_names = make_default_headers(len(row))
            # Put the row back on top
            rows = itertools.chain([row], rows)
        else:
            column_names = next(rows)

        column_ids = parse_column_identifiers(self.args.columns, column_names, self.args.zero_based, self.args.not_columns)

        if self.args.filter_column:
            # get column_id for needed column_name
            filter_column_id, = parse_column_identifiers(self.args.filter_column, column_names, self.args.zero_based, self.args.not_columns)

        output = CSVKitWriter(self.output_file, **self.writer_kwargs)
        output.writerow([column_names[c] for c in column_ids])
        str_colname = column_names[ filter_column_id]
        for row in rows:
            exec('%s = %s'%(str_colname, row[filter_column_id]))
            if eval(self.args.filter_expr): 
                out_row = [row[c] if c < len(row) else None for c in column_ids]
                output.writerow(out_row)

def launch_new_instance():
    utility = CSVFilter()
    utility.main()

if __name__ == "__main__":
    launch_new_instance()
