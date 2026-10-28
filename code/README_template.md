# Captain Swing: did the riots follow the machines?

In 1830 farm labourers across southern and eastern England smashed threshing machines, burned ricks and sent threatening letters signed "Captain Swing". Was the rising about the machines, or about hunger, wages, enclosure and the poor law? This is a visual, descriptive data study built entirely on the open replication data of Caprettini and Voth (2020).

**Interactive version:** https://tristan-hotham.github.io/captain-swing/
**Paper:** https://doi.org/10.5281/zenodo.23727133
**Blog post:** https://blog.tristanhotham.com/2026/10/28/captain-swing/

This repository holds the interactive page, the derived data and the analysis code for the data study *Captain Swing: did the riots follow the machines?* by Dr Tristan Hotham (Independent researcher, ORCID 0000-0003-4931-9349).

## Credit first

All underlying data come from **Caprettini, Bruno, and Hans-Joachim Voth. 2020. "Rage against the Machines: Labor-Saving Technology and Unrest in Industrializing England." *American Economic Review: Insights* 2 (3): 305 to 320. https://doi.org/10.1257/aeri.20190385**, replication package https://doi.org/10.3886/E117044V1 (openICPSR, CC BY 4.0). Their riot counts come from Holland (ed.) 2005, *Swing Unmasked*. Their causal results (including the heavy-soil instrumental-variable estimate) are theirs; I only reproduce them as a check. The maps, cross-tabulations, neighbour comparisons, gradients, simple models and the rest of the descriptive analysis here are mine.

## Headline results

My descriptive analysis (main sample of {{counts.parishes_sample|int}} parishes unless stated):

- The data hold {{counts.incidents_all|int}} Swing incidents in {{counts.riot_parishes_all|int}} of {{counts.parishes_all|int}} parishes of 1851 England and Wales; {{counts.machine_attacks_all|int}} ({{counts.attack_share_of_incidents|pct0}}) were attacks on threshing machines. They record {{counts.machines_all|int}} threshing machines in {{counts.machine_parishes_all|int}} parishes before 1830.
- Parishes with a recorded machine saw unrest in {{machines.riot_share_with|pct1}} of cases, against {{machines.riot_share_without|pct1}} without ({{machines.ratio|f1}} times). Against machine-free parishes within {{neighbours.radius_km|int}} km the gap is {{neighbours.diff|pp1}} percentage points (95% bootstrap interval {{neighbours.ci_lo|pp1}} to {{neighbours.ci_hi|pp1}}); it holds in {{machines.regions_higher_with|words}} of five regions.
- But {{machines.riot_parishes_without_machine_share|pct0}} of parishes with unrest had no recorded machine, and {{machines.machine_parishes_quiet_share|pct0}} of machine parishes stayed quiet. The machine records are a thin sample (Kent, where Swing began, has {{counties.top.0.machines|int}} in {{counties.top.0.parishes|int}} parishes).
- Enclosure barely matters: unrest runs from {{gradients.enclosures.rows.0.riot_share|pct1}} in the least enclosed fifth of parishes to {{gradients.enclosures.rows.4.riot_share|pct1}} in the most enclosed ({{gradients.enclosures.n|int}} parishes).
- Poverty matters: among the {{gradients.poor.n|int}} parishes with 1801 poor rates, unrest rises from {{gradients.poor.rows.0.riot_share|pct0}} in the lowest-spending fifth to {{gradients.poor.rows.4.riot_share|pct0}} in the highest; winter unemployment reported in 1834 shows a similar rise ({{gradients.unemp.rows.0.riot_share|pct0}} to {{gradients.unemp.rows.3.riot_share|pct0}}, {{gradients.unemp.n|int}} parishes). Wheat prices show no clear pattern.
- {{london.within100_share|pct0}} of parishes within 100 km of London saw unrest, against {{london.beyond200_share|pct1}} beyond 200 km; parishes within 150 km hold {{london.within150_incident_share|pct0}} of incidents.
- The machine gap is larger far from industrial towns ({{outside.distant.gap|pp1}} points) than near them ({{outside.close.gap|pp1}} points), echoing Caprettini and Voth's Figure 3.
- Reproduction check: I reproduce their published sample size ({{repro.n|int}}), means (Swing {{repro.swing|f3}}, machines {{repro.thresh|f3}}), OLS coefficient ({{repro.ols1_thresh|f3}}) and 2SLS coefficient ({{repro.iv7_thresh|f3}}, s.e. {{repro.iv7_se|f3}}) exactly.

