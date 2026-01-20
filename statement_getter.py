"""
Statement Getter - Query actor statements by topic
DTU - Explore the Energy Islands controversy

This script filters statements from a specific actor about a specific topic.
Edit the configuration variables below and run the script.
"""

# ============================================================================
# CONFIGURATION - EDIT THESE VARIABLES
# ============================================================================

# Actor to search for (leave empty "" to include all actors)
actor = "Bornholm"

# Topic to search for (leave empty "" to include all topics)
topic = ""

# Include actor variations/aliases?
# If True, will search for common variations of the actor name
include_actor_variations = True

# Include topic formulations?
# If True, will search for related terms and formulations of the topic
include_topic_variations = True

# ============================================================================
# DATA SOURCE CONFIGURATION
# ============================================================================

# Path to dataset (edit if needed)
#DATASET_PATH = 'data/Actor statement dataset.csv'  # Local file
DATASET_PATH = 'https://jacomyma.github.io/dtu-sts-material/data/Actor%20statement%20dataset.csv'  # Online

# ============================================================================
# ACTOR VARIATIONS DICTIONARY
# ============================================================================
# Define common variations/aliases for actors
# Add more as needed

ACTOR_VARIATIONS = {
    "DEA": [
        "DEA",
        "Danish Energy Agency",
        "Energistyrelsen"
    ],
    "Danish Energy Agency": [
        "DEA",
        "Danish Energy Agency",
        "Energistyrelsen"
    ],
    "Energinet": [
        "Energinet",
        "Energinet (with Danish Energy Agency)"
    ],
    "Kraka": [
        "Kraka",
        "Kraka Economics",
        "Think tank Kraka"
    ],
    "Business Center Bornholm": [
        "Business Center Bornholm",
        "BCB"
    ]
}

# ============================================================================
# TOPIC FORMULATIONS DICTIONARY
# ============================================================================
# Define related formulations for topics
# Add more as needed

TOPIC_FORMULATIONS = {
    "supply security": [
        "supply security",
        "energy security",
        "security of supply",
        "energy independence",
        "self-sufficiency",
        "energy sovereignty",
        "supply reliability",
        "energy autonomy",
        "supply stability",
        "energy resilience",
        "strategic autonomy",
        "supply chain security",
        "energy dependence"
    ],
    "expertise": [
        "expertise",
        "expert",
        "specialists",
        "competence",
        "knowledge",
        "skills",
        "qualified",
        "professionals",
        "experience",
        "know-how",
        "capabilities",
        "proficiency"
    ],
    "cost": [
        "cost",
        "expense",
        "price",
        "budget",
        "expensive",
        "cheap",
        "affordable",
        "funding",
        "investment",
        "financing"
    ],
    "nuclear": [
        "nuclear",
        "atomic",
        "reactor",
        "fission",
        "uranium"
    ],
    "wind energy": [
        "wind energy",
        "wind power",
        "wind turbine",
        "wind farm",
        "offshore wind",
        "onshore wind"
    ],
    "environment": [
        "environment",
        "environmental",
        "climate",
        "green",
        "sustainable",
        "sustainability",
        "carbon",
        "emissions",
        "pollution"
    ]
}

# ============================================================================
# MAIN CODE
# ============================================================================

import pandas as pd
import matplotlib.pyplot as plt
import os

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

def get_actor_terms(actor, include_variations):
    """Get list of actor terms to search for"""
    if not actor or actor.strip() == "":
        print(f"Actor filter disabled:")
        print(f"  Including ALL actors")
        return None

    if include_variations and actor in ACTOR_VARIATIONS:
        terms = ACTOR_VARIATIONS[actor]
        print(f"Actor variations enabled:")
        print(f"  Searching for: {', '.join(terms)}")
    else:
        terms = [actor]
        print(f"Actor variations disabled:")
        print(f"  Searching for: {actor}")
    return terms

