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
5. Inspect both pages: polity/year slicers, selected-score card, SHAP bars,
   observation table, false-positive review table and the score-by-year scatter
   (points at or above 0.70 without a decline outcome are the audit queue).
   On the False-positive audit page, use the **Audit threshold** slicer to adjust
   the queue from 30% to 90%. The queue card and scatter update to the selected
   threshold. Format the threshold slicer as a numeric range slider in Power BI
   Desktop if the slicer initially renders as a list. The case table is filtered
   by `Cases[oof_p_decline]` and the scatter is filtered by matching audit cases.
   Select exactly one polity and year for a single score; a multi-row selection
   intentionally returns blank.
6. Check that selection filters the exact OOF SHAP row; log-odds explanations must
   reconstruct that score. Check pending historical-review status and captions.
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
