#!/usr/bin/env python3


# GLOBALS

my_container = "docker://quay.io/biocontainers/atol-qc-annotation:0.1.2--pyhdfd78af_0"

pipelines = ["braker"]  # TODO: add more tests

genome = "test-data/genome.fa"
annot_glob = "test-data/{pipeline}.{annot_ext}"

outdir = "test-output/{run_type}/{pipeline}"

lineage = "embryophyta_odb10"
taxid = 3702


include: "test_rules.smk"


rule tests_target:
    default_target: True
    input:
        rules.test_biocontainer.input,
        rules.test_dev.input,
