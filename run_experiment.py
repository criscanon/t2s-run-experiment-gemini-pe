import re
import time
import json
import pandas as pd
import google.generativeai as genai
from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.schema import CreateTable
from prompts_to_use import prompts
from experiments import experiments

id_experiment = "4-2"
experiment_name = experiments[id_experiment]["name"]

# Load configuration from JSON file
with open('config.json', 'r') as f:
    config = json.load(f)

# Configuration variables
log_file_path = config['output_path'] + experiment_name + '_log.txt'
output_excel_path = config['output_path'] + experiment_name + '_res.xlsx'
num_records = 80
num_repetitions = 3
max_retries = 10
time_delay_between_retries = 2
time_delay_between_inferences = 2

# Configuration from JSON
api_key = config['api_key_gemini']
model_name = config[experiments[id_experiment]["model"]]
connection_string = config['connection_string']

# Configure the generative AI model
genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name)

# Prompt template for generating SQL queries
prompt_to_use = prompts[experiments[id_experiment]["prompt"]]

# Connect to the SQLite database using SQLAlchemy
engine = create_engine(connection_string)
metadata = MetaData()
metadata.reflect(engine)
tables = ', '.join(metadata.tables.keys())
dialect = engine.dialect.name

# Get the construction statements for each table
schema_statements = []
for table_name in metadata.tables:
    table = Table(table_name, metadata, autoload_with=engine)
    ddl = CreateTable(table).compile(engine)
    schema_statements.append(str(ddl))

# Join all construction statements into a single string
schema = '\n\n'.join(schema_statements)

# Ensure there is only two newline between each statement
schema = '\n'.join(filter(None, schema.split('\n\n')))

def get_table_info(engine_url):
    # Create the database engine
    engine = create_engine(engine_url)
    
    # Reflect the database tables
    metadata = MetaData()
    metadata.reflect(engine)
    
    output_string = ""

    # Retrieve table creation statements and the first 3 rows of each table
    with engine.connect() as connection:
        for table_name in metadata.tables:
            table = Table(table_name, metadata, autoload_with=engine)
            
            # Get the table creation statement
            ddl = CreateTable(table).compile(engine)
            output_string += f"\nTable schema for {table_name}:\n{ddl}\n"
            
            # Get column names
            columns = table.c
            
            # Build header with column names
            column_names = [column.name for column in columns]
            header = "\t".join(column_names)
            output_string += f"First 3 rows of {table_name}:\n{header}\n"
            
            # Get the first 3 rows of the table
            query = select(columns).limit(3)
            result = connection.execute(query).fetchall()
            
            # Append rows to the output string
            for row in result:
                row_values = "\t".join(str(value) for value in row)
                output_string += f"{row_values}\n"
    
    return output_string

table_info = get_table_info(connection_string)

# Read the Excel dataset with NLQs and expected SQL queries
data = pd.read_excel(config['dataset_excel_path']).head(num_records)
#data = pd.read_excel(config['dataset_excel_path'], nrows=9).tail(1)

# Extract NLQs and SQL queries from the dataset
nlq_values = data['nlq']
sql_values = data['sql'].apply(lambda sql: ' '.join(sql.replace('\n', ' ').split()))

# Function to execute SQL query and return results with timing
def execute_query(query, engine):
    start_time = time.perf_counter()
    try:
        result_df = pd.read_sql_query(query, engine)
        result = result_df.values.tolist()
        error = "No error."
    except Exception as e:
        result = [[-1]]
        error = str(e).strip().splitlines()[:2]
    end_time = time.perf_counter()
    execution_time_ms = (end_time - start_time) * 1000  # Convert to milliseconds
    return result, error, execution_time_ms

# List to store experiment results
results = []

