#!/usr/bin/env python3


# GLOBALS

my_container = "docker://quay.io/biocontainers/atol-qc-annotation:0.1.2--pyhdfd78af_0"

pipelines = ["braker3", "funannotate", "helixer", "tiberius"]

genome = "test-data/rgram/R_gram.fasta"
annot_glob = "test-data/rgram/{pipeline}.{annot_ext}"

outdir = "test-output/rgram/{run_type}/{pipeline}"


lineage = "helotiales_odb10"
taxid = 2792576


include: "test_rules.smk"


rule rgram_target:
    default_target: True
    input:
        rules.test_biocontainer.input,
        rules.test_dev.input,
