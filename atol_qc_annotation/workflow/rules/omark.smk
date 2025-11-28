#!/usr/bin/env python3


rule omark:
    input:
        file=Path(workingdir, "proteins.omamer"),
        db=omamer_db,
        ete_ncbi_db=ete_ncbi_db,
    output:
        omark=directory(Path(outdir, "omark")),
    params:
        taxid=taxid,
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
        "--outputFolder {output.omark} "
        "&> {log}"


rule omamer_search:
    input:
        db=omamer_db,
        query=Path(outdir, "proteins.faa"),
    output:
        file=Path(workingdir, "proteins.omamer"),
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
