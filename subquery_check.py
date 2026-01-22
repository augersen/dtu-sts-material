"""
Subquery and Issue Filter - Find statements matching specific subqueries and issues
DTU - Explore the Energy Islands controversy

This script filters statements based on:
1. Handpicked subqueries (formulations) for different topics
2. Specific issue numbers (1-16)

It returns all statements that:
- Contain at least one of the specified subqueries AND
- Are tagged with the specified issue

Edit the configuration variables below and run the script.
"""

# ============================================================================
# CONFIGURATION - EDIT THESE VARIABLES
# ============================================================================

# Define your handpicked subqueries for each topic/query
# Format: {"Topic Name": ["subquery1", "subquery2", ...]}
TOPIC_SUBQUERIES = {
    "Social impact": [
        "Social impact",
        "Broad social"
    ],

    "Stakeholders": [
        "Stakeholders",
        "Bornholm",
        "Denmark",
        "The danish"
    ],

    "Communities": [
        "Bornholm",
        "North Sea",
        "Denmark",
        "Communities",
    ],

    "Housing": [
        "Housing"
    ],

    "Benefits": [
        "to the",
        "for the"
    ],

    "Job opportunities": [
        "New job",
        "Opportunities",
        "Job opportunities",
        "Jobs",
        "Work"
    ],

    "Local": [
        "Local"
    ],

    "Environmental Impact": [
        "Environmental Impact"
    ],

    "Social Impact": [
        "Social Impact"
    ],

    "Compensation": [
        "Compensation"
    ],

    "Esbjerg": [
        "Esbjerg"
    ]
}

# Select which issue to filter by (1-16)
# See "data/Issues coding.md" for issue descriptions
selected_issue = 11  # Issue 11: How will energy islands impact local communities?

# Filter out social media users (actors with "user" in their name)
# This excludes Reddit users, Facebook users, LinkedIn users, etc.
exclude_users = True

# Output folder for results
output_folder = "subquery checks"

# Show sample statements in console for each topic
show_sample_statements = True

# Number of sample statements to display in console
num_samples = 5

# ============================================================================
# DATA SOURCE CONFIGURATION
# ============================================================================

# Path to dataset (edit if needed)
DATASET_PATH = 'data/Actor statement dataset.csv'  # Local file
# DATASET_PATH = 'https://jacomyma.github.io/dtu-sts-material/data/Actor%20statement%20dataset.csv'  # Online

# ============================================================================
# ISSUE DESCRIPTIONS (for reference)
# ============================================================================

ISSUE_DESCRIPTIONS = {
    1: "Are investments in energy islands a good way to stimulate innovation and economic growth?",
    2: "Are energy islands the most cost-effective way to reach carbon emission targets?",
    3: "Is bureaucracy slowing down the energy island projects?",
    4: "What will the implications be of a new bidding zone for the electricity market?",
    5: "Will we have a stable energy supply?",
    6: "Will the European countries manage to cooperate around offshore energy hubs?",
    7: "Geopolitics and energy independence: Will the energy islands make our energy system more resilient or more fragile?",
    8: "How to finance the energy islands?",
    9: "Is nuclear power an alternative to energy islands?",
    10: "How will energy islands impact the marine environment?",
    11: "How will energy islands impact local communities?",
    12: "What are the current envisioned ideas of interplay between Power-to-X and energy islands?",
    13: "From cyber to sabotage - are energy islands a security risk?",
    14: "How sustainable are the building materials for the energy islands?",
    15: "How can High Voltage Direct Current (HVDC) technology be integrated into the electricity system?",
    16: "Are the energy islands socially and economically just?"
}

# ============================================================================
# MAIN CODE
# ============================================================================

import pandas as pd
import os
import re
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import Counter

def load_data(dataset_path):
    """Load and prepare the dataset"""
    print(f"Loading dataset from: {dataset_path}")
    df = pd.read_csv(dataset_path, dtype=str)
    df = df.fillna('')

    # Set 'Year' column to int
    df['Year'] = df['Year'].replace('', pd.NA)
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce').astype(pd.Int64Dtype())

    # Set 'X', 'Y' and 'Size' columns to float
    df['X'] = pd.to_numeric(df['X'], errors='coerce')
    df['Y'] = pd.to_numeric(df['Y'], errors='coerce')
    df['Size'] = pd.to_numeric(df['Size'], errors='coerce')

    print(f"✓ Data loaded: {len(df)} statements total\n")
    return df

