"""
Relevant Queries Finder - Discover related formulations for a query
DTU - Explore the Energy Islands controversy

This script helps you iteratively discover related formulations for a given topic/query.
It starts with an initial query and uses context analysis and n-gram extraction
to automatically discover related terms and variations.

Edit the configuration variables below and run the script.
"""

# ============================================================================
# CONFIGURATION - EDIT THESE VARIABLES
# ============================================================================

# Starting query to find related formulations for
# Can be a single string or a list of strings
start_query = ["Esbjerg"]
# start_query = "hydrogen"  # Or single query

# Maximum iterations to search for new formulations
max_iterations = 5

# Show sample statements for each iteration (helps identify new terms)
show_sample_statements = True

# Number of sample statements to display per iteration
num_samples = 10

# Minimum frequency for a term to be considered (filters out rare terms)
# Lower this for rare topics, increase for common topics
min_term_frequency = 2

# Maximum number of new formulations to add per iteration
max_new_per_iteration = 5

# Include single-word variations (e.g., for "hydrogen" also find "h2")
include_single_word_variants = True

# ============================================================================
# DATA SOURCE CONFIGURATION
# ============================================================================

# Path to dataset (edit if needed)
#DATASET_PATH = 'data/Actor statement dataset.csv'  # Local file
DATASET_PATH = 'https://jacomyma.github.io/dtu-sts-material/data/Actor%20statement%20dataset.csv'  # Online

# ============================================================================
# MAIN CODE
# ============================================================================

import pandas as pd
import matplotlib.pyplot as plt
import os
from collections import Counter
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

def search_statements(df, query_terms):
    """Search for statements matching any of the query terms"""
    pattern = '|'.join(query_terms)
    condition = df['Statement'].str.contains(pattern, case=False, na=False)
    return df[condition]

def extract_bigrams(text, target_word):
    """
    Extract common bigrams (two-word phrases) containing the target word.
    This helps identify related formulations.
    """
    # Tokenize and clean
    words = re.findall(r'\b\w+\b', text.lower())
    bigrams = []

    for i in range(len(words) - 1):
        if target_word.lower() in [words[i], words[i+1]]:
            bigrams.append(f"{words[i]} {words[i+1]}")

    return bigrams

def extract_context_words(df, query_terms, context_window=5):
    """
    Extract words that frequently appear near the query terms.
    This helps identify related concepts.
    """
    all_context_words = []

    for statement in df['Statement']:
        words = re.findall(r'\b\w+\b', statement.lower())

        for query in query_terms:
            query_words = query.lower().split()

            for i, word in enumerate(words):
                if word in query_words:
                    # Get context words before and after
                    start = max(0, i - context_window)
                    end = min(len(words), i + context_window + 1)
                    context = words[start:end]

                    # Filter out the query words themselves and common stopwords
                    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being'}
                    context = [w for w in context if w not in query_words and w not in stopwords and len(w) > 2]
                    all_context_words.extend(context)

    return Counter(all_context_words)

def extract_ngrams(df, current_formulations, n=2):
    """
    Extract n-grams (phrases) that contain any word from the current formulations.
    This helps discover related multi-word expressions.
    """
    # Extract key words from current formulations
    key_words = set()
    for formulation in current_formulations:
        key_words.update(formulation.lower().split())

    ngram_counter = Counter()

    for statement in df['Statement']:
        words = re.findall(r'\b\w+\b', statement.lower())

        # Extract n-grams
        for i in range(len(words) - (n - 1)):
            ngram = ' '.join(words[i:i+n])

            # Check if ngram contains any key word
            ngram_words = set(ngram.split())
            if ngram_words & key_words:  # Intersection
                ngram_counter[ngram] += 1

    return ngram_counter

def extract_context_variants(df, current_formulations, min_freq=2):
    """
    Extract single words and variants that frequently appear in statements
    containing the current formulations. This helps find related concepts.
    """
    # Get all statements matching current formulations
    pattern = '|'.join(current_formulations)
    matching_statements = df[df['Statement'].str.contains(pattern, case=False, na=False)]['Statement']

    # Extract all words from matching statements
    word_counter = Counter()
    for statement in matching_statements:
        words = re.findall(r'\b\w+\b', statement.lower())
        word_counter.update(words)

    # Filter out stopwords and current formulation words
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                 'this', 'that', 'these', 'those', 'will', 'would', 'can', 'could',
                 'should', 'may', 'might', 'has', 'have', 'had', 'do', 'does', 'did'}

    current_words = set()
    for formulation in current_formulations:
        current_words.update(formulation.lower().split())

    filtered_words = {}
    for word, count in word_counter.items():
        if (word not in stopwords and
            word not in current_words and
            len(word) > 2 and
            count >= min_freq):
            filtered_words[word] = count

    return filtered_words