def get_topic_terms(topic, include_variations):
    """Get list of topic terms to search for"""
    if not topic or topic.strip() == "":
        print(f"Topic filter disabled:")
        print(f"  Including ALL topics")
        return None

    if include_variations and topic in TOPIC_FORMULATIONS:
        terms = TOPIC_FORMULATIONS[topic]
        print(f"Topic formulations enabled:")
        print(f"  Searching for {len(terms)} formulations: {', '.join(terms[:5])}...")
    else:
        terms = [topic]
        print(f"Topic formulations disabled:")
        print(f"  Searching for: {topic}")
    return terms

def create_actor_condition(df, actor_terms):
    """Create condition for actor matching"""
    if actor_terms is None:
        # No actor filter - include all rows
        return pd.Series([True] * len(df), index=df.index)

    # Use OR logic to match any of the actor variations
    pattern = '|'.join([term.replace('(', r'\(').replace(')', r'\)') for term in actor_terms])
    condition = df['Actor'].str.contains(pattern, case=False, na=False)
    return condition

def create_topic_condition(df, topic_terms):
    """Create condition for topic matching"""
    if topic_terms is None:
        # No topic filter - include all rows
        return pd.Series([True] * len(df), index=df.index)

    # Use OR logic to match any of the topic formulations
    pattern = '|'.join(topic_terms)
    condition = df['Statement'].str.contains(pattern, case=False, na=False)
    return condition

def display_results(df, matching_df, actor, topic):
    """Display the filtered results"""
    print("\n" + "="*80)
    print(f"RESULTS: {len(matching_df)} statements found")
    print("="*80)

    if len(matching_df) == 0:
        print("\nNo statements found matching the criteria.")
        print("Try enabling variations or using different search terms.")
        return matching_df

    # Show summary statistics
    percentage = (len(matching_df) / len(df)) * 100
    print(f"\nFound {len(matching_df)} statements ({percentage:.2f}% of total)")

    # Display filter criteria
    if actor and actor.strip() != "":
        print(f"From actor: {actor}")
    else:
        print(f"From actor: ALL ACTORS")

    if topic and topic.strip() != "":
        print(f"About topic: {topic}")
    else:
        print(f"About topic: ALL TOPICS")

    # Show breakdown by year if available
    if 'Year' in matching_df.columns:
        year_counts = matching_df['Year'].value_counts().sort_index()
        if len(year_counts) > 0:
            print(f"\nBreakdown by year:")
            for year, count in year_counts.items():
                print(f"  {year}: {count} statements")

    # Show breakdown by source
    if 'Source name' in matching_df.columns:
        source_counts = matching_df['Source name'].value_counts().head(5)
        print(f"\nTop 5 sources:")
        for source, count in source_counts.items():
            print(f"  {source}: {count} statements")

    # Display first 5 statements
    print("\n" + "="*80)
    print("SAMPLE STATEMENTS (first 5)")
    print("="*80)

    for i, (_, row) in enumerate(matching_df.head(5).iterrows(), 1):
        print(f"\n[{i}] ID: {row['id']} | {row['Actor']} | {row['Date of publication']}")
        print("-" * 80)
        statement = row['Statement']
        # Truncate long statements
        display_statement = statement[:300] + "..." if len(statement) > 300 else statement
        print(display_statement)

    # Export to Excel
    print("\n" + "="*80)
    print("EXPORTING TO EXCEL")
    print("="*80)
    return matching_df

def visualize_results(df, condition, title):
    """Create a pie chart visualization of the results"""
    df_copy = df.copy()
    df_copy['filtered'] = condition

    filtered_counts = df_copy['filtered'].value_counts()

    def make_autopct(values):
        def my_autopct(pct):
            total = sum(values)
            val = int(round(pct*total/100.0))
            return '{p:.1f}%\n({v:d})'.format(p=pct,v=val)
        return my_autopct

    colors = ['#4deded' if label else '#EAEAEA' for label in filtered_counts.index]

    plt.figure(figsize=(4, 4))
    plt.pie(filtered_counts, autopct=make_autopct(filtered_counts),
            colors=colors, startangle=90)
    plt.title(title)
    plt.show()

