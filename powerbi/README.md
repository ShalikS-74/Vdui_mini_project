# Power BI project candidate - Desktop verification required

Open `BeyondEmpire.pbip` using recent Power BI Desktop with PBIP/PBIR support.
This is editable project source, **not a PBIX or a visually verified dashboard**.
PBIR report/page/visual JSON passed Microsoft's published schema validation.
The TMDL semantic model and rendering have not been executed in Power BI Desktop.

1. Rebuild CSVs using `python src/pipeline.py`.
2. Edit `BeyondEmpire.SemanticModel/definition/expressions.tmdl`: set DataRoot to
   the absolute local dashboard directory. Or change this text parameter in
   Power Query after opening. No login or paid service needed for local files.
3. Open the PBIP and refresh. Check typed Predictions, Explanations and Cases.
4. Confirm observation_id uniqueness in Predictions and one-to-many relationships
   to Explanations and Cases. All use polity|year, derived in Power Query.
5. Inspect the pages: polity/year slicers, selected-score card, SHAP bars,
   observation table, threshold-driven audit queue table and the score-by-year scatter
   (points at or above the selected threshold without a decline outcome are the
   audit queue).
   On the False-positive audit page, use the **Audit threshold** dropdown to
   switch among 50%, 60%, 70% and 80%. The selected-threshold card, queue-size
   card, review-set card, queue table and scatter all update together. The
   queue table lists every held-out row at or above the selected threshold,
   highest scores first; rows in the curated 0.70 review set are flagged and
   carry their notes. Verdicts remain pending sourced review.
   On the Threshold results page, pick a model and protocol to read the held-out
   confusion counts (tp/fp/fn/tn), precision, recall, F1 and false-alarm queue
   size at each of the four thresholds, per evaluation seed, with mean-across-
   seeds cards and charts. These come from threshold_results.csv: one trained
   model scored once per held-out row, re-classified at each cutoff. No
   per-threshold retraining, and with six observed declines every number is
   exploratory.
6. Check that selection filters the exact OOF SHAP row; log-odds explanations must
   reconstruct that score. Check pending historical-review status and captions.
   `DataRoot` is preserved across regeneration; the generator only writes the
   CHANGE_ME placeholder when no path has been set yet.
7. Inspect pixels at 100% and fit-to-page, fix any Desktop issues, then save as
   PBIX if needed. Do not claim this step was done until a person/renderer checks.

Regenerate project source with `python powerbi/build_project.py` after export
schema changes. Existing Desktop visual edits would be overwritten; preserve a
copy before regenerating. The generator also does not emit Desktop-added
metadata (lineageTags, model annotations, newer schema versions), so a blind
regenerate-plus-commit would drop them; restore or re-apply them as done in the
committed files. Sources consulted for format and schema conventions:
https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview
https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report
https://github.com/ruiromano/pbip-demo/

These sources describe format, not evidence this candidate renders correctly.
