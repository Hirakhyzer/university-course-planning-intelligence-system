# Notebooks

Run the main script first:

```bash
python scripts/run_synthetic_course_lab.py
```

Then open a local notebook and load files from `outputs/results/`, such as:

```python
from pathlib import Path
import pandas as pd

results = Path('outputs/results')
risk = pd.read_csv(results / 'synthetic_graduation_risk.csv')
recommendations = pd.read_csv(results / 'synthetic_course_recommendations.csv')
```
