import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os

def read_covid_data(file_path='/tmp/covid_summary.json'):
    """
    Read COVID data from JSON file.
    
    Args:
        file_path (str): Path to the COVID summary JSON file
        
    Returns:
        dict: COVID data with keys 'cases', 'deaths', 'recovered', 'updated'
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"COVID data file not found: {file_path}")
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    return data

def create_barcode_plot(covid_data, output_path=None):
    """
    Create a barcode plot from COVID data.
    
    Args:
        covid_data (dict): COVID data with keys 'cases', 'deaths', 'recovered', 'updated'
        output_path (str): Path to save the PNG file. If None, auto-generates based on date.
        
    Returns:
        str: Path to the saved PNG file
    """
    # Extract metrics
    cases = covid_data.get('cases', 0)
    deaths = covid_data.get('deaths', 0) 
    recovered = covid_data.get('recovered', 0)
    updated = covid_data.get('updated', datetime.now().timestamp() * 1000)
    
    # Convert timestamp to date string
    date_str = datetime.fromtimestamp(updated / 1000).strftime('%Y-%m-%d')
    
    # Generate output path if not provided
    if output_path is None:
        output_path = f'/tmp/covid_barcode_{date_str}.png'
    
    # Normalize values for barcode visualization (0-1 scale)
    max_value = max(cases, deaths, recovered)
    if max_value == 0:
        # Handle edge case where all values are 0
        normalized_cases = normalized_deaths = normalized_recovered = 0
    else:
        normalized_cases = cases / max_value
        normalized_deaths = deaths / max_value
        normalized_recovered = recovered / max_value
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Create barcode-style visualization
    # Each metric gets multiple bars to create a barcode pattern
    bar_width = 0.8
    num_bars_per_metric = 10
    
    # Generate positions for bars
    positions = []
    heights = []
    colors = []
    labels = []
    
    # Cases - Red bars
    for i in range(num_bars_per_metric):
        pos = i * 3 + 0  # Starting at 0, spacing of 3
        positions.append(pos)
        # Vary height slightly to create barcode pattern
        height = normalized_cases * (0.8 + 0.2 * np.sin(i))
        heights.append(height)
        colors.append('#FF4444')  # Red
        if i == num_bars_per_metric // 2:  # Label only the middle bar
            labels.append(f'Cases: {cases:,}')
        else:
            labels.append('')
    
    # Deaths - Black bars
    for i in range(num_bars_per_metric):
        pos = i * 3 + 1  # Offset by 1
        positions.append(pos)
        height = normalized_deaths * (0.8 + 0.2 * np.sin(i + 1))
        heights.append(height)
        colors.append('#000000')  # Black
        if i == num_bars_per_metric // 2:
            labels.append(f'Deaths: {deaths:,}')
        else:
            labels.append('')
    
    # Recovered - Green bars
    for i in range(num_bars_per_metric):
        pos = i * 3 + 2  # Offset by 2
        positions.append(pos)
        height = normalized_recovered * (0.8 + 0.2 * np.sin(i + 2))
        heights.append(height)
        colors.append('#44AA44')  # Green
        if i == num_bars_per_metric // 2:
            labels.append(f'Recovered: {recovered:,}')
        else:
            labels.append('')
    
    # Create the bar plot
    bars = ax.bar(positions, heights, width=bar_width, color=colors)
    
    # Customize the plot
    ax.set_title(f'COVID-19 Barcode Visualization - {date_str}', fontsize=16, fontweight='bold')
    ax.set_xlabel('Metrics Pattern', fontsize=12)
    ax.set_ylabel('Normalized Values', fontsize=12)
    ax.set_ylim(0, 1.1)
    
    # Add legend
    legend_elements = [
        plt.Rectangle((0,0),1,1, facecolor='#FF4444', label=f'Cases: {cases:,}'),
        plt.Rectangle((0,0),1,1, facecolor='#000000', label=f'Deaths: {deaths:,}'),
        plt.Rectangle((0,0),1,1, facecolor='#44AA44', label=f'Recovered: {recovered:,}')
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    
    # Add grid for better readability
    ax.grid(True, alpha=0.3, axis='y')
    
    # Remove x-axis ticks since this is a barcode pattern
    ax.set_xticks([])
    
    # Add text box with summary statistics
    total_population_affected = cases
    mortality_rate = (deaths / cases * 100) if cases > 0 else 0
    recovery_rate = (recovered / cases * 100) if cases > 0 else 0
    
    textstr = f'Total Cases: {cases:,}\nMortality Rate: {mortality_rate:.2f}%\nRecovery Rate: {recovery_rate:.2f}%'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props)
    
    # Tight layout and save
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Barcode plot saved to: {output_path}")
    return output_path

def main():
    """
    Main function to read COVID data and generate barcode plot.
    """
    try:
        # Read COVID data
        covid_data = read_covid_data()
        print(f"Successfully read COVID data: {covid_data}")
        
        # Generate barcode plot
        output_file = create_barcode_plot(covid_data)
        print(f"Barcode plot generated successfully: {output_file}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Make sure the COVID ETL DAG has run and created the data file.")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()