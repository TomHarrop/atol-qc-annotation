#!/usr/bin/env python3


rule check_protein_fasta_file:
    input:
        proteins=Path(workingdir, "proteins.faa"),
    output:
        proteins=Path(outdir, "proteins.faa"),
    log:
        Path(logs_directory, "check_protein_fasta_file.log"),
    container:
        containers["bbmap"]
    shell:
        "reformat.sh "
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
        proteins=Path(workingdir, "proteins.faa"),
    log:
        Path(logs_directory, "extract_proteins.log"),
    container:
        containers["agat"]
    shadow:
        "minimal"
    shell:
        "agat_sp_extract_sequences.pl "
        "--gff {input.gff} "
        "--fasta {input.genome} "
        "--protein "
        "--output {output.proteins} "
        "&> {log}"