def filter_out_users(df):
    """Filter out social media users (actors with 'user' in their name)"""
    initial_count = len(df)

    # Filter out rows where Actor contains 'user' (case-insensitive)
    df_filtered = df[~df['Actor'].str.contains('user', case=False, na=False)]

    filtered_count = initial_count - len(df_filtered)

    if filtered_count > 0:
        print(f"✓ Filtered out {filtered_count} statements from social media users")
        print(f"  Remaining statements: {len(df_filtered)}\n")
    else:
        print(f"✓ No social media users found to filter\n")

    return df_filtered

def filter_by_subqueries_and_issue(df, subqueries, issue_number):
    """
    Filter statements that match:
    - At least one of the subqueries AND
    - The specified issue
    """
    print("="*80)
    print("FILTERING STATEMENTS")
    print("="*80)
    print(f"Topic subqueries: {len(subqueries)} terms")
    print(f"Issue: {issue_number} - {ISSUE_DESCRIPTIONS.get(issue_number, 'Unknown')}")
    print()

    # Create regex pattern for subqueries (case-insensitive)
    pattern = '|'.join(re.escape(sq) for sq in subqueries)

    # Filter by subqueries
    print("Step 1: Filtering by subqueries...")
    subquery_condition = df['Statement'].str.contains(pattern, case=False, na=False, regex=True)
    subquery_matches = df[subquery_condition]
    print(f"  ✓ Found {len(subquery_matches)} statements matching subqueries")

    # Filter by issue
    print(f"\nStep 2: Filtering by Issue_{issue_number}...")
    issue_column = f'Issue_{issue_number}'

    if issue_column not in df.columns:
        print(f"  ✗ ERROR: Column '{issue_column}' not found in dataset!")
        print(f"  Available issue columns: {[col for col in df.columns if col.startswith('Issue_')]}")
        return pd.DataFrame()

    # Issue column might contain 'x', 'X', '1', or similar markers
    # We'll consider any non-empty value as "tagged with this issue"
    issue_condition = (df[issue_column].str.strip() != '') & (df[issue_column].notna())
    issue_matches = df[issue_condition]
    print(f"  ✓ Found {len(issue_matches)} statements tagged with Issue {issue_number}")

    # Combine both conditions
    print(f"\nStep 3: Combining filters (subqueries AND issue)...")
    combined_condition = subquery_condition & issue_condition
    filtered_df = df[combined_condition]
    print(f"  ✓ Found {len(filtered_df)} statements matching BOTH criteria")

    return filtered_df

def analyze_results(df, filtered_df, subqueries):
    """Display analysis of the filtered results"""
    print("\n" + "="*80)
    print("RESULTS ANALYSIS")
    print("="*80)
    print()

    total_statements = len(df)
    matching_statements = len(filtered_df)
    percentage = (matching_statements / total_statements * 100) if total_statements > 0 else 0

    print(f"Total statements in dataset: {total_statements}")
    print(f"Matching statements: {matching_statements}")
    print(f"Percentage of dataset: {percentage:.2f}%")

    if matching_statements == 0:
        print("\n⚠ No statements found matching both criteria.")
        print("  Suggestions:")
        print("    • Try different subqueries")
        print("    • Check if the issue number is correct")
        print("    • Verify that statements with this issue contain these terms")
        return

    # Count which subqueries were found
    print(f"\nSubquery distribution (in matching statements):")
    subquery_counts = {}
    for subquery in subqueries:
        pattern = re.escape(subquery)
        count = filtered_df['Statement'].str.contains(pattern, case=False, na=False, regex=True).sum()
        if count > 0:
            subquery_counts[subquery] = count

    # Sort by count
    sorted_subqueries = sorted(subquery_counts.items(), key=lambda x: x[1], reverse=True)
    for subquery, count in sorted_subqueries:
        print(f"  • '{subquery}': {count} occurrences")

    unused_subqueries = [sq for sq in subqueries if sq not in subquery_counts]
    if unused_subqueries:
        print(f"\nSubqueries not found in matching statements ({len(unused_subqueries)}):")
        for sq in unused_subqueries[:10]:  # Show first 10
            print(f"  • '{sq}'")
        if len(unused_subqueries) > 10:
            print(f"  ... and {len(unused_subqueries) - 10} more")

    # Year distribution
    if 'Year' in filtered_df.columns:
        print(f"\nYear distribution:")
        year_counts = filtered_df['Year'].value_counts().sort_index()
        for year, count in year_counts.items():
            if pd.notna(year):
                print(f"  • {int(year)}: {count} statements")

    # Actor distribution (top 10)
    if 'Actor' in filtered_df.columns:
        print(f"\nTop 10 actors:")
        actor_counts = filtered_df['Actor'].value_counts().head(10)
        for actor, count in actor_counts.items():
            if actor:
                print(f"  • {actor}: {count} statements")