## Files

- `index.html`: the interactive page (parish map with search and a 1800 to 1830 play mode, charts). `header.png`: social card.
- `data/parishes.csv`: one row per 1851 parish ({{counts.parishes_all|int}} rows): county, parish, identifier, region, main-sample flag, centroid (computed from their boundary file) and inside point (WGS84), Swing incidents (all, machine attacks, other, up to April 1831), recorded machines, pre-1830 unrest, and their covariates (1801 density and occupations, enclosure, heavy soil, cereal suitability, poor rates, 1834 unemployment, wheat and oat prices, distances to Elham, newspapers and manufacturing towns, 1830 weather anomalies), plus my distance to London. Values are Caprettini and Voth's, unchanged, except the centroid and distance to London.
- `data/machines.csv`: every dated threshing-machine record (newspaper adverts and General Views of Agriculture) with year, parish and coordinates.
- `data/unrest_pre1830.csv`: every dated pre-1830 report of arson or machine-breaking, with parish and coordinates.
- `data/counties.csv`: incidents, machines and shares by county. `data/bands.csv`: unrest and machines by 25 km distance band from Elham and from London.
- `data/results.json`: every number quoted on the page, in the paper, the blog post and the collage. `repro.*` holds the reproduction of Caprettini and Voth's published numbers; everything else is my own analysis.
- `work/`: intermediate files for the page (rebuilt by the code).
- `code/`: run in order `01_prepare.py` (reads their package in place; set `SWING_DIR`), `02_analyse.py`, `03_build_page.py`, `04_header.py`. Release outputs: `release/make_figures.py`, `release/paper/build_paper.py`, `release/blog/build_post.py`, `reddit/collage.py`. Figures need the fonts Fraunces, Source Serif 4 and IBM Plex Mono (set `FONT_DIR`). Python packages: pandas, numpy, scipy, statsmodels, shapely, pyproj, matplotlib, Pillow, playwright (header only).

## Method in brief and caveats

Everything is descriptive and associational. The machines are those advertised in the newspapers searched or described in the agricultural surveys, so "no recorded machine" does not mean "no machine". The Swing incidents in this package carry no dates, so the spread through autumn 1830 cannot be shown week by week; distance from Elham stands in. Enclosure is a district estimate; poor rates and unemployment exist only for parishes that answered the 1834 Poor Law inquiry, and unemployment was reported after the riots. There are no parish wage data.

## Sources and licences

- Caprettini, B. and Voth, H.-J. 2020. Rage against the Machines: Labor-Saving Technology and Unrest in Industrializing England. *American Economic Review: Insights* 2 (3): 305 to 320. https://doi.org/10.1257/aeri.20190385
- Caprettini, B. and Voth, H.-J. Replication data, openICPSR project E117044 V1. https://doi.org/10.3886/E117044V1 (CC BY 4.0). See their documentation for the original sources: Holland (2005) *Swing Unmasked*; British Newspaper Archive; General Views of Agriculture; Poor Law Report of 1834; Gonner (1912); 1801 census; corn returns; 1851 parish boundaries.
- Wikipedia, "Swing Riots" and "Threshing machine" (CC BY-SA 4.0), retrieved 28 October 2026, for dates, sentences and the share of farm labour spent threshing.
- Base map tiles on the page: Esri. Map library: Leaflet.

The derived data and the text are released under CC BY 4.0, as are Caprettini and Voth's data from which they derive; please credit both. Code is MIT (see `LICENSE`).

## Citation

Hotham, T. 2026. *Captain Swing: Did the Riots Follow the Machines? A Parish-Level Look at the Swing Riots of 1830 to 1832*. Zenodo. https://doi.org/10.5281/zenodo.23727133

Please also cite Caprettini and Voth (2020) and their replication data.

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
