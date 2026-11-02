**Problem Statement**

For our project, we're building a leakage-safe, explainable model of historical state decline using the Seshat Global History Databank, and testing whether the patterns it learns can meaningfully transfer to present-day governance risk \- while being careful not to overclaim that transfer.

Specifically, I'm proposing: *"Beyond the Empire: A Leakage-Safe, Explainable Model of Historical State Decline and Its Calibrated Transfer to Modern Governance Risk Indicators."* We train a classifier on Seshat (linked to Cliopatria for polity continuity/labels) to predict whether a historical polity declines, rises, or stays stable over a 50-year horizon, using governance, fiscal, military, succession, and administrative features. We validate it properly \- lineage-grouped and temporal train/test splits so we're not leaking future information into the past \- then build a "bridge" feature set with defensible modern proxies (V-Dem, World Bank indicators) and explicitly test whether historical and modern data are even statistically comparable before we try to transfer anything. The core contribution is a false-positive audit: finding the historical cases where the model was confident a state would decline and it didn't, and surfacing what protected those states \- all delivered through an interactive Power BI dashboard with SHAP-based explanations.

**Scope**

I want to be upfront with the team about what we can realistically build versus what we should just cite as future work, so we don't overcommit:

*What we will build:* a clean, documented Seshat–Cliopatria join; one clear label definition (decline/rise/stable at a 50-year horizon, 30% area-change threshold); a baseline model (logistic regression) plus one stronger model (random forest or LightGBM); SHAP feature importance; and \- most importantly \- the false-positive audit, since that's our strongest and most original piece. The dashboard will have a polity selector, a risk estimate, the SHAP explanation, and the flagged false-positive cases.

*What we'll include if time allows:* a domain-shift check (testing whether historical and modern data are too different to compare), and one additional validation split (temporal, since it best supports a "does this generalize forward in time" argument).

*What we're intentionally cutting:* the full sensitivity sweep across every label window and threshold, the CrisisDB cross-check as a separate dataset, the complete drop-one-feature-group ablation, manually extending leader-transition data to 2016–2026, and probability calibration. These are all good scientific practices, but they're multi-week additions we don't have room for \- I'll mention them as future work in our IEEE draft instead of trying to build them.

**Feasibility**

Realistically, the full original scope (as my teammate drafted it) reads like a methods section for an actual research paper, not something four of us can finish by week 12\. The two biggest time-risks are the Seshat–Cliopatria join (historical database linking is messy and under-documented) and the Archigos extension to 2016–2026 (that alone would be its own multi-week data-labeling project). I think we should drop both of those if they start eating into our timeline \- we can build polity continuity directly from Seshat's own data if the Cliopatria join becomes a bottleneck. Everything else in our "must-build" scope is achievable: one clean dataset, one or two models, SHAP, and the false-positive audit is a complete, demo-able project on its own.

**Novelty**

Two things make this stand out from typical collapse-prediction projects. First, the domain-shift check \- actually testing whether historical and modern data are comparable *before* claiming any transfer \- is exactly the kind of rigor that's usually missing when people try to apply historical models to current countries. Even if that check shows the data are too different to transfer cleanly, that's still a valid, citable finding on its own. Second, treating the false-positive audit as our core contribution (not an afterthought) is what makes this genuinely an interactive, explainable-AI project rather than just an EDA/narrative one \- it's also the part that will be most memorable in a demo, since it shows the model being wrong in an interesting way, not just being "accurate."

**Publishability**

I think this version is a real step up from where we started \- if we execute the core scope well, it's close to short-paper quality for a computational social science or digital humanities venue, mainly because of the leakage-safe validation and the domain-shift test. That said, I want to be careful about one thing specifically: if we report any kind of "risk score" for a currently-governing country, even with uncertainty bounds, that reads as a political claim once it leaves our dashboard. I'd rather we keep the present-day angle limited to a retrospective, already-resolved case \- something like checking whether our model would have flagged the USSR before 1991 \- rather than scoring any country that's in power today. That keeps us on safe, defensible ground with the professor and in any future submission. For now, I'd frame this project as "designed to extend toward publication" rather than "ready to submit" \- which is still a strong thing to tell the professor, without us overpromising on what we can actually finish by the final review.

