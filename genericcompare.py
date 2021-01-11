import csv


def get_comparison(input1, input2, keyname, outfile, input1name=None, input2name=None, input_type='csv'):

    def convert_to_dict(input, pk, input_type):

        #################################################################################################
        # THIS CONVERTS ANY GIVEN FORMAT OF DATA INTO A DICTIONARY OF DICTIONARIES                      #
        # WHERE THE KEY IS THE PRIMARY KEY AND THE VALUE IS THE DICTIONARY OF KEY,VALUES FOR            #
        # THE CORRESPONDING PRIMARY KEY.                                                                #
        # FOR EXAMPLE:                                                                                  #
        # SERIAL    |   NAME    |   AGE                                                                 #
        # --------------------------------                                                              #
        # 1         |   ANDY    |   30                                                                  #
        # WOULD BECOME  {1:{'SERIAL': 1, 'NAME' : 'ANDY', 'AGE' : 30}} IF SERIAL IS PKEY                #
        #################################################################################################

        if input_type == 'csv':
            return convert_csv(input, pk)
        elif input_type == 'dict_list':
            return convert_dict_list(input, pk)
        elif input_type == 'tuple_list':
            return convert_tuple_list(input, pk)
        else:
            raise Exception("Input Type not supported yet! Sorry :(")

    def convert_csv(fpath, pk):

        #################################################################################################
        # TAKES IN A CSV AND RETURNS DICTIONARY OF DICTIONARY, AS IS NEEDED                             #
        #################################################################################################

        with open(fpath, mode='r') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',')
            reader.fieldnames = [fieldname.upper()
                                 for fieldname in reader.fieldnames]

            if isinstance(pk, str):     # Primary key is a string
                pkey = pk.upper()
                if pkey not in reader.fieldnames:
                    raise Exception(
                        "The primary key does not match any header. Sorry :(")
                content_dict = {row[pkey]: row for row in reader}
            else:                       # Primary key is composite
                pkey = [k.upper() for k in pk]
                if not all((k in reader.fieldnames for k in pkey)):
                    raise Exception(
                        "The primary key does not match any header. Sorry :(")
                content_dict = {tuple(row[k]
                                      for k in pkey): row for row in reader}

            csvfile.close()
            return content_dict

    def convert_dict_list(input_dict_list, pk):

        #################################################################################################
        # IMPORTANT NOTE: THIS CODE ASSUMES ALL THE DICTS IN THE INPUT LIST HAS THE SAME SET OF KEYS.   #
        # IF THAT IS NOT THE CASE, THEN ADDITIONAL VERIFICATION NEEDS TO BE DONE.                       #
        # THIS CODE RUNS IN GOOD FAITH THAT THE KEYS IN THE FIRST ENTRY OF THE LIST                     #
        # ARE THE ONES AND ONLY ONES PRESENT IN ALL OTHER ENTRIES TOO.                                  #
        #################################################################################################

        # CONVERT ALL KEYS TO UPPERCASE FOR ALL ENTRIES
        formatted_list = [{k.upper(): v for k, v in dict_entry.items()}
                          for dict_entry in input_dict_list]
        
        if len(formatted_list) == 0:
            raise Exception("Empty list provided!)

        if isinstance(pk, str):     # primary key is a string
            pkey = pk.upper()
            if pkey not in formatted_list[0]:
                raise Exception(
                    "The primary key does not match any header. Sorry :(")
            content_dict = {row[pkey]: row for row in formatted_list}

        else:                       # primary key is composite
            pkey = [k.upper() for k in pk]
            if not all((k in formatted_list[0] for k in pkey)):
                raise Exception(
                    "The primary key does not match any header. Sorry :(")
            content_dict = {tuple(row[k] for k in pkey): row for row in formatted_list}

        return content_dict

    def convert_tuple_list(input_tuple_list, pk):
        #################################################################################################
        # IMPORTANT NOTE: THIS CODE ASSUMES THE TUPLE CONTAINS THE KEYS.                                #
        # IF THAT IS NOT THE CASE, THEN THE CODE WILL FAIL MISERABLY.                                   #
        # ALSO, ALL THE TUPLES NEED TO HAVE THE SAME LENGTH AND ORDER, OBVIOUSLY.                       #
        #################################################################################################

        headers = input_tuple_list[0]

        # TRANSFORM GIVEN DATA TO A LIST OF DICTS
        dict_list = [{headers[index]: val for index, val in enumerate(entry)}
                     for entry in input_tuple_list[1:]]

        # REUSE THE CODE FOR DICT LIST
        return convert_dict_list(dict_list, pk)

    def compare_mismatch_rows(row1, row2):
        #################################################################################################
        # GIVEN TWO DICTS, RETURNS THE MISMATCHES                                                       #
        # RETURN FORMAT IS A LIST                                                                       #
        # EACH ELEMENT OF THE LIST HAS THE FOLLOWING STRUCTURE: <KEYNAME>, <VAL_DICT1>, <VAL_DICT2>     #
        #################################################################################################
        keys = [k for k in row1]
        mismatch = [(k, row1[k], row2[k])
                    for k in keys if row1[k] != row2[k]]
        return mismatch

    def get_comparison_details(d1, d2):
        #################################################################################################
        # GIVEN TWO DICTS, RETURNS A DICTIONARY WITH COMPARISON                                         #
        # RETURNED DICT HAS FOLLOWING KEYS:                                                             #
        # missing_keys, mismatch_keys, mismatch_columns, mismatch_col_details                           #
        # missing_keys : KEYS IN d1 BUT MISSING IN d2                                                   #
        # mismatch_keys : KEYS FOR WHICH VALUES OF d1 AND d2 DO NOT MATCH                               #
        # mismatch_columns : COLUMN NAMES FOR WHICH SOME VALUES OF d1 AND d2 DO NOT MATCH               #
        # mismatch_col_details : DICT OF COLUMNS AND VALUES FOR WHICH d1 AND d2 DO NOT MATCH            #
        # NOTE: THE THING I DISLIKE IS mismatch_keys IS COMPLETELY REDUNDANT AND CAN BE CALCULATED      #
        # FROM mismatch_col_details.keys()                                                              #
        #################################################################################################

        missing_keys = [key for key in d1 if key not in d2]
        mismatch_keys = [key for key in d1
                         if key in d2
                         and d1[key] != d2[key]]
        mismatch_columns = set()
        mismatch_col_details = dict()

        for k in mismatch_keys:
            mismatch_details = compare_mismatch_rows(d1[k], d2[k])
            mismatch_col_details[k] = mismatch_details
            mismatch_columns = mismatch_columns | {
                colname for colname, *_ in mismatch_details}

        return {'missing_keys': missing_keys,
                'mismatch_keys': mismatch_keys,
                'mismatch_columns': mismatch_columns,
                'mismatch_col_details': mismatch_col_details}

    def get_comparison_summary(d1, d2, d1name, d2name):

        #################################################################################################
        #   THIS FUNCTION TAKES IN TWO DICTS THAT IS PROPERLY FORMATTED, AND SPITS OUT                  #
        #   A PRINTABLE SUMMARY OF THE COMPARISON, ALONG WITH MISMATCHED KEYS.                          #
        #   d1name AND d2name ARE REQUIRED FOR NAMING COMPARISONS IN THE SUMMARY.                       #
        #################################################################################################

        def printable_key(key):
            return key if isinstance(key, str) else ";".join((str(k) for k in key))

        comparison_details = get_comparison_details(d1, d2)
        missing_keys = comparison_details['missing_keys']
        mismatch_keys = comparison_details['mismatch_keys']
        mismatch_columns = comparison_details['mismatch_columns']
        mismatch_col_details = comparison_details['mismatch_col_details']

        out_summary = f'Comparing {d1name} to {d2name}\n'

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

        return {'summary': out_summary, 'mismatch_keys': mismatch_keys}

    #################################################################################################
    # IT STARTS HERE. FIRST THE INPUTS ARE CONVERTED TO DICTIONARY.                                 #
    # AND THEN THE NAMES ARE SET. NAMES ARE NECESSARY FOR THE SUMMARY.                              #
    # THEN COMPARISON SUMMARY IS CALLED WHICH TAKES CARE OF THE REST.                               #
    #################################################################################################

    d1 = convert_to_dict(input1, keyname, input_type)
    d2 = convert_to_dict(input2, keyname, input_type)

    if input_type == 'csv':
        if ((input1name == None) | (input2name == None)):
            d1name = input1
            d2name = input2
    else:
        if ((input1name == None) | (input2name == None)):
            d1name = 'LEFT'
            d2name = 'RIGHT'

    comparison_summary = get_comparison_summary(d1, d2, d1name, d2name)
    summary = comparison_summary['summary']
    mismatch = comparison_summary['mismatch_keys']

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


#######################################################################################
# HOW TO USE WITH cx_Oracle:
# ...
# headers = [col[0] for col in cur.description]
# rows1 = list(cur.fetchall())
# rows2 = list(cur.fetchall())
# if len(rows1) == 0 | len(rows2) == 0:
#       print("skipping")
# else:
#       tuple_list1 = [headers, *rows]
#       make a similar one called tuple_list2
#       call get_comparison with    tuple_list1 as input1,
#                                   tuple_list2 as input2,
#                                   'tuple_list' as input_type
#######################################################################################
