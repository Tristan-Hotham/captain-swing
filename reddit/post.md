## Title

[OC] The 1830 "Captain Swing" riots against threshing machines, mapped by parish: places with a recorded machine were twice as likely to riot (27% vs 14%), but 90% of riotous parishes had no machine on record

## Body (optional)

In 1830 farm labourers across southern and eastern England smashed threshing machines and burned ricks. Using Bruno Caprettini and Hans-Joachim Voth's open replication data, I mapped 3,117 Swing incidents and 641 recorded machines across 10,699 parishes.

Parishes with a recorded machine rioted about twice as often, and still 10 points more often than their own machine-free neighbours. But most riots happened where no machine was recorded, enclosure barely mattered (16% to 18%), and parishes spending most on poor relief rioted far more (14% to 34%).

Caveat: the machines are those that appeared in newspaper adverts or farming surveys, a sample rather than a census, and these are associations, not causes (their paper has the causal test).

Interactive version: https://tristan-hotham.github.io/captain-swing/

## Source comment

Source: Caprettini, B. and Voth, H.-J. 2020, "Rage against the Machines: Labor-Saving Technology and Unrest in Industrializing England", American Economic Review: Insights 2 (3), 305 to 320 (doi.org/10.1257/aeri.20190385); replication data on openICPSR (doi.org/10.3886/E117044V1, CC BY 4.0), including riot counts from Holland (ed.) 2005, Swing Unmasked, threshing machines from newspaper adverts and the General Views of Agriculture, 1834 Poor Law Report figures, Gonner (1912) enclosure estimates and 1851 parish boundaries. Their causal results are theirs; the maps and comparisons are mine. Context dates from Wikipedia, "Swing Riots" (CC BY-SA 4.0).

Tools: Python (pandas, NumPy, SciPy, statsmodels for the reproduction and comparisons, shapely and pyproj for the parish boundaries, matplotlib).

Interactive: https://tristan-hotham.github.io/captain-swing/
Blog post: https://blog.tristanhotham.com/2026/10/28/captain-swing/
Paper: https://doi.org/10.5281/zenodo.23727133
