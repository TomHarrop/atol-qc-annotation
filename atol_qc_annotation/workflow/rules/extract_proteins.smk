#!/usr/bin/env python3


rule check_protein_fasta_file:
    input:
        proteins=Path(workingdir, "proteins.faa"),
    output:
        proteins=Path(outdir, "proteins.faa"),
    params:
        mem_pct=95,  # amount to assign to java
    log:
        Path(logs_directory, "check_protein_fasta_file.log"),
    retries: 5
    resources:
        mem=lambda wildcards, attempt: f"{int(2** attempt)}GB",
    shell:
        "mem_mb=$(( {resources.mem_mb} * {params.mem_pct} / 100 )) ; "
        "reformat.sh "
        "-Xmx${{mem_mb}}m "
        "fixheaders=t "
        "trimreaddescription=t "
        "ignorejunk=t "
        "in={input} "
        "out={output} "
        "2>{log}"


rule extract_proteins:
    input:
        gff=Path(outdir, "agat.fix_cds_phases.gff"),
        genome=Path(workingdir, "genome.fasta"),
    output:
        proteins=temp(Path(workingdir, "proteins.faa")),
    log:
        Path(logs_directory, "extract_proteins.log"),
    benchmark:
        Path(logs_directory, "extract_proteins.stats")
    shadow:
        "minimal"
    shell:
        "agat_sp_extract_sequences.pl "
        "--gff {input.gff} "
        "--fasta {input.genome} "
        "--protein "
        "--output {output.proteins} "
        "&> {log}"
