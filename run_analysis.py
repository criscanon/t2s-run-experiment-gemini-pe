import pandas as pd
import numpy as np
import ast

from experiments import experiments
from analysis.error_analysis import classify_sqlite_error
from analysis.match_analysis import calculate_sql_matches, calculate_result_matches, calculate_record_matches, calculate_column_matches
from analysis.consistency import compare_inf_sql

NUM_ITERATIONS = 3
id_experiment = "6-2"
experiment_name = experiments[id_experiment]["name"]
input_excel_path = 'findings/' + experiment_name + '_res.xlsx'
output_analysis_path = 'results/' + experiment_name + '_analysis.xlsx'

# Read the input Excel file
data = pd.read_excel(input_excel_path)

# Function to convert strings to lists of lists
def str_to_list(s):
    try:
        return ast.literal_eval(s)
    except (ValueError, SyntaxError) as e:
        print(f"Error converting string to list: {e}")
        return []

# Convert response columns from strings to lists of lists
response_columns = ['exp_response', 'inf_response_1', 'inf_response_2', 'inf_response_3']
for col in response_columns:
    data[col] = data[col].apply(str_to_list)

# Calculate matches, errors, and times
for i in range(1, NUM_ITERATIONS + 1):
    # Calculate match columns
    data[f'match_sql_{i}'] = data.apply(lambda row: calculate_sql_matches(row, f'inf_sql_{i}', 'exp_sql'), axis=1)
    data[f'match_result_{i}'] = data.apply(lambda row: calculate_result_matches(row, f'inf_response_{i}', 'exp_response'), axis=1)
    data[f'match_rows_{i}'] = data.apply(lambda row: calculate_record_matches(row, f'inf_response_{i}', 'exp_response'), axis=1)
    data[f'match_columns_{i}'] = data.apply(lambda row: calculate_column_matches(row, f'inf_response_{i}', 'exp_response'), axis=1)

    # Classify errors and create new columns for them
    data[f'category_error_{i}'] = data[f'inf_error_{i}'].apply(classify_sqlite_error)

# Calculate consistency
data['consistency'] = data.apply(compare_inf_sql, axis=1)

# Calculate and export metrics
match_metrics = {
    'match_sql': [data[f'match_sql_{i}'].sum() for i in range(1, NUM_ITERATIONS + 1)],
    'match_result': [data[f'match_result_{i}'].sum() for i in range(1, NUM_ITERATIONS + 1)],
    'match_rows': [data[f'match_rows_{i}'].sum() for i in range(1, NUM_ITERATIONS + 1)],
    'match_columns': [data[f'match_columns_{i}'].sum() for i in range(1, NUM_ITERATIONS + 1)]
}

# Calculate percentages
total_rows = len(data)
match_metrics_percent = {
    'match_sql_percent': [round((m / total_rows) * 100, 2) for m in match_metrics['match_sql']],
    'match_result_percent': [round((m / total_rows) * 100, 2) for m in match_metrics['match_result']],
    'match_rows_percent': [round((m / total_rows) * 100, 2) for m in match_metrics['match_rows']],
    'match_columns_percent': [round((m / total_rows) * 100, 2) for m in match_metrics['match_columns']]
}

# Prepare error analysis data
error_combined = {
    'Iteration': [f'Iteration {i}' for i in range(1, NUM_ITERATIONS + 1)]
}

error_types = ['Syntactic', 'Semantic', 'Unknown', 'No error.']
error_counts = {f'Iteration {i}': {error: 0 for error in error_types} for i in range(1, NUM_ITERATIONS + 1)}

for i in range(1, NUM_ITERATIONS + 1):
    error_series = data[f'category_error_{i}']
    for error in error_series:
        if error in error_counts[f'Iteration {i}']:
            error_counts[f'Iteration {i}'][error] += 1

for error in error_types:
    error_combined[f'{error} Count'] = [error_counts[f'Iteration {i}'][error] for i in range(1, NUM_ITERATIONS + 1)]
    error_combined[f'{error} Percentage'] = [round((error_counts[f'Iteration {i}'][error] / total_rows) * 100, 2) for i in range(1, NUM_ITERATIONS + 1)]

# Function to calculate statistics
def calculate_statistics(times):
    return {
        'mean': round(np.mean(times), 2),
        'median': round(np.median(times), 2),
        'std_dev': round(np.std(times), 2)
    }

# Calculate statistics for times
inf_times = [data[f'inf_time_ms_{i}'] for i in range(1, NUM_ITERATIONS + 1)]
exec_times = [data[f'inf_exec_time_ms_{i}'] for i in range(1, NUM_ITERATIONS + 1)]

inf_stats = [calculate_statistics(times) for times in inf_times]
exec_stats = [calculate_statistics(times) for times in exec_times]

