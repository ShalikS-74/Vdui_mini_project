# Blinded historical time-support review package

This is an uncompleted review form, not reviewed labels or expert endorsement.
`time_support_review.csv` samples two unique polity-feature records in each
available feature/formation-period stratum using fixed hash ranking. It never
uses outcomes, model scores, future areas or false-positive status. Region is
retained so coverage can be inspected; it is not a sampling stratum.

Reviewers should not open the prediction outputs before recording judgments.
Use two independent reviewers, preserve their separate forms, then record
adjudication of disagreements. Do not overwrite disagreements to force consensus.
The same person/assistant cannot supply independent agreement by filling two forms.

For each record, find its source entry using the polity/feature identifier. Record
actual observed URLs, citation/page and relevant narrative before entering a verdict.
Do not construct guessed links. A source's empty year field or gray lifetime dates
are not evidence for a specific historical start/end. Consult original cited works
where accessible, and explicitly mark when they were not read.

`time_support_verdict`: whole_lifetime_supported, bounded_interval_supported,
point_only_supported, no_explicit_time_support, conflicting_scope, or unresolved.
`construct_verdict`: supports_defined_construct, partial_or_different_construct,
conflicting_evidence, or unresolved. `confidence`: high, medium, low, with reasons.
Leave explicit time fields blank unless supported by the source. Record inferred,
uncertain or disputed claims in the note rather than laundering them into certainty.

This form does not include outcomes, values, model names or predictions. The source
itself may reveal events; blinding is a procedural goal, not guaranteed ignorance.
Do not use agreement percentages as accuracy or ground truth. A stratified small
sample does not estimate population error rates without appropriate weighting and
coverage assumptions. All reviewer fields are intentionally blank.

Regenerate from the pinned primary inputs and feature-support audit using
`python research/prepare_review.py`. The sample and seed are frozen in the manifest.
No expert has been contacted and no external work or time commitment is authorized.
