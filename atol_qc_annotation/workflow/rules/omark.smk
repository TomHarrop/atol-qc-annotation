#!/usr/bin/env python3

omark_files = [
    "_detailed_summary.txt",
    ".omq",
    ".pdf",
    ".png",
    ".sum",
    ".tax",
    ".ump",
]


rule parse_omark_sum_file:
    input:
        sum_file=Path(outdir, "omark", "proteins.sum"),
        db=omamer_db,
        omamer_search_log=Path(logs_directory, "omamer_search.log"),
    output:
        json=Path(outdir, "omark_summary.json"),
    log:
        Path(logs_directory, "parse_omark_sum_file.log"),
    benchmark:
        Path(logs_directory, "parse_omark_sum_file.stats")
    shell:
        "parse-omark-sum-file "
        "--sum_file {input.sum_file} "
        "--database {input.db} "
        "--omamer_search_log {input.omamer_search_log} "
        "--output {output.json} "
        "2>{log}"


rule omark:
    input:
        file=Path(workingdir, "proteins.omamer"),
        db=omamer_db,
        ete_ncbi_db=ete_ncbi_db,
    output:
        multiext(Path(outdir, "omark", "proteins").as_posix(), *omark_files),
    params:
        taxid=taxid,
        outdir=subpath(output[0], parent=True),
    log:
        Path(logs_directory, "omark.log"),
    benchmark:
        Path(logs_directory, "omark.stats")
    resources:
        mem="4GB",
    shell:
        "omark  "
        "--file {input.file} "
        "--database {input.db} "
        "--ete_ncbi_db {input.ete_ncbi_db} "
        "--taxid {params.taxid} "
        "--outputFolder {params.outdir} "
        "&> {log}"


rule omamer_search:
    input:
        db=omamer_db,
        query=Path(outdir, "proteins.faa"),
    output:
        file=temp(Path(workingdir, "proteins.omamer")),
    log:
        Path(logs_directory, "omamer_search.log"),
    benchmark:
        Path(logs_directory, "omamer_search.stats")
    threads: int(workflow.cores - 1)
    resources:
        mem="16GB",
    shell:
        "omamer search "
        "--db {input.db} "
        "--query {input.query} "
        "--out {output.file} "
        "--nthreads {threads} "
        "&> {log}"
