"""
Tower of Hanoi Report Generator

Generates performance reports, charts, CSV, and JSON files from game data.
"""

import json
import csv
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import database
import os


def fetch_report_data(limit=15):
    """
    Fetch the last N game records for report generation.
    
    Args:
        limit (int): Number of records to fetch
        
    Returns:
        list: List of game records with all relevant data
    """
    conn = database.get_conn()
    cur = conn.cursor()

    cur.execute("PRAGMA table_info(results)")
    columns = [col[1] for col in cur.fetchall()]

    query_cols = ["id", "player", "pegs", "disks", "moves", "optimal_moves", "time_taken"]

    if 'recursive_time' in columns:
        query_cols.append('recursive_time')
    if 'iterative_time' in columns:
        query_cols.append('iterative_time')
    elif 'algorithm_time' in columns:
        query_cols.append('algorithm_time')
    
    if 'date' in columns:
        query_cols.append('date')
    if 'solved' in columns:
        query_cols.append('solved')
    if 'efficiency' in columns:
        query_cols.append('efficiency')
    if 'user_moves' in columns:
        query_cols.append('user_moves')
    if 'actual_moves' in columns:
        query_cols.append('actual_moves')
    if 'is_correct' in columns:
        query_cols.append('is_correct')
    if 'efficiency_note' in columns:
        query_cols.append('efficiency_note')
    
    query = f"SELECT {', '.join(query_cols)} FROM results ORDER BY id DESC LIMIT ?"
    cur.execute(query, (limit,))
    
    rows = cur.fetchall()
    conn.close()

    records = []
    for row in rows:
        record = {}
        for i, col in enumerate(query_cols):
            record[col] = row[i]
        records.append(record)
    
    return records


