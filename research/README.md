# Expanded 50-year study

This is an exploratory extension, not a replacement of the small Equinox dashboard
and not a claim of research-grade or publishable evidence. Read `protocol.md`
before interpreting the results and `../docs/research_findings.md` for conclusions.

From repository root, install pinned `requirements.txt`, then:

```sh
python research/polaris_cliopatria.py
python research/evaluate50.py
python -m pytest -q
```

The first command downloads two source-pinned datasets and verifies their SHA256.
Optional `--polaris-path` and `--cliopatria-path` accept already-downloaded exact
files, still hash checked. The second command creates fold metrics, split membership,
all predictions and bootstrap summaries in `data/research50`. Runtime is roughly a
minute on the development machine; hardware affects it. No GPU, cloud run, API key
or paid service is required. The small manifest/summary exports are committed;
large derived panels and per-row logs are regenerated locally rather than treated
as manually curated historical evidence.

The manifest's `fitted_models:0` describes the feasibility constructor only. The
separate evaluation command fits models and writes its own output CSVs. It never
changes the old dashboard's predictions. Scores are not calibrated probabilities.

The exact same SeshatID does not prove perfect boundary reliability or historical
continuity. In particular this panel excludes polities without a future endpoint
under the same ID. It estimates area-change among continuing, mapped observations,
not all collapses or disappearances. A static geometry interval may repeat one
reconstruction at several50-year marks; this is not finer independent evidence.
Grouping limits some related histories crossing folds, but does not eliminate
regional, source or global-time dependence. Do not call these rows independent.
