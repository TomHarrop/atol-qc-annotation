#!/usr/bin/env python3


rule busco:
    input:
        proteins=Path(outdir, "proteins.faa"),
        busco_db=Path(lineages_path, lineage_dataset),
    output:
        json=Path(
            outdir, "busco", f"short_summary.specific.{lineage_dataset}.busco.json"
        ),
        txt=Path(outdir, "busco", f"short_summary.specific.{lineage_dataset}.busco.txt"),
    params:
        outdir=subpath(output.json, parent=True),
    log:
        Path(logs_directory, "busco.log"),
    container:
        containers["busco"]
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
        "&> {log} "
