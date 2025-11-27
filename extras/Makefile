shell=/bin/bash

local_version := $(shell python3 -m setuptools_scm)
tmpdir := $(shell mktemp -d)
branch := $(shell git rev-parse --abbrev-ref HEAD)
RESULTDIR := "test-output"

test_braker_gtf:
	mkdir -p $(RESULTDIR)/profiling
	python3 -m cProfile -o "test-output/profiling/test_braker_gtf.cProfile.stats" \
	-m atol_qc_annotation.__main__ \
		--fasta test-data/genome.fa \
		--gtf test-data/braker.gtf \
		--lineage_dataset embryophyta_odb10 \
		--lineages_path test-data/busco/lineages \
		--outdir test-output/test_braker_gtf \
		--logs test-output/test_braker_gtf/logs 
