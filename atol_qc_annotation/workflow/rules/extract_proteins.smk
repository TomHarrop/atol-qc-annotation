#!/usr/bin/env python3


rule check_protein_fasta_file:
    input:
        proteins=Path(workingdir, "proteins.faa"),
    output:
        proteins=Path(outdir, "proteins.faa"),
    params:
        mem_mb=lambda wildcards, resources: int(resources.mem_mb * 0.9),
    log:
        Path(logs_directory, "check_protein_fasta_file.log"),
    resources:
        mem="2GB",
    shell:
        "reformat.sh "
        "-Xmx{params.mem_mb}m "
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
