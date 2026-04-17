# Simulated Data Profiles — Contributor Guide

Each YAML file in this folder defines one data table. The generator reads these
profiles and produces simulated data that matches the specified distributions.

## How to make data more realistic

Edit the YAML files directly. Look for `# TUNE:` comments — these mark the
parameters that most affect realism. No code changes needed.

### What you can tune

| Knob | Where | What it controls | Example |
|------|-------|-----------------|---------|
| `mean` | numeric columns | Center of the distribution | Bureau score mean: 680 → 720 |
| `std` | numeric columns | Spread (higher = more variance) | Score std: 75 → 50 (tighter) |
| `lambda` | poisson columns | Average count | Derog marks lambda: 1.2 → 0.8 (fewer) |
| `min` / `max` | numeric columns | Hard bounds (values clipped) | Score: 300–850 |
| `categories` | categorical columns | Value probabilities (sum to ~1.0) | on_time: 0.72 → 0.80 |
| `correlations` | table level | Cross-column relationships | score ↔ derog: negative, 0.7 |
| `row_count` | table level | How many rows to generate | 50 → 200 |
| `description` | columns | Shows up in data catalog for specialists | Human-readable meaning |

### Step by step

1. **Open the YAML** for the table you want to improve (e.g. `bureau_full.yaml`)

2. **Adjust parameters** — examples:
   - "Real bureau scores for our cases center around 640, not 680"
     → Change `mean: 680` to `mean: 640`
   - "Most customers have 0-2 derog marks, not 1.2 average"
     → Change `lambda: 1.2` to `lambda: 0.8`
   - "We see more 'late' payments than 10%"
     → Change `late: 0.18` to `late: 0.25` (reduce another category to compensate)

3. **Add new columns** if the real data has fields we're missing:
   ```yaml
   new_column_name:
     dtype: float          # string | int | float | categorical | date
     distribution: normal  # normal | poisson | uniform
     mean: 50
     std: 15
     min: 0
     max: 100
     description: "Human-readable description of what this column means"
   ```

4. **Add correlations** if you know two columns are related:
   ```yaml
   correlations:
     - columns: [income_est, total_debt]
       direction: positive    # both go up together
       strength: 0.5          # 0.0 = no effect, 1.0 = perfect rank correlation
   ```

5. **Regenerate**:
   ```bash
   python -m data --output data/simulated/ --seed 42
   ```

6. **Inspect** — check a case folder to see if the data looks right:
   ```bash
   cat data/simulated/CASE-00001/bureau_full.csv
   ```

### Distribution cheat sheet

| Distribution | When to use | Key parameter |
|-------------|-------------|---------------|
| `normal` | Continuous values clustered around a center | `mean`, `std` |
| `poisson` | Counts of rare events (0, 1, 2, 3...) | `lambda` (average rate) |
| `uniform` | Equally likely across range | `min`, `max` |
| `categorical` | Named categories with probabilities | `categories: {A: 0.6, B: 0.4}` |

### Tips

- **Probabilities must sum to ~1.0** for categorical columns
- **Correlations are rank-based** — they preserve each column's distribution while sorting them together
- **Use `description`** on every column — specialists read these to understand what data means
- **Seed is deterministic** — same seed always produces the same data, so changes are easy to compare
