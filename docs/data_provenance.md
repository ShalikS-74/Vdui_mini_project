# Data provenance

Official source: https://github.com/seshatdb/Equinox_Data
Pinned revision: 602c7cdf0649e1fbbdb37f5b5a387edbe19915d0
File: Equinox_on_GitHub_June9_2022.xlsx
Sheet: AggrSCWarAgriRelig
Release DOI: https://doi.org/10.5281/zenodo.6642229

The upstream README states CC BY-NC-SA. Upstream GitHub license metadata and
README disagree; honor the data-specific non-commercial/share-alike statement
and resolve licensing before distribution beyond this academic use.
Raw input is downloaded, not checked in. The generated outputs derive from this
source and must retain attribution and its applicable restrictions.

Transform: replace -999 with missing; remove uniq=n fillers; coerce numerical
columns; reject duplicate observation keys; exact future/past joins within
(NGA, PolID). The current group key is PolID across NGAs. A continuity export
explicitly labels it observed-polity-only. No predecessor/successor links are
inferred, and polity transitions outside an unchanged key are censored.

Terr is treated as log10 area, as in the existing implementation. The current
rebuild reproduces its 98 rows and 6 positives. Source variable coding, sampling,
Terr interpretation and survival/transition bias need domain review before any
research claim. Adjacent centuries and multiple NGA observations are dependent.
