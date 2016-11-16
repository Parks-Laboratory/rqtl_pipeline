## Synopsis
Snippets of code that are commonly used in R/QTL mapping. Each snippet should be viewed as an independent test, 
and is intended to function independently of the other snippets.

This is an example snippet:
```
######################################################################################################
##  Remove markers that are adjacent and duplicates
######################################################################################################
duplicate_markers = unlist(findDupMarkers(cross, exact.only=TRUE, adjacent.only = TRUE))
cross = drop.markers(cross, duplicate_markers)
```

## Usage
1. Open **rqtl_mapping.r** with RStudio/RGui
2. Set parameters for read.cross()
3. Load an R/QTL cross object by selecting and running either Option 1 or Option 2 under heading "Read in data"
4. Alter snippet, select it, run it

