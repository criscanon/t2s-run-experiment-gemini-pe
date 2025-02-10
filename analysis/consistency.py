# Function to determine the condition
def compare_inf_sql(row):
    if row['inf_sql_1'] == row['inf_sql_2'] == row['inf_sql_3']:
        return 'all_equal'
    elif row['inf_sql_1'] == row['inf_sql_2'] or row['inf_sql_1'] == row['inf_sql_3'] or row['inf_sql_2'] == row['inf_sql_3']:
        return 'two_equal'
    else:
        return 'all_different'