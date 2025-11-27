#!/usr/bin/env python3

rule busco:
    input:
        protein="results/tiberius/proteins/{genome}.faa",
    output:
        json="results/tiberius/busco/{genome}/{genome}.json",
    params:
        busco_db=get_busco_db,
        lineage=get_lineage_name,
        outdir="results/tiberius/busco/{genome}",
    resources:
        mem="32G",
        runtime=180,
    log:
        "logs/busco/{genome}.log",
    container:
        busco
    shell:
        "busco "
        "-i {input.protein} "
        "-o {params.outdir} "
        "-l {params.busco_db} "
        "-m protein "
        "--force "
        "&> {log}; "
        "cp {params.outdir}/short_summary.specific.{params.lineage}.{wildcards.genome}.json {output.json}"

