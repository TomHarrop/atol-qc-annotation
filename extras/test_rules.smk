#!/usr/bin/env python3


from pathlib import Path


def format_call(wildcards):
    if wildcards.run_type == "biocontainer":
        return "atol-qc-annotation"
    else:
        formatted_outdir = outdir.format(**wildcards)
        call = (
            "python3 -m cProfile -o "
            f"{formatted_outdir}/cProfile.stats "
            "-m atol_qc_annotation.__main__"
        )
        return call


def get_annot_file(wildcards):
    return annot_files[wildcards.pipeline]


filenames = [
    "omark_summary.json",
    "proteins.faa",
    "short_summary.specific.busco.json",
    "short_summary.specific.busco.txt",
]

annot_exts = ["gtf", "gff", "gff3"]
run_types = [
    "dev",
    "biocontainer",
]  # add "local" to test against locally installed deps

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
        annot=get_annot_file,
        omark_db="test-data/omark/LUCA.h5",
        taxdb="test-data/omark/ete/taxa.sqlite",
    output:
        [Path(outdir, x).as_posix() for x in filenames],
    params:
        call=format_call,
        dev_container=lambda wildcards: (
            f"--dev_container {my_container}" if wildcards.run_type == "dev" else ""
        ),
        lineage=lineage,
        lineages_path="test-data/busco/lineages",
        taxid=taxid,
        outdir=subpath(output[0], parent=True),
    threads: 12
    container:
        lambda wildcards: my_container if wildcards.run_type == "biocontainer" else None
    shell:
        "{params.call} "
        "--threads {threads} "
        "{params.dev_container} "
        "--fasta {input.fasta} "
        "--annot {input.annot} "
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
