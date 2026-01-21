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
    ]
}

# Select which issue to filter by (1-16)
# See "data/Issues coding.md" for issue descriptions
selected_issue = 11  # Issue 11: How will energy islands impact local communities?

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

def export_results_to_text(filtered_df, topic_name, issue_number, output_folder):
    """Export filtered results to text file"""
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Clean topic name for filename
    safe_topic_name = topic_name.replace("/", "-").replace("\\", "-")
    filename = f"{safe_topic_name}.txt"
    output_path = os.path.join(output_folder, filename)

    with open(output_path, 'w', encoding='utf-8') as f:
        # Write header
        f.write("="*80 + "\n")
        f.write(f"TOPIC: {topic_name}\n")
        f.write(f"ISSUE: {issue_number} - {ISSUE_DESCRIPTIONS[issue_number]}\n")
        f.write(f"MATCHING STATEMENTS: {len(filtered_df)}\n")
        f.write("="*80 + "\n\n")

        # Write each statement
        for i, (_, row) in enumerate(filtered_df.iterrows(), 1):
            statement = row['Statement']
            actor = row.get('Actor', 'Unknown')
            year = row.get('Year', 'N/A')
            stmt_id = row.get('id', 'N/A')

            f.write(f"{i}. ID: {stmt_id}\n")
            f.write(f"   Actor: {actor}\n")
            f.write(f"   Year: {year}\n")
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
    print(f"  Output folder: {output_folder}")
    print()

    # Load data once
    df = load_data(DATASET_PATH)

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

        # Export to text file
        if len(filtered_df) > 0:
            output_path = export_results_to_text(filtered_df, topic_name, selected_issue, output_folder)
            exported_files.append((topic_name, output_path, len(filtered_df)))
            print(f"✓ Exported to: {output_path}")
        else:
            print(f"⚠ No results to export for '{topic_name}'")

    # Final summary
    print("\n" + "="*80)
    print("FINAL SUMMARY - ALL TOPICS")
    print("="*80)
    print(f"\nIssue: {selected_issue} - {ISSUE_DESCRIPTIONS[selected_issue]}")
    print(f"Topics processed: {len(TOPIC_SUBQUERIES)}")
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
        print(f"\nExported files ({len(exported_files)}):")
        for topic_name, file_path, count in exported_files:
            print(f"  • {os.path.basename(file_path)} ({count} statements)")

    print("\n" + "="*80)
    print("DONE")
    print("="*80)
