#!/usr/bin/env python3


def get_annot_file(wildcards):
    return annot_files[wildcards.pipeline]


# GLOBALS

my_container = "docker://quay.io/biocontainers/atol-qc-annotation:0.1.0--pyhdfd78af_0"

annot_exts = ["gtf", "gff", "gff3"]
pipelines = ["funannotate", "braker3", "tiberius"]
run_types = ["local", "dev", "biocontainer"]

genome = "test-data/rgram/R_gram.fasta"
annot_glob = "test-data/rgram/{pipeline}.{annot_ext}"

# MAIN

matches = glob_wildcards(annot_glob)
annot_files = {
    p: annot_glob.format(pipeline=p, annot_ext=e)
    for p, e in zip(matches.pipeline, matches.annot_ext)
    if p in pipelines and e in annot_exts
}


wildcard_constraints:
    annot_ext="|".join(annot_exts),
    pipeline="|".join(pipelines),
    run_type="|".join(run_types),


rule atol_qc_annotation:
    input:
        fasta=genome,
        annot_file=get_annot_file,
        omark_db="test-data/omark/LUCA.h5",
        taxdb="test-data/omark/ete/taxa.sqlite",
    output:
        stats="test-output/{run_type}/rgram/{pipeline}/agat.stats.yaml",
    params:
        call=lambda wildcards: (
            (
                "python3 -m cProfile -o "
                f"test-output/{wildcards.run_type}/rgram/{wildcards.pipeline}/cProfile.stats "
                "-m atol_qc_annotation.__main__"
            )
            if wildcards.run_type != "biocontainer"
            else "atol-qc-annotation"
        ),
        dev_container=lambda wildcards: (
            f"--dev_container {my_container}" if wildcards.run_type == "dev" else ""
        ),
        lineage="helotiales_odb10",
        lineages_path="test-data/busco/lineages",
        taxid=2792576,
        outdir=subpath(output.stats, parent=True),
    threads: 12
    container:
        lambda wildcards: my_container if wildcards.run_type == "biocontainer" else None
    shell:
        "{params.call} "
        "--threads {threads} "
        "{params.dev_container} "
        "--fasta {input.fasta} "
        "--gtf {input.annot_file} "
        "--lineage_dataset {params.lineage} "
        "--lineages_path {params.lineages_path} "
        "--db {input.omark_db} "
        "--taxid {params.taxid} "
        "--ete_ncbi_db {input.taxdb} "
        "--outdir {params.outdir} "
        "--logs {params.outdir}/logs "


rule test_biocontainer:
    input:
        expand(
            rules.atol_qc_annotation.output,
            run_type="biocontainer",
            pipeline=pipelines,
        ),


rule test_local:
    input:
        expand(
            rules.atol_qc_annotation.output,
            run_type="local",
            pipeline=pipelines,
        ),


rule test_dev:
    input:
        expand(
            rules.atol_qc_annotation.output,
            run_type="dev",
            pipeline=pipelines,
        ),


rule target:
    default_target: True
    input:
        rules.test_biocontainer.input,
        rules.test_dev.input,
        rules.test_local.input,
