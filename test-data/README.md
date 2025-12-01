### Source of the test files:

#### Reference data

LUCA.h5
: https://omabrowser.org/All/LUCA.h5

eukaryota_odb10
: https://busco-data.ezlab.org/v5/data/lineages/eukaryota_odb10.2024-01-08.tar.gz

taxa.sqlite

```python3

from ete4 import NCBITaxa

# downloads to a hard-coded location
# ~/.local/share/ete/
ncbi=NCBITaxa()

```


#### Braker3 input test

genome.fa
: https://github.com/Gaius-Augustus/BRAKER/blob/master/example/genome.fa

braker.gtf
: https://github.com/Gaius-Augustus/BRAKER/blob/master/example/results/test3_4/braker.gtf


#### Rgram tests

Private data - from Jane Tung's annotation project.