# Calculate averages across iterations
avg_metrics = {
    # Match metrics (average of percentages)
    'avg_match_sql': round(np.mean(match_metrics_percent['match_sql_percent']), 2),
    'avg_match_result': round(np.mean(match_metrics_percent['match_result_percent']), 2),
    'avg_match_rows': round(np.mean(match_metrics_percent['match_rows_percent']), 2),
    'avg_match_columns': round(np.mean(match_metrics_percent['match_columns_percent']), 2),
    
    # Error metrics (average of percentages)
    'avg_syntactic_error': round(np.mean(error_combined['Syntactic Percentage']), 2),
    'avg_semantic_error': round(np.mean(error_combined['Semantic Percentage']), 2),
    'avg_unknown_error': round(np.mean(error_combined['Unknown Percentage']), 2),
    'avg_no_error': round(np.mean(error_combined['No error. Percentage']), 2),
    
    # Time statistics (average of averages)
    'avg_inference_mean': round(np.mean([stat['mean'] for stat in inf_stats]), 2),
    'avg_execution_mean': round(np.mean([stat['mean'] for stat in exec_stats]), 2),
    
    # Consistency (count of each category)
    'count_consistency_all_equal': sum(data['consistency'].apply(lambda x: 1 if x == 'all_equal' else 0)),
    'count_consistency_two_equal': sum(data['consistency'].apply(lambda x: 1 if x == 'two_equal' else 0)),
    'count_consistency_all_different': sum(data['consistency'].apply(lambda x: 1 if x == 'all_different' else 0))
}

# Prepare summary data
summary_data = pd.DataFrame({
    'Metric': [
        'Average Match SQL (%)', 'Average Match Result (%)', 'Average Match Rows (%)', 'Average Match Columns (%)',
        'Average Syntactic Errors (%)', 'Average Semantic Errors (%)', 'Average Unknown Errors (%)', 'Average No Errors (%)',
        'Average Inference Mean', 'Average Execution Mean',
        'Count Consistency (All Equal)', 'Count Consistency (Two Equal)', 'Count Consistency (All Different)'
    ],
    id_experiment: [
        avg_metrics['avg_match_sql'], avg_metrics['avg_match_result'], avg_metrics['avg_match_rows'], avg_metrics['avg_match_columns'],
        avg_metrics['avg_syntactic_error'], avg_metrics['avg_semantic_error'], avg_metrics['avg_unknown_error'], avg_metrics['avg_no_error'],
        avg_metrics['avg_inference_mean'], avg_metrics['avg_execution_mean'],
        avg_metrics['count_consistency_all_equal'], avg_metrics['count_consistency_two_equal'], avg_metrics['count_consistency_all_different']
    ]
})

# Export to Excel with separate sheets for matches, errors, times, consistency, and summary metrics
with pd.ExcelWriter(output_analysis_path) as writer:
    # Write the original data to the first sheet
    data.to_excel(writer, sheet_name='Original Data', index=False)
    
    # Write match metrics to a new sheet
    match_data = pd.DataFrame({
        'Iteration': [f'Iteration {i}' for i in range(1, NUM_ITERATIONS + 1)],
        'Match SQL': match_metrics['match_sql'],
        'Match SQL %': match_metrics_percent['match_sql_percent'],
        'Match Result': match_metrics['match_result'],
        'Match Result %': match_metrics_percent['match_result_percent'],
        'Match Rows': match_metrics['match_rows'],
        'Match Rows %': match_metrics_percent['match_rows_percent'],
        'Match Columns': match_metrics['match_columns'],
        'Match Columns %': match_metrics_percent['match_columns_percent']
    })
    match_data.to_excel(writer, sheet_name='Matches', index=False)

    # Write error metrics to a new sheet
    error_df = pd.DataFrame(error_combined)
    error_df.to_excel(writer, sheet_name='Errors', index=False)

    # Write time statistics to a new sheet
    times_df = pd.DataFrame({
        'Iteration': [f'Iteration {i}' for i in range(1, NUM_ITERATIONS + 1)],
        'Inference Mean': [stat['mean'] for stat in inf_stats],
        'Execution Mean': [stat['mean'] for stat in exec_stats]
    })
    times_df.to_excel(writer, sheet_name='Times', index=False)
    
   # Write consistency analysis to a new sheet
    consistency_data = pd.DataFrame(data['consistency'].value_counts()).reset_index()
    consistency_data.columns = ['Consistency', 'Count']
    consistency_data['Percentage'] = round((consistency_data['Count'] / total_rows) * 100, 2)
    consistency_data.to_excel(writer, sheet_name='Consistency', index=False)
    
    # Write summary metrics to a new sheet
    summary_data.to_excel(writer, sheet_name='Summary Metrics', index=False)

print(f"Analysis exported to {output_analysis_path}")
