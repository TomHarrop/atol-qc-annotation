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
        Path(logs_directory, "omamer_search.log"),
    container:
        containers["omark"]
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
    container:
        containers["omark"]
    shell:
        "omamer search "
        "--db {input.db} "
        "--query {input.query} "
        "--out {output.file} "
        "--nthreads {threads} "
        "&> {log}"
