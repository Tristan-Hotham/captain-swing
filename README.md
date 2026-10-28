# Captain Swing: did the riots follow the machines?

In 1830 farm labourers across southern and eastern England smashed threshing machines, burned ricks and sent threatening letters signed "Captain Swing". Was the rising about the machines, or about hunger, wages, enclosure and the poor law? This is a visual, descriptive data study built entirely on the open replication data of Caprettini and Voth (2020).

**Interactive version:** https://tristan-hotham.github.io/captain-swing/
**Paper:** https://doi.org/10.5281/zenodo.23727133
**Blog post:** https://blog.tristanhotham.com/2026/10/28/captain-swing/

This repository holds the interactive page, the derived data and the analysis code for the data study *Captain Swing: did the riots follow the machines?* by Dr Tristan Hotham (Independent researcher, ORCID 0000-0003-4931-9349).

## Credit first

All underlying data come from **Caprettini, Bruno, and Hans-Joachim Voth. 2020. "Rage against the Machines: Labor-Saving Technology and Unrest in Industrializing England." *American Economic Review: Insights* 2 (3): 305 to 320. https://doi.org/10.1257/aeri.20190385**, replication package https://doi.org/10.3886/E117044V1 (openICPSR, CC BY 4.0). Their riot counts come from Holland (ed.) 2005, *Swing Unmasked*. Their causal results (including the heavy-soil instrumental-variable estimate) are theirs; I only reproduce them as a check. The maps, cross-tabulations, neighbour comparisons, gradients, simple models and the rest of the descriptive analysis here are mine.

## Headline results

My descriptive analysis (main sample of 9,674 parishes unless stated):

- The data hold 3,117 Swing incidents in 1,479 of 10,699 parishes of 1851 England and Wales; 529 (17%) were attacks on threshing machines. They record 641 threshing machines in 544 parishes before 1830.
- Parishes with a recorded machine saw unrest in 27.0% of cases, against 13.8% without (2.0 times). Against machine-free parishes within 10 km the gap is 9.8 percentage points (95% bootstrap interval 6.1 to 13.6); it holds in four of five regions.
- But 90% of parishes with unrest had no recorded machine, and 73% of machine parishes stayed quiet. The machine records are a thin sample (Kent, where Swing began, has 6 in 357 parishes).
- Enclosure barely matters: unrest runs from 16.3% in the least enclosed fifth of parishes to 17.7% in the most enclosed (6,715 parishes).
- Poverty matters: among the 1,251 parishes with 1801 poor rates, unrest rises from 14% in the lowest-spending fifth to 34% in the highest; winter unemployment reported in 1834 shows a similar rise (12% to 32%, 595 parishes). Wheat prices show no clear pattern.
- 23% of parishes within 100 km of London saw unrest, against 5.8% beyond 200 km; parishes within 150 km hold 71% of incidents.
- The machine gap is larger far from industrial towns (16.3 points) than near them (9.9 points), echoing Caprettini and Voth's Figure 3.
- Reproduction check: I reproduce their published sample size (9,674), means (Swing 0.308, machines 0.062), OLS coefficient (0.389) and 2SLS coefficient (6.361, s.e. 1.616) exactly.

## Files

- `index.html`: the interactive page (parish map with search and a 1800 to 1830 play mode, charts). `header.png`: social card.
- `data/parishes.csv`: one row per 1851 parish (10,699 rows): county, parish, identifier, region, main-sample flag, centroid (computed from their boundary file) and inside point (WGS84), Swing incidents (all, machine attacks, other, up to April 1831), recorded machines, pre-1830 unrest, and their covariates (1801 density and occupations, enclosure, heavy soil, cereal suitability, poor rates, 1834 unemployment, wheat and oat prices, distances to Elham, newspapers and manufacturing towns, 1830 weather anomalies), plus my distance to London. Values are Caprettini and Voth's, unchanged, except the centroid and distance to London.
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
