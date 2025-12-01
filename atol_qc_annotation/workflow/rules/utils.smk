#!/usr/bin/env python3


rule collect_gtf:
    input:
        gtf,
    output:
        temp(Path(workingdir, "input.gtf")),
    shell:
        "cp {input} {output}"


rule collect_genome_fasta_file:
    input:
        fasta=fasta,
    output:
        temp(Path(workingdir, "genome.fasta")),
    log:
        Path(logs_directory, "collect_genome_fasta_file.log"),
    benchmark:
        Path(logs_directory, "collect_genome_fasta_file.stats")
    shell:
        "reformat.sh "
        "fixheaders=t "
        "trimreaddescription=t "
        "ignorejunk=f "
        "in={input} "
        "out={output} "
        "2>{log}"