def score_candidate_formulations(candidates, current_formulations):
    """
    Score candidate formulations based on relevance.
    Higher score = more likely to be a good related formulation.
    """
    scored_candidates = []

    for candidate, frequency in candidates:
        score = frequency  # Base score is frequency

        # Bonus if it contains words from current formulations
        candidate_words = set(candidate.lower().split())
        for formulation in current_formulations:
            formulation_words = set(formulation.lower().split())
            overlap = len(candidate_words & formulation_words)
            if overlap > 0:
                score += overlap * 10  # Bonus for word overlap

        # Penalty for very long phrases (likely to be too specific)
        word_count = len(candidate.split())
        if word_count > 4:
            score *= 0.5

        scored_candidates.append((candidate, frequency, score))

    # Sort by score descending
    scored_candidates.sort(key=lambda x: x[2], reverse=True)

    return scored_candidates

def iterative_search(df, start_query, max_iterations, show_samples, num_samples):
    """
    Iteratively search for related formulations using automated discovery.
    """
    print("="*80)
    print(f"ITERATIVE SEARCH FOR RELATED FORMULATIONS")
    print(f"Starting query: '{start_query}'")
    print(f"Using automated discovery (no pre-defined formulations)")
    print("="*80)
    print()

    # Start with just the initial query
    all_formulations = {start_query}
    current_formulations = [start_query]

    # First, check if the start query returns any results
    print("Checking initial query coverage...")
    initial_matches = search_statements(df, [start_query])
    print(f"✓ Found {len(initial_matches)} statements containing '{start_query}'")

    if len(initial_matches) == 0:
        print("\n⚠ WARNING: No statements found for the initial query!")
        print("  This query may not appear in the dataset.")
        print("  Try a different query or check the spelling.")
        return all_formulations, []

    if len(initial_matches) < 10:
        print(f"\n⚠ NOTE: Only {len(initial_matches)} statements found.")
        print("  This is a rare topic - results may be limited.")
        print(f"  Consider lowering min_term_frequency (currently {min_term_frequency})")

    print()

    iteration_results = []

    for iteration in range(1, max_iterations + 1):
        print(f"\n{'='*80}")
        print(f"ITERATION {iteration}")
        print(f"{'='*80}")
        print(f"Current formulations to search ({len(current_formulations)}): {current_formulations}")
        print()

        # Search for statements matching current formulations
        matching_df = search_statements(df, current_formulations)
        print(f"Found {len(matching_df)} matching statements")

        if len(matching_df) == 0:
            print("No matching statements found. Stopping iteration.")
            break

        # Store iteration results
        iteration_results.append({
            'iteration': iteration,
            'formulations': current_formulations.copy(),
            'count': len(matching_df)
        })

        # Show sample statements
        if show_samples:
            print(f"\nSample statements (showing first {num_samples}):")
            print("-" * 80)
            for i, (_, row) in enumerate(matching_df.head(num_samples).iterrows(), 1):
                statement = row['Statement']
                display_statement = statement[:200] + "..." if len(statement) > 200 else statement
                print(f"{i}. {display_statement}\n")

        # AUTOMATED DISCOVERY - Extract candidate formulations
        print("\n" + "-" * 80)
        print("AUTOMATED DISCOVERY")
        print("-" * 80)

        # Extract bigrams and trigrams containing our key words
        print("\nExtracting bigrams (2-word phrases)...")
        bigrams = extract_ngrams(matching_df, current_formulations, n=2)

        print("Extracting trigrams (3-word phrases)...")
        trigrams = extract_ngrams(matching_df, current_formulations, n=3)

        # Also extract single-word variants if enabled
        all_candidates = list(bigrams.items()) + list(trigrams.items())

        if include_single_word_variants:
            print("Extracting single-word context variants...")
            single_words = extract_context_variants(matching_df, current_formulations, min_freq=min_term_frequency)

            # Show top context words for information
            if single_words:
                print(f"\nMost frequent context words:")
                for word, count in sorted(single_words.items(), key=lambda x: x[1], reverse=True)[:10]:
                    print(f"  • {word} ({count} times)")

            # Add single words to candidates
            all_candidates.extend(list(single_words.items()))

        # Filter by minimum frequency
        all_candidates = [(ngram, freq) for ngram, freq in all_candidates
                         if freq >= min_term_frequency]

        # Remove candidates that are already in our formulations
        all_candidates = [(ngram, freq) for ngram, freq in all_candidates
                         if ngram not in [f.lower() for f in all_formulations]]

        # Filter out candidates that are exact substrings (but allow partial overlap)
        filtered_candidates = []
        for ngram, freq in all_candidates:
            is_exact_substring = False
            for existing in all_formulations:
                # Only filter if one is completely contained in the other
                if ngram == existing.lower():
                    is_exact_substring = True
                    break
                # For multi-word terms, check if it's a complete substring
                if ' ' in ngram and ngram in existing.lower():
                    is_exact_substring = True
                    break
                if ' ' in existing and existing.lower() in ngram:
                    is_exact_substring = True
                    break
            if not is_exact_substring:
                filtered_candidates.append((ngram, freq))

        if not filtered_candidates:
            print("\nℹ No new candidate formulations found.")
            if iteration == 1:
                print("  Possible reasons:")
                print(f"    • The topic '{start_query}' is very specific with no common variations")
                print(f"    • min_term_frequency ({min_term_frequency}) is too high for this rare topic")
                print(f"    • The dataset has limited statements about this topic")
                print("\n  Try:")
                print(f"    • Lowering min_term_frequency to 1")
                print(f"    • Using a broader starting query (e.g., 'energy' instead of '{start_query}')")
                print(f"    • Checking if '{start_query}' appears in the dataset with different spelling")
            else:
                print("  All relevant terms may have been discovered.")
            break

        # Score candidates
        scored_candidates = score_candidate_formulations(
            filtered_candidates, current_formulations
        )

        # Show top candidates
        print(f"\nTop {min(10, len(scored_candidates))} candidate formulations:")
        print(f"{'Candidate':<40} {'Frequency':<12} {'Score':<10}")
        print("-" * 80)
        for i, (candidate, freq, score) in enumerate(scored_candidates[:10], 1):
            print(f"{candidate:<40} {freq:<12} {score:<10.1f}")

        # Automatically select top N candidates
        new_formulations = [candidate for candidate, _, _ in scored_candidates[:max_new_per_iteration]]

        if not new_formulations:
            print("\nℹ No new formulations to add in this iteration.")
            print("  Stopping iteration.")
            break

        print(f"\n✓ Automatically adding top {len(new_formulations)} formulations:")
        for f in new_formulations:
            print(f"  • {f}")

        # Update tracking
        all_formulations.update(new_formulations)
        current_formulations = new_formulations  # Next iteration searches for new terms only

    return all_formulations, iteration_results