def display_sample_statements(filtered_df, num_samples):
    """Display sample matching statements"""
    print("\n" + "="*80)
    print(f"SAMPLE STATEMENTS (showing first {num_samples})")
    print("="*80)
    print()

    for i, (_, row) in enumerate(filtered_df.head(num_samples).iterrows(), 1):
        statement = row['Statement']
        actor = row.get('Actor', 'Unknown')
        year = row.get('Year', 'N/A')

        # Truncate long statements
        display_statement = statement if len(statement) <= 300 else statement[:300] + "..."

        print(f"{i}. [{actor}, {year}]")
        print(f"   {display_statement}")
        print()

def create_cluster_visualization(df, filtered_df, topic_name, issue_number, output_folder):
    """Create and save cluster visualization as PDF"""
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Clean topic name for filename
    safe_topic_name = topic_name.replace("/", "-").replace("\\", "-")
    pdf_filename = f"{safe_topic_name}.pdf"
    pdf_path = os.path.join(output_folder, pdf_filename)

    # Get all statements for this issue (for context)
    issue_column = f'Issue_{issue_number}'
    issue_condition = (df[issue_column].str.strip() != '') & (df[issue_column].notna())
    issue_df = df[issue_condition]

    # Check if we have valid X, Y coordinates
    if 'X' not in df.columns or 'Y' not in df.columns or 'Cluster' not in df.columns:
        print(f"  ⚠ Warning: Missing X, Y, or Cluster columns. Skipping visualization.")
        return None

    # Filter out rows without valid coordinates
    valid_coords_df = df[(df['X'].notna()) & (df['Y'].notna())]
    valid_issue_df = issue_df[(issue_df['X'].notna()) & (issue_df['Y'].notna())]
    valid_filtered_df = filtered_df[(filtered_df['X'].notna()) & (filtered_df['Y'].notna())]

    if len(valid_filtered_df) == 0:
        print(f"  ⚠ Warning: No statements with valid coordinates. Skipping visualization.")
        return None

    # Get clusters present in filtered data
    filtered_clusters = set(valid_filtered_df['Cluster'].dropna().unique())

    # Count statements per cluster in filtered data
    cluster_counts = Counter(valid_filtered_df['Cluster'].dropna())

    # Create figure
    _, ax = plt.subplots(figsize=(12, 8))

    # Plot all statements (background) in light gray
    ax.scatter(valid_coords_df['X'], valid_coords_df['Y'],
               c='lightgray', s=10, alpha=0.3, label='Other statements')

    # Plot issue-related statements (but not matching topic) in a different color
    issue_not_topic = valid_issue_df[~valid_issue_df.index.isin(valid_filtered_df.index)]
    if len(issue_not_topic) > 0:
        ax.scatter(issue_not_topic['X'], issue_not_topic['Y'],
                   c='lightblue', s=20, alpha=0.5, label=f'Issue {issue_number} (other)')

    # Get unique clusters in filtered data and assign colors
    unique_clusters = sorted(filtered_clusters)

    # Use tab20 for more colors if needed
    if len(unique_clusters) <= 10:
        colors = plt.cm.tab10(range(len(unique_clusters)))
    else:
        colors = plt.cm.tab20(range(len(unique_clusters)))

    cluster_color_map = {cluster: colors[i % len(colors)] for i, cluster in enumerate(unique_clusters)}

    # Plot filtered statements by cluster
    # If too many clusters, only show top 10 in legend
    show_in_legend = unique_clusters[:10] if len(unique_clusters) > 10 else unique_clusters

    for cluster in unique_clusters:
        cluster_data = valid_filtered_df[valid_filtered_df['Cluster'] == cluster]
        count = cluster_counts[cluster]

        label = f'Cluster {cluster} ({count})' if cluster in show_in_legend else None
        ax.scatter(cluster_data['X'], cluster_data['Y'],
                   c=[cluster_color_map[cluster]], s=50, alpha=0.8,
                   label=label)

    # Set labels and title
    ax.set_xlabel('X', fontsize=12)
    ax.set_ylabel('Y', fontsize=12)
    title = f'{topic_name}\nIssue {issue_number}: {ISSUE_DESCRIPTIONS[issue_number][:60]}...'
    ax.set_title(title, fontsize=14, fontweight='bold')

    # Add legend
    ax.legend(loc='best', fontsize=9, framealpha=0.9)

    # Add grid
    ax.grid(True, alpha=0.3)

    # Add summary text box
    top_3_clusters = cluster_counts.most_common(3)
    cluster_list = ', '.join([f'{cl} ({ct})' for cl, ct in top_3_clusters])

    summary_text = (
        f'Total matching statements: {len(filtered_df)}\n'
        f'Relevant clusters: {len(filtered_clusters)}\n'
        f'Top clusters: {cluster_list}'
    )

    if len(unique_clusters) > 10:
        summary_text += f'\n(Showing top 10 of {len(unique_clusters)} clusters in legend)'
    ax.text(0.02, 0.98, summary_text,
            transform=ax.transAxes,
            fontsize=9,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    # Tight layout
    plt.tight_layout()

    # Save as PDF
    plt.savefig(pdf_path, format='pdf', dpi=300, bbox_inches='tight')
    plt.close()

    return pdf_path

def export_results_to_text(filtered_df, topic_name, issue_number, output_folder, users_excluded=False):
    """Export filtered results to text file"""
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Clean topic name for filename
    safe_topic_name = topic_name.replace("/", "-").replace("\\", "-")
    filename = f"{safe_topic_name}.txt"
    output_path = os.path.join(output_folder, filename)

    # Get cluster information
    cluster_counts = Counter(filtered_df['Cluster'].dropna())
    unique_clusters = sorted(cluster_counts.keys())

    # Sort statements chronologically by Year
    # Handle NaN values by putting them at the end
    sorted_df = filtered_df.copy()
    sorted_df['Year_sort'] = sorted_df['Year'].fillna(9999)  # Put NaN years at the end
    sorted_df = sorted_df.sort_values('Year_sort')

    # Get year range for header
    valid_years = filtered_df['Year'].dropna()
    if len(valid_years) > 0:
        year_range = f"{int(valid_years.min())} - {int(valid_years.max())}"
    else:
        year_range = "N/A"

    with open(output_path, 'w', encoding='utf-8') as f:
        # Write header
        f.write("="*80 + "\n")
        f.write(f"TOPIC: {topic_name}\n")
        f.write(f"ISSUE: {issue_number} - {ISSUE_DESCRIPTIONS[issue_number]}\n")
        f.write(f"MATCHING STATEMENTS: {len(filtered_df)}\n")
        f.write(f"YEAR RANGE: {year_range}\n")
        f.write(f"RELEVANT CLUSTERS: {len(unique_clusters)}\n")
        if cluster_counts:
            f.write(f"CLUSTER DISTRIBUTION: {dict(cluster_counts)}\n")
        f.write(f"SOCIAL MEDIA USERS EXCLUDED: {'Yes' if users_excluded else 'No'}\n")
        f.write(f"SORTED BY: Year (chronological order)\n")
        f.write("="*80 + "\n\n")

        # Write each statement in chronological order
        for i, (_, row) in enumerate(sorted_df.iterrows(), 1):
            statement = row['Statement']
            actor = row.get('Actor', 'Unknown')
            year = row.get('Year', 'N/A')
            stmt_id = row.get('id', 'N/A')
            cluster = row.get('Cluster', 'N/A')

            f.write(f"{i}. ID: {stmt_id}\n")
            f.write(f"   Year: {year}\n")
            f.write(f"   Cluster: {cluster}\n")
            f.write(f"   Actor: {actor}\n")
            f.write(f"   Statement: {statement}\n")
            f.write("\n" + "-"*80 + "\n\n")

    return output_path

# ============================================================================
# EXECUTE THE FILTER
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("SUBQUERY AND ISSUE FILTER - PROCESS ALL TOPICS")
    print("="*80)
    print()

    # Validate configuration
    if selected_issue < 1 or selected_issue > 16:
        print(f"✗ ERROR: Issue number must be between 1 and 16!")
        exit(1)

    print(f"Configuration:")
    print(f"  Topics to process: {len(TOPIC_SUBQUERIES)}")
    print(f"  Issue: {selected_issue} - {ISSUE_DESCRIPTIONS[selected_issue]}")
    print(f"  Exclude social media users: {exclude_users}")
    print(f"  Output folder: {output_folder}")
    print()

    # Load data once
    df = load_data(DATASET_PATH)

    # Filter out social media users if requested
    if exclude_users:
        df = filter_out_users(df)

    # Track results for all topics
    all_results = {}
    exported_files = []

    # Process each topic
    for topic_idx, (topic_name, subqueries) in enumerate(TOPIC_SUBQUERIES.items(), 1):
        print("\n" + "="*80)
        print(f"PROCESSING TOPIC {topic_idx}/{len(TOPIC_SUBQUERIES)}: '{topic_name}'")
        print("="*80)
        print(f"Subqueries: {subqueries}")
        print()

        # Filter statements for this topic
        filtered_df = filter_by_subqueries_and_issue(df, subqueries, selected_issue)

        # Store results
        all_results[topic_name] = {
            'count': len(filtered_df),
            'df': filtered_df
        }

        # Show quick summary
        print(f"\n✓ Found {len(filtered_df)} matching statements for '{topic_name}'")

        # Show sample statements if requested
        if show_sample_statements and len(filtered_df) > 0:
            display_sample_statements(filtered_df, min(num_samples, len(filtered_df)))

        # Export to text file and create visualization
        if len(filtered_df) > 0:
            # Export text file
            txt_path = export_results_to_text(filtered_df, topic_name, selected_issue, output_folder, exclude_users)
            print(f"✓ Exported text file to: {txt_path}")

            # Create cluster visualization PDF
            pdf_path = create_cluster_visualization(df, filtered_df, topic_name, selected_issue, output_folder)
            if pdf_path:
                print(f"✓ Created visualization PDF: {pdf_path}")
                exported_files.append((topic_name, txt_path, pdf_path, len(filtered_df)))
            else:
                exported_files.append((topic_name, txt_path, None, len(filtered_df)))
        else:
            print(f"⚠ No results to export for '{topic_name}'")

    # Final summary
    print("\n" + "="*80)
    print("FINAL SUMMARY - ALL TOPICS")
    print("="*80)
    print(f"\nIssue: {selected_issue} - {ISSUE_DESCRIPTIONS[selected_issue]}")
    print(f"Topics processed: {len(TOPIC_SUBQUERIES)}")
    print(f"Social media users excluded: {'Yes' if exclude_users else 'No'}")
    print(f"Output folder: {os.path.abspath(output_folder)}")
    print()

    print("Results by topic:")
    total_statements = 0
    for topic_name, result in all_results.items():
        count = result['count']
        total_statements += count
        print(f"  • {topic_name}: {count} statements")

    print(f"\nTotal matching statements across all topics: {total_statements}")

    if exported_files:
        print(f"\nExported files ({len(exported_files)} topics):")
        for topic_name, txt_path, pdf_path, count in exported_files:
            txt_name = os.path.basename(txt_path)
            if pdf_path:
                pdf_name = os.path.basename(pdf_path)
                print(f"  • {topic_name}: {txt_name} + {pdf_name} ({count} statements)")
            else:
                print(f"  • {topic_name}: {txt_name} ({count} statements, no visualization)")

    print("\n" + "="*80)
    print("DONE")
    print("="*80)
