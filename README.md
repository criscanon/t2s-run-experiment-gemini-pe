# t2s-run-experiment-gemini-pe

This repository contains scripts and resources for running and analyzing SQL generation experiments with different prompts and models. The goal is to evaluate how accurately generative AI models can convert natural language questions (NLQs) into valid SQL queries and compare their performance across various metrics.

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Experiments](#running-the-experiments)
  - [1. run_experiment.py](#1-run_experimentpy)
  - [2. run_analysis.py](#2-run_analysispy)
  - [3. run_general_analysis.py](#3-run_general_analysispy)
- [Results](#results)
- [License](#license)

---

## Overview
This project focuses on converting **Natural Language Queries (NLQs)** into **SQL queries** using generative AI models. It includes scripts to:
- Run experiments using different prompts and models.
- Analyze the generated SQL in terms of syntax, semantics, and execution results.
- Produce summary metrics and visualizations of the experiment outcomes.

By following the steps in this repository, you can:
1. Perform multiple experiments (with different prompts/models).
2. Analyze each experiment’s results.
3. Compare experiments collectively with a final, general analysis.

---

## Installation
1. **Clone the repository**:
   ```sh
   git clone https://github.com/criscanon/t2s-run-experiment-gemini-pe.git
   cd t2s-run-experiment-gemini-pe
   ```
2. **Create and activate a virtual environment (recommended)**:
   ```sh
   python3 -m venv venv
   source venv/bin/activate   # On macOS/Linux
   # or
   venv\Scripts\activate      # On Windows
   ```
3. **Install the required dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

---

## Configuration
The **`config.json`** file contains important settings, such as:
- **`api_key_gemini`**: The API key used for the generative AI model.
- **`connection_string`**: The SQLAlchemy connection string to your database.
- **`dataset_excel_path`**: Path to the Excel file containing your NLQ-SQL pairs.
- **`output_path`**: Directory to store logs and results.
- **`<model_name>`**: The name or identifier for the model you wish to use.

Example of a minimal `config.json`:
```json
{
  "api_key_gemini": "<YOUR_API_KEY>",
  "gemini10": "google/generative-ai-model-name-1",
  "gemini15": "google/generative-ai-model-name-2",
  "connection_string": "sqlite:///database/example.db",
  "dataset_excel_path": "dataset/nlq_sql_pairs.xlsx",
  "output_path": "findings/"
}
```
Make sure to adjust each field to match your environment and requirements.

---

## Running the Experiments

### 1. run_experiment.py
- **Purpose**: Executes an experiment by:
  - Reading a set of NLQs and their expected SQL queries.
  - Generating SQL from a chosen model and comparing it to the expected SQL.
  - Logging all attempts, successes, and errors.
  - Saving the raw experiment results in an Excel file inside the `findings/` folder.

- **How to use**:
  1. Open `experiments.py` and define or check the experiments you want to run (their ID, model, prompt, etc.).
  2. In `run_experiment.py`, set the `id_experiment` to the ID of the experiment you wish to run.
  3. Run:
     ```sh
     python run_experiment.py
     ```
  4. After completion, check the `findings/` folder for the generated `*_res.xlsx` file and log file.

**Important**: Repeat this step **for each experiment** you want to conduct.

### 2. run_analysis.py
- **Purpose**: Analyzes the results of a single experiment by:
  - Comparing the expected SQL with the generated SQL.
  - Classifying errors (syntactic, semantic, etc.).
  - Calculating match rates for queries, rows, and columns.
  - Producing an Excel file with detailed analysis in the `results/` folder.

- **How to use**:
  1. Set the same `id_experiment` used in the previous step (or the one you want to analyze) inside `run_analysis.py`.
  2. Run:
     ```sh
     python run_analysis.py
     ```
  3. Check the `results/` folder for the `*_analysis.xlsx` file.

**Important**: Repeat this step **for each experiment** whose results you want to analyze.

### 3. run_general_analysis.py
- **Purpose**: Consolidates and compares the analysis from multiple experiments. Generates plots and metrics to help you visualize and compare different experiments side-by-side.

- **How to use**:
  1. Modify the parameters inside `run_general_analysis.py` (e.g., which models or experiment names to load).
  2. Run:
     ```sh
     python run_general_analysis.py
     ```
  3. Visualizations and comparison results will be saved into the `images/` folder. This script also reads from the `results/` folder to gather each experiment’s analysis summary.

---

## Results
- **`findings/`**: Contains raw experiment outputs (e.g., `experiment_name_res.xlsx`) for each run.
- **`results/`**: Contains analyzed data (e.g., `experiment_name_analysis.xlsx`) for each experiment.
- **`images/`**: Stores charts and plots produced by the general analysis script.

Use these outputs to:
- Compare how well each model or prompt performed.
- Check error classifications and reasons for SQL generation failures.
- Evaluate metrics like match rate (SQL syntax, returned rows/columns, etc.) and execution time.

---

## License
This project is released under the [MIT License](LICENSE) (or add your chosen license here). Feel free to use and adapt the code according to its terms.

---
