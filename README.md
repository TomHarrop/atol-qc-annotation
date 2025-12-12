# atol-qc-annotation

Run standardised QC on genome annotation files in GFF or GTF format. Output can
be used for the [AToL annotation
report](https://github.com/TomHarrop/atol-annotation-report).

1. Use
   [`agat_sp_extract_sequences.pl`](https://agat.readthedocs.io/en/latest/tools/agat_sp_extract_sequences.html)
   to extract and translate the coding regions. 
2. Run [BUSCO](https://gitlab.com/ezlab/busco) on the translations.
3. Run [OMArk](https://github.com/DessimozLab/OMArk) on the translations.
   1. Parse the irregular OMArk summary file into JSON.

> [!TIP]  
> For annotation statistics, run
> [AnnoOddities](https://github.com/EI-CoreBioinformatics/annooddities).
> AnnoOddities outputs a standardised GFF called `*.AnnoOddities.gff`, which
> can be used as input to `atol-qc-annotation`.

## Installation

The
[BioContainer](https://quay.io/repository/biocontainers/atol-qc-annotation?tab=tags)
is the only supported method of running `atol-qc-annotation`.

*e.g.* with Apptainer/Singularity:

```bash
apptainer exec \
  docker://quay.io/biocontainers/atol-qc-annotation \
  atol-qc-annotation --help
```


## Usage

### Input the genome FASTA file and the annotation GTF

The paths to the BUSCO, OMArk and NCBI taxonomy databases are also required.

```
atol-qc-annotation \
		--threads 12 \
		--fasta genomme.fasta \
		--annot annotation.gtf \
		--lineage_dataset eukaryota_odb10 \
		--lineages_path path/to/busco/lineages \
		--db path/to/LUCA.h5 \
		--taxid 123456 \
		--ete_ncbi_db path/to/taxa.sqlite \
		--outdir results \
		--logs logs 
```

### Reference data

- The OMArk `LUCA.h5` database can be downloaded from
[omabrowser.org](https://omabrowser.org/All/LUCA.h5)
- The BUSCO databases are from
  [busco-data.ezlab.org](https://busco-data.ezlab.org/v5/data/lineages/).
  Expand the tar.gz file and provide the path to the uncompressed directory.
- `taxa.sqlite` is the NCBI Taxonomy database as downloaded and formatted by
  the [ETE
  toolkit](https://etetoolkit.org/docs/latest/tutorial/tutorial_ncbitaxonomy.html).
  The easiest way to get a local copy is to run the following python3 code:  
  ```python3
  from ete4 import NCBITaxa
  ncbi=NCBITaxa()
  ```  
  This places the `taxa.sqlite` file in a default location
  (`~/.local/share/ete/` on Ubuntu). Move it from there to your shared data
  location.


### Output

For sample output, see the [results](./results/) directory.

### Full usage

```
usage: atol-qc-annotation [-h] [-t THREADS] [--mem MEM_GB] [-n] --fasta FASTA --annot
                          ANNOT_FILE [--lineage_dataset LINEAGE_DATASET]
                          --lineages_path LINEAGES_PATH --db OMAMER_DB --taxid TAXID
                          --ete_ncbi_db ETE_NCBI_DB --outdir OUTDIR
                          [--logs LOGS_DIRECTORY]

options:
  -h, --help            show this help message and exit
  -t THREADS, --threads THREADS
  --mem MEM_GB          Intended maximum RAM in GB. (default: 32)
  -n                    Dry run (default: False)

Input:
  --fasta FASTA         Path to the genome assembly FASTA file. (default: None)
  --annot ANNOT_FILE    Path to the genome annotation file. Any annotation format
                        recognised by agat_sp_extract_sequences works. (default:
                        None)

BUSCO settings:
  --lineage_dataset LINEAGE_DATASET
                        Name of the BUSCO lineage. (default: eukaryota_odb10)
  --lineages_path LINEAGES_PATH
                        Path to the BUSCO lineages directory. (default: None)

OMArk settings:
  --db OMAMER_DB        Path to OMAmer database. (default: None)
  --taxid TAXID         NCBI Taxonomy ID. (default: None)
  --ete_ncbi_db ETE_NCBI_DB
                        Path to the ete3-formatted NCBI Taxonomy database. (default:
                        None)

Output:
  --outdir OUTDIR       Output directory. (default: None)
  --logs LOGS_DIRECTORY
                        Log output directory. (default: None)
```

## TODO

- [x] Should this be a single monolithic pipeline with a container that has all the dependencies, or a normal pipeline that pulls the containers it needs? The second is more flexible and will perform better but will require profiles etc. to run it on HPC.
  - Doesn't actually seem to be possible: https://github.com/snakemake/snakemake/issues/1488. It has to be a single container
  - [x] BioConda recipe
- [x] Eliminate the use of temporary directories (use `temp` instead)
- [ ] Set the resources
- [x] Implement Gff to GTF conversion
- [x] Test with helixer/funannotate/tiberius output
- [x] OMARK: tool and DB version
  - for the DB:  
     ```python
    import tables
    db="test-data/omark/LUCA.h5"
    x=tables.open_file(db, mode='r')
    x.get_node_attr("/", "omamer_version")
    ```

- [x] OMARK: parse whole result/conserv lines