# ============================================================================
# EXECUTE THE QUERY
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("STATEMENT GETTER - Actor & Topic Query")
    print("="*80)
    print()

    # Load data
    df = load_data(DATASET_PATH)

    # Get search terms
    print("="*80)
    print("SEARCH CONFIGURATION")
    print("="*80)
    actor_terms = get_actor_terms(actor, include_actor_variations)
    print()
    topic_terms = get_topic_terms(topic, include_topic_variations)
    print()

    # Create conditions
    print("="*80)
    print("EXECUTING QUERY")
    print("="*80)

    actor_condition = create_actor_condition(df, actor_terms)
    if actor_terms is None:
        print(f"✓ Actor filter: DISABLED (all {actor_condition.sum()} statements included)")
    else:
        print(f"✓ Actor filter: {actor_condition.sum()} statements match")

    topic_condition = create_topic_condition(df, topic_terms)
    if topic_terms is None:
        print(f"✓ Topic filter: DISABLED (all {topic_condition.sum()} statements included)")
    else:
        print(f"✓ Topic filter: {topic_condition.sum()} statements match")

    # Combine with AND logic (must match both actor AND topic)
    combined_condition = actor_condition & topic_condition

    if actor_terms is None and topic_terms is None:
        print(f"✓ Combined filter: ALL {combined_condition.sum()} statements included (no filters applied)")
    elif actor_terms is None:
        print(f"✓ Combined filter: {combined_condition.sum()} statements about the topic")
    elif topic_terms is None:
        print(f"✓ Combined filter: {combined_condition.sum()} statements from the actor")
    else:
        print(f"✓ Combined filter: {combined_condition.sum()} statements match both")

    # Get matching statements
    matching_df = df[combined_condition].copy()

    # Sort by date
    matching_df['Date'] = pd.to_datetime(matching_df['Date of publication'], errors='coerce')
    matching_df = matching_df.sort_values('Date')

    # Display results
    matching_df = display_results(df, matching_df, actor, topic)

    # Export to Excel
    output_file = "results.xlsx"
    try:
        # Select relevant columns for export
        export_columns = [
            'id', 'Statement', 'Actor', 'Representative of', 'Actor context',
            'Year', 'Date of publication', 'Source name', 'Source type',
            'Source URL', 'Cluster'
        ]

        # Add Issue columns if they exist
        issue_cols = [col for col in matching_df.columns if col.startswith('Issue_')]
        export_columns.extend(issue_cols)

        # Filter to only existing columns
        export_columns = [col for col in export_columns if col in matching_df.columns]

        matching_df[export_columns].to_excel(output_file, index=False, engine='openpyxl')
        file_path = os.path.abspath(output_file)
        print(f"✓ Exported {len(matching_df)} statements to: {file_path}")
    except ImportError:
        print("⚠ openpyxl not installed. Installing now...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'openpyxl'])
        matching_df[export_columns].to_excel(output_file, index=False, engine='openpyxl')
        file_path = os.path.abspath(output_file)
        print(f"✓ Exported {len(matching_df)} statements to: {file_path}")
    except Exception as e:
        print(f"✗ Error exporting to Excel: {e}")
        print(f"  Falling back to CSV export...")
        csv_file = "results.csv"
        matching_df.to_csv(csv_file, index=False)
        print(f"✓ Exported to CSV: {os.path.abspath(csv_file)}")

    # Visualize
    print("\n")

    # Create title for visualization
    if actor and actor.strip() != "" and topic and topic.strip() != "":
        viz_title = f"{actor} on {topic}"
    elif actor and actor.strip() != "":
        viz_title = f"All statements from {actor}"
    elif topic and topic.strip() != "":
        viz_title = f"All statements about {topic}"
    else:
        viz_title = "All statements (no filters)"

    visualize_results(df, combined_condition, viz_title)

    print("\n" + "="*80)
    print("DONE")
    print("="*80)
    print(f"\nResults saved to: {output_file}")
    print("The variable 'matching_df' contains all filtered statements.")
    print("\nYou can open the Excel file to review all statements in detail.")
