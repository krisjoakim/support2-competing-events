# SUPPORT2 data source

The repository does not store or redistribute patient-level data. Each notebook
retrieves the official source programmatically with `ucimlrepo`:

~~~python
from ucimlrepo import fetch_ucirepo

support2 = fetch_ucirepo(id=880)
~~~

The retrieval is checked for UCI ID 880, the name `SUPPORT2`, 9,105 rows, 48
columns including the identifier, unique identifiers, the expected column list,
and an `slos` range of 3 to 343 days. `slos` is read from `data.original`
because it is not included in the package target frame.

No manual-download or local-CSV fallback is used. An unavailable source should
be reported rather than silently replaced with another file. The concise
machine-readable mapping from changed SUPPORT2 names to project names is stored
in [column_names.json](column_names.json); identity mappings are omitted.

Authoritative documentation:

- [UCI Machine Learning Repository: SUPPORT2](https://archive.ics.uci.edu/dataset/880/support2)
- [UCI DOI record](https://doi.org/10.3886/ICPSR02957.v2)
- [Vanderbilt SUPPORT description](https://hbiostat.org/data/repo/supportdesc)
- [Vanderbilt SUPPORT2 variable labels](https://hbiostat.org/data/repo/csupport2)

[data_dictionary.md](data_dictionary.md) summarizes these official variable
definitions, source-level missingness, and the modelling role of each field. It
is a convenience reference, not a replacement for the source documentation.

UCI attributes the data to Harrell, F. (1995), SUPPORT2. The original SUPPORT
study is Knaus WA, Harrell FE, Lynn J, et al. (1995), *The SUPPORT prognostic
model: Objective estimates of survival for seriously ill hospitalized adults*,
*Annals of Internal Medicine*, 122, 191–203.
