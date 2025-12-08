#!/usr/bin/env python3


rule collect_busco_output:
    input:
        json=Path(
            outdir, "busco", f"short_summary.specific.{lineage_dataset}.busco.json"
        ),
        txt=Path(outdir, "busco", f"short_summary.specific.{lineage_dataset}.busco.txt"),
    output:
        json=Path(outdir, "short_summary.specific.busco.json"),
        txt=Path(outdir, "short_summary.specific.busco.txt"),
    shell:
        "cp {input.json} {output.json} && "
        "cp {input.txt} {output.txt}"


rule busco:
    input:
        proteins=Path(outdir, "proteins.faa"),
        busco_db=Path(lineages_path, lineage_dataset),
    output:
        json=temp(
            Path(
                outdir, "busco", f"short_summary.specific.{lineage_dataset}.busco.json"
            )
        ),
        txt=temp(
            Path(
                outdir, "busco", f"short_summary.specific.{lineage_dataset}.busco.txt"
            )
        ),
    params:
        outdir=subpath(output.json, parent=True),
    log:
        Path(logs_directory, "busco.log"),
    benchmark:
        Path(logs_directory, "busco.stats")
    threads: int(workflow.cores - 1)
    resources:
        mem="32GB",
    shadow:
        "minimal"
    shell:
        "busco "
        "--cpu {threads} "
        "--force "
        "--in {input.proteins} "
        "--lineage_dataset {input.busco_db} "
        "--mode protein "
        "--offline "
        "--out {params.outdir} "
        "&> {log}"
