import csv


def get_csv_comparison(file1, file2, keyname, outfile):
    def convert_csv_to_dict(fpath, pk):
        with open(fpath, mode='r') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',')
            reader.fieldnames = [fieldname.upper()
                                 for fieldname in reader.fieldnames]
            if isinstance(pk, str):
                pkey = pk.upper()
                if pkey not in reader.fieldnames:
                    raise Exception("The primary key does not match any header. Sorry :(")
                content_dict = {row[pkey]: {key: val for key, val 
                                            in row.items()}
                                for row in reader}
            else:
                pkey = [k.upper() for k in pk]
                if not all((k in reader.fieldnames for k in pkey)):
                    raise Exception("The primary key does not match any header. Sorry :(")
                content_dict = {tuple(row[k] for k in pkey): 
                                {key: val for key, val in row.items()}
                                for row in reader}
            
            csvfile.close()
            return content_dict

    def compare_mismatch_rows(row1, row2):
        keys = [k for k in row1]
        mismatch = [(k, row1[k], row2[k])
                    for k in keys if row1[k] != row2[k]]
        return mismatch

    def get_comparison_details(f1, f2, pk):
        f1_parsed = convert_csv_to_dict(f1, pk)
        f2_parsed = convert_csv_to_dict(f2, pk)
        
        missing_keys = [key for key in f1_parsed if key not in f2_parsed]
        mismatch_keys = [key for key in f1_parsed
                         if key in f2_parsed
                         and f1_parsed[key] != f2_parsed[key]]
        mismatch_columns = set()
        mismatch_col_details = dict()
        for k in mismatch_keys:
            mismatch_details = compare_mismatch_rows(
                f1_parsed[k], f2_parsed[k])
            mismatch_col_details[k] = mismatch_details
            for colname, *_ in mismatch_details:
                mismatch_columns.add(colname)
        return (missing_keys, mismatch_keys, mismatch_columns, mismatch_col_details)

    def get_comparison_summary(f1, f2, pk):
        printable_key = lambda key : key if isinstance(key, str) else ";".join((str(k) for k in key))
        missing_keys, mismatch_keys, mismatch_columns, mismatch_col_details = get_comparison_details(
            f1, f2, pk)
        out_summary = f'Comparing {f1} to {f2}\n'
               
        out_summary += 'Missing keys:\n'
        out_summary += '\n'.join((printable_key(k) for k in missing_keys))
        
        out_summary += 'Mismatched columns:\n'
        out_summary += '\n'.join(mismatch_columns)

        out_summary += '\n'
        out_summary += 'Mismatch records:\n'

        for k in mismatch_keys:
            out_summary += printable_key(k)
            for colname, val1, val2 in mismatch_col_details[k]:
                out_summary += f",{colname},{val1},{val2}\n"

        return (out_summary, mismatch_keys)

    summary, mismatch = get_comparison_summary(file1, file2, keyname)  # Destructure the result

    if outfile == None:         # Dump the output onto the console
        print(summary)
    else:                       # Write output to outfile
        with open(outfile, mode='w') as f:
            f.write(summary)
            f.close()

    if len(mismatch) == 0:      # If no mismatch, return 0
        return 0
    else:                       # else return 1
        return 1
