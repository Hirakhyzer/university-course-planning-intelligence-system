# Synthetic lab

The synthetic lab creates fictional data for:

- degree programs
- course catalog and prerequisites
- professor availability
- course sections and capacity
- student goals and transcripts
- next-term recommendations
- graduation-risk signals
- subgroup fairness audit

Run:

```bash
python scripts/run_synthetic_course_lab.py --students 80 --seed 42
```

Generated files are written under `outputs/` and are ignored by Git except for `outputs/.gitkeep`.
