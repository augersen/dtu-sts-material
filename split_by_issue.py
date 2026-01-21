"""
Split Statements by Issue - Create separate datasets for each issue
DTU - Explore the Energy Islands controversy

This script creates a separate text file for each of the 16 issues,
containing all statements tagged with that issue.

Output: "Issue Specific Datasets" folder with one .txt file per issue
"""

# ============================================================================
# CONFIGURATION - EDIT THESE VARIABLES
# ============================================================================

# Filter out social media users (actors with "user" in their name)
# This excludes Reddit users, Facebook users, LinkedIn users, etc.
exclude_users = True

# Output folder for results
output_folder = "Issue Specific Datasets"

# ============================================================================
# DATA SOURCE CONFIGURATION
# ============================================================================

# Path to dataset (edit if needed)
DATASET_PATH = 'data/Actor statement dataset.csv'  # Local file
# DATASET_PATH = 'https://jacomyma.github.io/dtu-sts-material/data/Actor%20statement%20dataset.csv'  # Online

# ============================================================================
# ISSUE DESCRIPTIONS
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

def export_issue_to_text(df, issue_number, issue_description, output_folder, users_excluded=False):
    """Export statements for a specific issue to text file"""
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Filename
    filename = f"Issue_{issue_number}.txt"
    output_path = os.path.join(output_folder, filename)

    # Filter statements for this issue
    issue_column = f'Issue_{issue_number}'

    if issue_column not in df.columns:
        print(f"  ✗ ERROR: Column '{issue_column}' not found in dataset!")
        return None

    # Issue column might contain 'x', 'X', '1', or similar markers
    issue_condition = (df[issue_column].str.strip() != '') & (df[issue_column].notna())
    issue_df = df[issue_condition]

    if len(issue_df) == 0:
        print(f"  ⚠ No statements found for Issue {issue_number}")
        return None

    # Get cluster information
    cluster_counts = Counter(issue_df['Cluster'].dropna())
    unique_clusters = sorted(cluster_counts.keys())

    # Sort statements chronologically by Year
    sorted_df = issue_df.copy()
    sorted_df['Year_sort'] = sorted_df['Year'].fillna(9999)  # Put NaN years at the end
    sorted_df = sorted_df.sort_values('Year_sort')

    # Get year range
    valid_years = issue_df['Year'].dropna()
    if len(valid_years) > 0:
        year_range = f"{int(valid_years.min())} - {int(valid_years.max())}"
    else:
        year_range = "N/A"

    # Get actor statistics
    actor_counts = Counter(issue_df['Actor'].dropna())
    top_actors = actor_counts.most_common(10)

    with open(output_path, 'w', encoding='utf-8') as f:
        # Write header
        f.write("="*80 + "\n")
        f.write(f"ISSUE {issue_number}\n")
        f.write(f"{issue_description}\n")
        f.write("="*80 + "\n")
        f.write(f"TOTAL STATEMENTS: {len(issue_df)}\n")
        f.write(f"YEAR RANGE: {year_range}\n")
        f.write(f"RELEVANT CLUSTERS: {len(unique_clusters)}\n")
        if cluster_counts:
            f.write(f"CLUSTER DISTRIBUTION: {dict(cluster_counts)}\n")
        f.write(f"SOCIAL MEDIA USERS EXCLUDED: {'Yes' if users_excluded else 'No'}\n")
        f.write(f"SORTED BY: Year (chronological order)\n")
        f.write("="*80 + "\n\n")

        # Write top actors
        if top_actors:
            f.write("TOP 10 ACTORS:\n")
            for i, (actor, count) in enumerate(top_actors, 1):
                if actor:
                    f.write(f"  {i}. {actor} ({count} statements)\n")
            f.write("\n" + "="*80 + "\n\n")

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

    return output_path, len(issue_df)

# ============================================================================
# EXECUTE THE SPLIT
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("SPLIT STATEMENTS BY ISSUE")
    print("="*80)
    print()

    print(f"Configuration:")
    print(f"  Total issues: 16")
    print(f"  Exclude social media users: {exclude_users}")
    print(f"  Output folder: {output_folder}")
    print()

    # Load data
    df = load_data(DATASET_PATH)

    # Filter out social media users if requested
    if exclude_users:
        df = filter_out_users(df)

    # Track results
    results = []

    # Process each issue
    for issue_number in range(1, 17):
        print(f"\nProcessing Issue {issue_number}...")
        print(f"  {ISSUE_DESCRIPTIONS[issue_number][:70]}...")

        result = export_issue_to_text(
            df,
            issue_number,
            ISSUE_DESCRIPTIONS[issue_number],
            output_folder,
            exclude_users
        )

        if result:
            output_path, count = result
            results.append((issue_number, output_path, count))
            print(f"  ✓ Exported {count} statements to: {os.path.basename(output_path)}")

    # Final summary
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    print(f"Output folder: {os.path.abspath(output_folder)}")
    print(f"Social media users excluded: {'Yes' if exclude_users else 'No'}")
    print()

    print("Results by issue:")
    total_statements = sum(count for _, _, count in results)
    for issue_number, output_path, count in results:
        filename = os.path.basename(output_path)
        print(f"  • Issue {issue_number:2d}: {filename} ({count} statements)")

    print(f"\nTotal statements across all issues: {total_statements}")
    print(f"Note: Statements can be tagged with multiple issues, so totals may exceed dataset size.")

    print("\n" + "="*80)
    print("DONE")
    print("="*80)