def analyze_formulation_usage(df, all_formulations):
    """
    Analyze how each formulation is used in the dataset.
    """
    print("\n\n" + "="*80)
    print("FORMULATION USAGE ANALYSIS")
    print("="*80)
    print()

    formulation_stats = []
    for formulation in all_formulations:
        condition = df['Statement'].str.contains(formulation, case=False, na=False)
        matching_rows = df[condition]
        count = len(matching_rows)

        if count > 0:
            first_id = matching_rows.iloc[0]['id']
            first_statement = matching_rows.iloc[0]['Statement'][:100] + "..."
        else:
            first_id = None
            first_statement = "N/A"

        formulation_stats.append({
            'formulation': formulation,
            'count': count,
            'first_id': first_id,
            'first_statement': first_statement
        })

    # Sort by count (descending)
    formulation_stats.sort(key=lambda x: x['count'], reverse=True)

    # Display results
    print(f"{'Formulation':<40} {'Count':<10} {'First ID':<10}")
    print("-" * 80)
    for stats in formulation_stats:
        first_id_str = str(stats['first_id']) if stats['first_id'] else 'N/A'
        print(f"{stats['formulation']:<40} {stats['count']:<10} {first_id_str:<10}")

    # Show top 3
    print("\n" + "="*80)
    print("TOP 3 MOST USED FORMULATIONS")
    print("="*80)
    for i, stats in enumerate(formulation_stats[:3], 1):
        print(f"\n{i}. '{stats['formulation']}'")
        print(f"   Used in {stats['count']} statements")
        if stats['first_id']:
            print(f"   First statement ID: {stats['first_id']}")
            print(f"   Example: {stats['first_statement']}")

    return formulation_stats

def create_comprehensive_query(df, all_formulations):
    """
    Create a comprehensive query using all formulations.
    """
    print("\n\n" + "="*80)
    print("COMPREHENSIVE QUERY")
    print("="*80)
    print()

    final_query = '|'.join(all_formulations)
    final_condition = df['Statement'].str.contains(final_query, case=False, na=False)
    final_matches = df[final_condition]

    print(f"Total formulations found: {len(all_formulations)}")
    print(f"Total statements matching any formulation: {len(final_matches)}")
    print(f"Percentage of dataset: {(len(final_matches)/len(df)*100):.2f}%")

    return final_matches, final_condition

