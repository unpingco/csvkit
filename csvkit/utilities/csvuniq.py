#!/usr/bin/env python

"""
"""

import itertools

from csvkit import CSVKitReader, CSVKitWriter
from csvkit.cli import CSVKitUtility, parse_column_identifiers
from csvkit.headers import make_default_headers
from ColumnSelectorMixin import ColumnSelectorMixin

class CSVUniq(CSVKitUtility,ColumnSelectorMixin):
    description = 'Make rows unique based upon specific column rows. Like unix "uniq" command, but for tabular data.'
    def add_arguments(self):
        ColumnSelectorMixin.add_arguments(self)
        self.argparser.add_argument('-x', '--delete-empty-rows', dest='delete_empty', action='store_true',
            help='After cutting, delete rows which are completely empty.')
        self.argparser.add_argument('--uniq-column', dest='uniq_column',
            help='A comma separated list of column indices or names to be un-duplicated. Defaults to all columns.')

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
        column_ids = self.parse_regex_column(self.args.regex_column,column_ids,column_names)
        column_ids = self.parse_not_regex_column(self.args.not_regex_column,column_ids,column_names)
        column_ids = self.parse_column_contains(self.args.column_contains,column_ids,column_names)
        column_ids = self.parse_not_column_contains(self.args.not_column_contains,column_ids,column_names)

        uniq_column_id = parse_column_identifiers(self.args.uniq_column, column_names, self.args.zero_based, self.args.not_columns)
        output = CSVKitWriter(self.output_file, **self.writer_kwargs)
        output.writerow([column_names[c] for c in column_ids])
        d = set() # cache for used-rows
        # use tuple as keys for cache
        cache_key = lambda row: tuple([row[i] for i in uniq_column_id])
        for row in rows:
            if cache_key(row) in d: continue
            d.update([ cache_key(row) ])
            out_row = [row[c] if c < len(row) else None for c in column_ids]
            if self.args.delete_empty:
                if ''.join(out_row) == '':
                    continue
            output.writerow(out_row)

def launch_new_instance():
    utility = CSVUniq()
    utility.main()

if __name__ == "__main__":
    launch_new_instance()

