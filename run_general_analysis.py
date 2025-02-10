import pandas as pd
import glob
import matplotlib.pyplot as plt
import seaborn as sns

# Parametrize paradigm and experiment names
paradigm = 'Prompt Engineering'

def read_experiment_metrics(directory, experiment_name):
    """
    Reads the metrics of a specific experiment from Excel files in a directory.
    Returns a DataFrame with the organized metrics.
    """
    excel_files = glob.glob(f'{directory}/*{experiment_name}*.xlsx')
    
    dfs = []
    for file in excel_files:
        df = pd.read_excel(file, sheet_name='Summary Metrics', index_col=0)
        dfs.append(df)
    
    return pd.concat(dfs, axis=1)

def plot_and_save(df, experiment_name, metrics, filename):
    """
    Creates an individual plot for specific metrics and saves it as an image.
    """
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(6, 5))

    # More vibrant color palette without repetition
    num_metrics = len(df)
    colors = sns.color_palette("pastel", n_colors=num_metrics, desat=1)
    
    # Bar chart generation
    df.loc[metrics].plot(kind='bar', rot=45, ax=ax, color=colors, edgecolor='black', linewidth=1)
    
    # Title, labels, and axis limits adjustment
    ax.set_title(f'{experiment_name} - {paradigm}')
    ax.set_xlabel('')
    if metrics == ['Average Inference Mean']:
        ax.set_ylabel('Time (ms)')
    else:
        ax.set_ylabel('Percentage (%)')

    ax.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    # Set max y-axis limit to 100 for percentage metrics
    if metrics == ['Average Inference Mean']:
        ax.set_ylim(0, 4600)
    else:
        ax.set_ylim(0, 100)
    
    # Save the image with tight layout
    plt.tight_layout()
    plt.savefig(filename, bbox_inches='tight')
    plt.close(fig)  # Close the figure to free up memory

def plot_comparison_subplot(df, experiment_name, metrics_list, filename):
    """
    Creates subplots for multiple metrics and saves them as an image.
    """
    # Create figure and axes
    fig, axs = plt.subplots(nrows=1, ncols=3, figsize=(18, 5))

    for ax, metrics in zip(axs, metrics_list):
        # More vibrant color palette without repetition
        num_metrics = len(df)
        colors = sns.color_palette("pastel", n_colors=num_metrics, desat=1)

        # Bar chart generation
        df.loc[metrics].plot(kind='bar', rot=45, ax=ax, color=colors, edgecolor='black', linewidth=1)

        # Title, labels, and axis limits adjustment
        ax.set_title(f'{experiment_name} - {paradigm}')
        ax.set_xlabel('')
        if metrics == ['Average Inference Mean']:
            ax.set_ylabel('Time (ms)')
        else:
            ax.set_ylabel('Percentage (%)')

        ax.grid(True, axis='y', linestyle='--', alpha=0.7)

        # Set max y-axis limit to 100 for percentage metrics
        if metrics == ['Average Inference Mean']:
            ax.set_ylim(0, 4600)
        else:
            ax.set_ylim(0, 100)

    # Save the image with tight layout
    plt.tight_layout()
    plt.savefig(filename, bbox_inches='tight')
    plt.close(fig)  # Close the figure to free up memory

# Directory where the Excel files are located
directory = 'results'

# Experiment models to be used as parameters (can be changed)
short_model_1 = 'gemini10'
complete_model_1 = 'Gemini 1.0 Pro'
short_model_2 = 'gemini15'
complete_model_2 = 'Gemini 1.5 Pro'

# Read experiment metrics for model_1
model_1_metrics = read_experiment_metrics(directory, short_model_1)
print(model_1_metrics)

# Read experiment metrics for model_2
model_2_metrics = read_experiment_metrics(directory, short_model_2)
print(model_2_metrics)

# Specific metrics by category
matches_metrics = ['Average Match SQL (%)', 'Average Match Result (%)', 'Average Match Rows (%)', 'Average Match Columns (%)']
errors_metrics = ['Average Syntactic Errors (%)', 'Average Semantic Errors (%)', 'Average Unknown Errors (%)', 'Average No Errors (%)']
times_inferences_metrics = ['Average Inference Mean']

# Save individual plots for model_1
plot_and_save(model_1_metrics, f'Matches - {complete_model_1}', matches_metrics, f'images/{short_model_1.lower()}_matches.png')
plot_and_save(model_1_metrics, f'Errors - {complete_model_1}', errors_metrics, f'images/{short_model_1.lower()}_errors.png')
plot_and_save(model_1_metrics, f'Performance - {complete_model_1}', times_inferences_metrics, f'images/{short_model_1.lower()}_inferences.png')

# Save individual plots for model_2
plot_and_save(model_2_metrics, f'Matches - {complete_model_2}', matches_metrics, f'images/{short_model_2.lower()}_matches.png')
plot_and_save(model_2_metrics, f'Errors - {complete_model_2}', errors_metrics, f'images/{short_model_2.lower()}_errors.png')
plot_and_save(model_2_metrics, f'Performance - {complete_model_2}', times_inferences_metrics, f'images/{short_model_2.lower()}_inferences.png')

# Save subplots for model_1
plot_comparison_subplot(model_1_metrics, complete_model_1, 
                        [matches_metrics, errors_metrics, times_inferences_metrics], 
                        f'images/{short_model_1.lower()}_comparison.png')

# Save subplots for model_2
plot_comparison_subplot(model_2_metrics, complete_model_2, 
                        [matches_metrics, errors_metrics, times_inferences_metrics], 
                        f'images/{short_model_2.lower()}_comparison.png')