# Open a log file to record details of the experiment
with open(log_file_path, 'w') as log_file:
    log_file.write(f"Experiment started at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    log_file.write(f"Experiment ID: {id_experiment}\n")
    log_file.write(f"Experiment name: {experiment_name}\n")
    log_file.write(f"Model used: {model_name}\n")
    log_file.write(f"Number of records: {num_records}\n")
    log_file.write(f"Number of repetitions: {num_repetitions}\n\n")

    print(f"Running experiment {id_experiment}: {experiment_name}")

    # Iterate over each row in the DataFrame
    for index, (nlq, sql) in enumerate(zip(nlq_values, sql_values)):
        print(f"\rProcessing NLQ {index + 1}/{num_records}...", end='', flush=True)

        result_entry = {'nlq': nlq, 'exp_sql': sql}

        # Execute the expected SQL query and get the result
        exp_result, exp_error, exp_time = execute_query(sql, engine)
        result_entry.update({
            'exp_response': exp_result,
            'exp_error': exp_error,
            'exp_time_ms': exp_time
        })

        # Repeat the inference and execution process
        for i in range(1, num_repetitions + 1):
            print(f"\rProcessing NLQ {index + 1}/{num_records}, Repetition {i}/{num_repetitions}...", end='', flush=True)

            # Complete the prompt with dialect and table names
            prompt_completed = prompt_to_use.format(dialect=dialect, tables=tables, nlq=nlq, schema=schema, table_info=table_info)
            
            # Initialize retry counter
            retries = 0

            while retries < max_retries:
                # Generate content using the prompt and measure time
                start_time = time.perf_counter()
                response = model.generate_content(prompt_completed)
                end_time = time.perf_counter()
                inf_time_ms = (end_time - start_time) * 1000  # Convert to milliseconds
                
                # Add inference time delay
                time.sleep(time_delay_between_inferences)

                try:
                    # Validate if response contains a valid `Part` before accessing `text`
                    if hasattr(response, 'text') and response.text.strip():
                        # Extract inferred SQL query without `sql` at the beginning and end, and without consecutive spaces
                        inferred_sql = response.text.strip().replace('\n', ' ')

                        # Remove backticks, 'sql', 'sqlite', and extra spaces
                        inferred_sql = re.sub(r'[`]+', '', inferred_sql)
                        inferred_sql = re.sub(r'\bsql\b', '', inferred_sql)
                        inferred_sql = re.sub(r'\bsqlite\b', '', inferred_sql)

                        # Remove extra spaces and double semicolons
                        inferred_sql = re.sub(r'\s+', ' ', inferred_sql).strip()
                        inferred_sql = re.sub(r';\s*;', ';', inferred_sql)
                        break  # Exit the loop if a valid value is obtained

                    else:
                        # Raise an error if response.text is not valid
                        raise ValueError("Invalid response text or response does not contain a valid `Part`")

                except ValueError as e:
                    # Increment retry counter
                    retries += 1
                    # Add retry time delay
                    time.sleep(time_delay_between_retries)

            # If no valid value is obtained after the retries, assign an error message
            if retries == max_retries:
                inferred_sql = "Error: No valid SQL generated."
            
            # Execute the inferred SQL query and get the result
            inf_result, inf_error, inf_exec_time_ms = execute_query(inferred_sql, engine)
            
            # Add inferred SQL and results to the entry
            result_entry.update({
                f'inf_sql_{i}': inferred_sql,
                f'inf_response_{i}': inf_result,
                f'inf_error_{i}': inf_error,
                f'inf_time_ms_{i}': inf_time_ms,
                f'inf_exec_time_ms_{i}': inf_exec_time_ms
            })
        
        results.append(result_entry)

    log_file.write(f"NLQ: {nlq}\n\n")
    log_file.write(f"Prompt: {prompt_completed}\n\n")
    log_file.write(f"{repr(response)}\n\n")

# Create a DataFrame with the results
summary_table = pd.DataFrame(results)

# Export the DataFrame to a new Excel file
summary_table.to_excel(output_excel_path, index=False)
print("\nSuccessful experiment...")

# Log the end time of the experiment
with open(log_file_path, 'a') as log_file:
    log_file.write(f"Experiment ended at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