def generate_algorithm_comparison_chart(records, output_file="algorithm_comparison_chart.png"):
    """
    Generate a comparison chart between recursive and iterative algorithms.
    
    Args:
        records (list): List of game records
        output_file (str): Output filename for the chart
    """
    if not records:
        print("No records found to generate chart.")
        return

    has_both = 'recursive_time' in records[0] and 'iterative_time' in records[0]
    
    if not has_both:
        print("⚠️  Warning: Database doesn't have both algorithm times. Generating single algorithm chart.")
        generate_time_comparison_chart(records, output_file)
        return

    records = list(reversed(records))
    
    rounds = list(range(1, len(records) + 1))
    recursive_times = [r.get('recursive_time', 0) * 1000 for r in records]  # Convert to ms
    iterative_times = [r.get('iterative_time', 0) * 1000 for r in records]  
    disk_counts = [r.get('disks', 0) for r in records]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Chart 1: Line comparison
    ax1.plot(rounds, recursive_times, marker='o', label='Recursive Algorithm', 
             linewidth=2.5, color='#FF6B9D', markersize=8)
    ax1.plot(rounds, iterative_times, marker='s', label='Iterative Algorithm', 
             linewidth=2.5, color='#00E5FF', markersize=8)
    
    ax1.set_xlabel('Game Round', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Execution Time (milliseconds)', fontsize=12, fontweight='bold')
    ax1.set_title('Algorithm Performance Comparison: Recursive vs Iterative', 
                  fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11, loc='upper left')
    ax1.grid(True, alpha=0.3, linestyle='--')

    for i in range(0, len(rounds), max(1, len(rounds)//5)):
        ax1.annotate(f'{disk_counts[i]}D', 
                    (rounds[i], recursive_times[i]),
                    textcoords="offset points", xytext=(0,10), ha='center',
                    fontsize=8, color='#FF6B9D', fontweight='bold')
    
    # Chart 2: Performance difference
    time_diff = [iter_t - rec_t for iter_t, rec_t in zip(iterative_times, recursive_times)]
    colors = ['#4CAF50' if d < 0 else '#F44336' for d in time_diff]
    
    ax2.bar(rounds, time_diff, color=colors, alpha=0.7, edgecolor='black')
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)
    
    ax2.set_xlabel('Game Round', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Time Difference (ms)\n(Iterative - Recursive)', fontsize=12, fontweight='bold')
    ax2.set_title('Performance Difference (Negative = Recursive Faster)', 
                  fontsize=14, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Chart saved: {output_file}")
    plt.close()


def generate_time_comparison_chart(records, output_file="time_comparison_chart.png"):
    """
    Generate a time comparison chart for algorithm performance.
    
    Args:
        records (list): List of game records
        output_file (str): Output filename for the chart
    """
    if not records:
        print("No records found to generate chart.")
        return
    
    records = list(reversed(records))

    rounds = list(range(1, len(records) + 1))
    
    if 'recursive_time' in records[0]:
        times = [r.get('recursive_time', 0) * 1000 for r in records]  # Convert to ms
        label = 'Recursive Algorithm'
    elif 'algorithm_time' in records[0]:
        times = [r.get('algorithm_time', 0) * 1000 for r in records] 
        label = 'Algorithm'
    else:
        print("No algorithm time data found.")
        return
    
    disk_counts = [r.get('disks', 0) for r in records]

    plt.figure(figsize=(12, 6))
    plt.plot(rounds, times, marker='o', label=label, linewidth=2, color='#00E5FF', markersize=8)

    for i, (round_num, time_val, disk_count) in enumerate(zip(rounds, times, disk_counts)):
        if i % 2 == 0:  
            plt.annotate(f'{disk_count}D', 
                        (round_num, time_val),
                        textcoords="offset points", xytext=(0,10), ha='center',
                        fontsize=9, fontweight='bold')
    
    plt.xlabel('Game Round', fontsize=12, fontweight='bold')
    plt.ylabel('Time (milliseconds)', fontsize=12, fontweight='bold')
    plt.title('Tower of Hanoi Algorithm Timing (per Round)', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Chart saved: {output_file}")
    plt.close()


def generate_efficiency_chart(records, output_file="efficiency_chart.png"):
    """
    Generate an efficiency chart showing user performance vs optimal.
    
    Args:
        records (list): List of game records
        output_file (str): Output filename for the chart
    """
    if not records:
        print("No records found to generate chart.")
        return

    records = list(reversed(records))
    
    rounds = list(range(1, len(records) + 1))
    user_moves = [r.get('moves', 0) for r in records]
    optimal_moves = [r.get('optimal_moves', 0) for r in records]
    efficiency = [(opt/usr)*100 if usr > 0 else 0 for opt, usr in zip(optimal_moves, user_moves)]
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Chart 1: Moves comparison
    ax1.plot(rounds, user_moves, marker='o', label='User Moves', 
             linewidth=2.5, color='#FF6B9D', markersize=8)
    ax1.plot(rounds, optimal_moves, marker='s', label='Optimal Moves', 
             linewidth=2.5, color='#00E5FF', markersize=8)
    ax1.fill_between(rounds, user_moves, optimal_moves, alpha=0.2, color='gray')
    
    ax1.set_xlabel('Game Round', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Number of Moves', fontsize=12, fontweight='bold')
    ax1.set_title('User Performance vs Optimal Solution', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3, linestyle='--')
    
    # Chart 2: Efficiency bars
    colors = ['#4CAF50' if e >= 90 else '#FFC107' if e >= 70 else '#F44336' for e in efficiency]
    bars = ax2.bar(rounds, efficiency, color=colors, alpha=0.7, edgecolor='black')
    ax2.axhline(y=100, color='#00E5FF', linestyle='--', linewidth=2, label='Perfect (100%)')

    for bar, eff in zip(bars, efficiency):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{eff:.0f}%',
                ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    ax2.set_xlabel('Game Round', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Efficiency (%)', fontsize=12, fontweight='bold')
    ax2.set_title('Solution Efficiency by Round', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=11)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    ax2.set_ylim([0, max(efficiency) * 1.15])
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Chart saved: {output_file}")
    plt.close()


def generate_csv_report(records, output_file="tower_of_hanoi_report.csv"):
    """
    Generate a CSV report of game statistics.
    
    Args:
        records (list): List of game records
        output_file (str): Output filename for the CSV
    """
    if not records:
        print("No records found to generate CSV.")
        return

    headers = ["Round", "Player", "Pegs", "Disks", "Moves", "Optimal Moves", "Time Taken (s)"]

    if 'recursive_time' in records[0]:
        headers.append("Recursive Time (s)")
    if 'iterative_time' in records[0]:
        headers.append("Iterative Time (s)")
    elif 'algorithm_time' in records[0]:
        headers.append("Algorithm Time (s)")
    
    headers.extend(["Solved", "Efficiency (%)", "Date", "Efficiency Note"])
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        # Write data rows
        for i, record in enumerate(reversed(records), start=1):
            efficiency = record.get('efficiency', 0.0)
            efficiency_pct = f"{efficiency * 100:.1f}" if efficiency else "0.0"
            solved = "Yes" if record.get('solved', 0) == 1 else "No"
            
            row = [
                i,
                record.get('player', 'Unknown'),
                record.get('pegs', 0),
                record.get('disks', 0),
                record.get('moves', 0),
                record.get('optimal_moves', 0),
                f"{record.get('time_taken', 0.0):.2f}",
            ]
            
            # Add algorithm times
            if 'recursive_time' in record:
                row.append(f"{record.get('recursive_time', 0.0):.6f}")
            if 'iterative_time' in record:
                row.append(f"{record.get('iterative_time', 0.0):.6f}")
            elif 'algorithm_time' in record:
                row.append(f"{record.get('algorithm_time', 0.0):.6f}")
            
            row.extend([
                solved,
                efficiency_pct,
                record.get('date', ''),
                record.get('efficiency_note', '')
            ])
            writer.writerow(row)
    
    print(f"✅ CSV report saved: {output_file}")


def generate_json_report(records, output_file="tower_of_hanoi_report.json"):
    """
    Generate a JSON report of game statistics.
    
    Args:
        records (list): List of game records
        output_file (str): Output filename for the JSON
    """
    if not records:
        print("No records found to generate JSON.")
        return

    report = {
        "report_metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_games": len(records),
            "report_type": "Tower of Hanoi Performance Analysis"
        },
        "summary_statistics": calculate_summary_stats(records),
        "game_records": []
    }

    for i, record in enumerate(reversed(records), start=1):
        game_record = {
            "round": i,
            "player": record.get('player', 'Unknown'),
            "pegs": record.get('pegs', 0),
            "disks": record.get('disks', 0),
            "moves": record.get('moves', 0),
            "optimal_moves": record.get('optimal_moves', 0),
            "time_taken_seconds": round(record.get('time_taken', 0.0), 2),
            "solved": record.get('solved', 0) == 1,
            "efficiency_percentage": round(record.get('efficiency', 0.0) * 100, 1),
            "date": record.get('date', ''),
            "efficiency_note": record.get('efficiency_note', ''),
            "user_moves": record.get('user_moves', ''),
            "actual_moves": record.get('actual_moves', ''),
            "is_correct": record.get('is_correct', 0) == 1
        }

        if 'recursive_time' in record:
            game_record["recursive_algorithm_time_seconds"] = round(record.get('recursive_time', 0.0), 6)
        if 'iterative_time' in record:
            game_record["iterative_algorithm_time_seconds"] = round(record.get('iterative_time', 0.0), 6)
        elif 'algorithm_time' in record:
            game_record["algorithm_time_seconds"] = round(record.get('algorithm_time', 0.0), 6)
        
        report["game_records"].append(game_record)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"✅ JSON report saved: {output_file}")


def calculate_summary_stats(records):
    """
    Calculate summary statistics from game records.
    
    Args:
        records (list): List of game records
        
    Returns:
        dict: Summary statistics
    """
    if not records:
        return {}
    
    total_games = len(records)
    solved_games = sum(1 for r in records if r.get('solved', 0) == 1)
    
    avg_moves = sum(r.get('moves', 0) for r in records) / total_games
    avg_time = sum(r.get('time_taken', 0.0) for r in records) / total_games
    avg_efficiency = sum(r.get('efficiency', 0.0) for r in records) / total_games
    
    stats = {
        "total_games": total_games,
        "solved_games": solved_games,
        "success_rate_percentage": round((solved_games / total_games) * 100, 1),
        "average_moves": round(avg_moves, 1),
        "average_time_seconds": round(avg_time, 2),
        "average_efficiency_percentage": round(avg_efficiency * 100, 1)
    }

    if 'recursive_time' in records[0]:
        avg_recursive = sum(r.get('recursive_time', 0.0) for r in records) / total_games
        stats["average_recursive_time_ms"] = round(avg_recursive * 1000, 3)
    
    if 'iterative_time' in records[0]:
        avg_iterative = sum(r.get('iterative_time', 0.0) for r in records) / total_games
        stats["average_iterative_time_ms"] = round(avg_iterative * 1000, 3)
    
    return stats


def generate_full_report(limit=15):
    """
    Generate complete report package: charts, CSV, and JSON.
    
    Args:
        limit (int): Number of recent games to include
    """
    print(f"\n{'='*60}")
    print(f"  TOWER OF HANOI - REPORT GENERATOR")
    print(f"{'='*60}\n")

    database.init_db()

    if not os.path.exists('reports'):
        os.makedirs('reports')
    
    # Fetch data
    print(f"📊 Fetching last {limit} game records...")
    records = fetch_report_data(limit)
    
    if not records:
        print("❌ No game records found in database.")
        print("   Play some games first to generate reports!")
        return
    
    print(f"✅ Found {len(records)} game records\n")

    print("📄 Generating reports...\n")

    generate_algorithm_comparison_chart(records, "reports/algorithm_comparison_chart.png")
    generate_efficiency_chart(records, "reports/efficiency_chart.png")

    generate_csv_report(records, "reports/tower_of_hanoi_report.csv")
    generate_json_report(records, "reports/tower_of_hanoi_report.json")
    
    print(f"\n{'='*60}")
    print("✅ REPORT GENERATION COMPLETE!")
    print(f"{'='*60}\n")
    print("Generated files in 'reports/' folder:")
    print("  📈 algorithm_comparison_chart.png - Recursive vs Iterative")
    print("  📊 efficiency_chart.png - User performance analysis")
    print("  📄 tower_of_hanoi_report.csv - Spreadsheet data")
    print("  📋 tower_of_hanoi_report.json - Structured data")
    print()
    
    stats = calculate_summary_stats(records)
    print("📊 SUMMARY STATISTICS:")
    print(f"   Total Games: {stats.get('total_games', 0)}")
    print(f"   Solved Games: {stats.get('solved_games', 0)}")
    print(f"   Success Rate: {stats.get('success_rate_percentage', 0)}%")
    print(f"   Average Efficiency: {stats.get('average_efficiency_percentage', 0)}%")
    if 'average_recursive_time_ms' in stats:
        print(f"   Avg Recursive Time: {stats['average_recursive_time_ms']}ms")
    if 'average_iterative_time_ms' in stats:
        print(f"   Avg Iterative Time: {stats['average_iterative_time_ms']}ms")
    print()


if __name__ == "__main__":
    generate_full_report(limit=15)