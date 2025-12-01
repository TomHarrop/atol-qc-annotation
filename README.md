# atol-qc-annotation

## TODO

- [ ] Should this be a single monolithic pipeline with a container that has all the dependencies, or a normal pipeline that pulls the containers it needs? The second is more flexible and will perform better but will require profiles etc. to run it on HPC.
  - Doesn't actually seem to be possible: https://github.com/snakemake/snakemake/issues/1488. It has to be a single container
  - [ ] BioConda recipe
- [x] Eliminate the use of temporary directories (use `temp` instead)
- [ ] Set the resources
- [ ] Implement Gff to GTF conversion
- [ ] Test with helixer/funannotate/tiberius output