def export_formulations(all_results, output_file="discovered_formulations.txt"):
    """
    Export the discovered formulations to a text file.
    all_results is a dict mapping query -> dict with 'formulations' and 'stats'
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Related Formulations Discovery Results\n")
        f.write(f"# Generated by relevant_queries.py\n")
        f.write(f"# Total queries processed: {len(all_results)}\n")
        f.write(f"# Format: formulation (count)\n\n")

        # Write as Python dict format (can be copied into code)
        f.write("TOPIC_FORMULATIONS = {\n")

        query_list = list(all_results.items())
        for i, (query, result_data) in enumerate(query_list):
            formulations = result_data['formulations']
            stats = result_data['stats']

            # Create a dict mapping formulation -> count for easy lookup
            count_map = {stat['formulation']: stat['count'] for stat in stats}

            # Sort formulations by count (descending), then alphabetically
            sorted_formulations = sorted(formulations, key=lambda f: (-count_map.get(f, 0), f.lower()))

            f.write(f'    "{query}": [\n')
            for j, formulation in enumerate(sorted_formulations):
                count = count_map.get(formulation, 0)
                comma = "," if j < len(sorted_formulations) - 1 else ""
                f.write(f'        "{formulation}",  # {count} occurrences{comma}\n')

            # Add comma after closing bracket if not last query
            comma_after = "," if i < len(query_list) - 1 else ""
            f.write(f'    ]{comma_after}\n')

            if i < len(query_list) - 1:
                f.write('\n')  # Blank line between queries

        f.write('}\n')

    print(f"\n✓ Formulations exported to: {os.path.abspath(output_file)}")
    print(f"  You can copy these into your TOPIC_FORMULATIONS dictionary.")
    print(f"  Each formulation includes its occurrence count as a comment.")

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
# EXECUTE THE SEARCH
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("RELEVANT QUERIES FINDER")
    print("="*80)
    print()

    # Load data
    df = load_data(DATASET_PATH)

    # Convert single query to list for uniform processing
    if isinstance(start_query, str):
        queries = [start_query]
    else:
        queries = start_query

    print(f"Processing {len(queries)} quer{'y' if len(queries) == 1 else 'ies'}: {queries}")
    print()

    # Store all results
    all_results = {}

    # Process each query
    for query_idx, query in enumerate(queries, 1):
        print("\n" + "="*80)
        print(f"QUERY {query_idx}/{len(queries)}: '{query}'")
        print("="*80)
        print()

        # Iterative search for related formulations
        all_formulations, iteration_results = iterative_search(
            df,
            query,
            max_iterations,
            show_sample_statements,
            num_samples
        )

        # Analyze formulation usage
        formulation_stats = analyze_formulation_usage(df, all_formulations)

        # Create comprehensive query
        final_matches, final_condition = create_comprehensive_query(df, all_formulations)

        # Store results (formulations and stats)
        all_results[query] = {
            'formulations': all_formulations,
            'stats': formulation_stats
        }

        # Summary for this query
        print("\n" + "="*80)
        print(f"SUMMARY FOR '{query}'")
        print("="*80)
        print(f"Total formulations discovered: {len(all_formulations)}")
        print(f"Total matching statements: {len(final_matches)}")
        print(f"\nAll formulations:")
        for formulation in sorted(all_formulations):
            print(f"  • {formulation}")

        if query_idx < len(queries):
            print("\n" + "-"*80)
            print(f"Moving to next query...")
            print("-"*80)

    # Export all formulations to single file
    print("\n" + "="*80)
    print("EXPORTING ALL RESULTS")
    print("="*80)
    export_formulations(all_results)

    # Overall summary
    print("\n" + "="*80)
    print("FINAL SUMMARY - ALL QUERIES")
    print("="*80)
    total_formulations = sum(len(result_data['formulations']) for result_data in all_results.values())
    print(f"\nTotal queries processed: {len(queries)}")
    print(f"Total formulations discovered: {total_formulations}")
    print(f"\nResults by query:")
    for query, result_data in all_results.items():
        print(f"  • '{query}': {len(result_data['formulations'])} formulations")

    print("\n" + "="*80)
    print("DONE")
    print("="*80)
    print(f"\nNext steps:")
    print(f"  1. Review the discovered formulations in 'discovered_formulations.txt'")
    print(f"  2. Copy the TOPIC_FORMULATIONS dict into statement_getter.py")
    print(f"  3. Use them in your queries for richer results")
