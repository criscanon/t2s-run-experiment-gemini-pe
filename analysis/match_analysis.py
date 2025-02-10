# Function to calculate matches
def calculate_sql_matches(row, inf_sql_col, exp_sql_col):
    return row[inf_sql_col] == row[exp_sql_col]

def calculate_result_matches(row, inf_response_col, exp_response_col):
    return row[inf_response_col] == row[exp_response_col]

def calculate_record_matches(row, inf_response_col, exp_response_col):
    return len(row[inf_response_col]) == len(row[exp_response_col])

def calculate_column_matches(row, inf_response_col, exp_response_col):
    if len(row[inf_response_col]) > 0 and len(row[exp_response_col]) > 0:
        return len(row[inf_response_col][0]) == len(row[exp_response_col][0])
    return False