shell=/bin/bash

local_version := $(shell python3 -m setuptools_scm)
tmpdir := $(shell mktemp -d)
branch := $(shell git rev-parse --abbrev-ref HEAD)
RESULTDIR := test-output
CONTAINER := atol-qc-annotation---0.0.4--pyhdfd78af_0.sif

# Discover all GTFs and map them to expected outputs
GTFS := $(wildcard test-data/rgram/*.gtf)
GFFS := $(wildcard test-data/rgram/*.gff)
STEMS := $(patsubst test-data/rgram/%.gtf,%,$(GTFS)) $(patsubst test-data/rgram/%.gff,%,$(GFFS))
TARGETS := $(addprefix $(RESULTDIR)/rgram/,$(addsuffix /agat.stats.yaml,$(sort $(STEMS))))

.PHONY: rgram
rgram: $(TARGETS)

dir_guard = @mkdir -p $(@D)

# Enable second expansion so $* can be used in prerequisites
.SECONDEXPANSION:

$(RESULTDIR)/rgram/%/agat.stats.yaml: $$(if $$(wildcard test-data/rgram/$$*.gtf),test-data/rgram/$$*.gtf,test-data/rgram/$$*.gff)
	$(dir_guard) ;
	python3 -m cProfile -o $(RESULTDIR)/rgram/$*/cProfile.stats \
		-m atol_qc_annotation.__main__ \
		--threads 12 \
		--dev_container $(CONTAINER) \
		--fasta test-data/rgram/R_gram.fasta \
		--gtf $< \
		--lineage_dataset helotiales_odb10 \
		--lineages_path test-data/busco/lineages \
		--db test-data/omark/LUCA.h5 \
		--taxid 2792576 \
		--ete_ncbi_db test-data/omark/ete/taxa.sqlite \
		--outdir $(RESULTDIR)/rgram/$* \
		--logs $(RESULTDIR)/rgram/$*/logs 


# add the following switch to run in the dev container
# 		--dev_container "atol-qc-annotation---0.0.2--pyhdfd78af_0.sif" \
# 		

test_braker_gtf: 
	$(dir_guard) ;
	python3 -m cProfile -o "test-output/test_braker_gtf/cProfile.stats" \
	-m atol_qc_annotation.__main__ \
		--threads 12 \
		--dev_container $(CONTAINER) \
		--fasta test-data/genome.fa \
		--gtf test-data/braker.gtf \
		--lineage_dataset embryophyta_odb10 \
		--lineages_path test-data/busco/lineages \
		--db test-data/omark/LUCA.h5 \
		--taxid 3702 \
		--ete_ncbi_db test-data/omark/ete/taxa.sqlite \
		--outdir test-output/test_braker_gtf \
		--logs test-output/test_braker_gtf/logs 


changelog: CHANGELOG.md

CHANGELOG.md: .git/index
	gitchangelog > $(tmpdir)/CHANGELOG.md
	apptainer exec docker://davidanson/markdownlint-cli2:v0.13.0 \
	markdownlint-cli2 \
	--fix \
	:$(tmpdir)/CHANGELOG.md || true
	mv $(tmpdir)/CHANGELOG.md ./CHANGELOG.md
	git add CHANGELOG.md
	git commit -m 'changelog !cosmetic'
	git push origin $(branch)
