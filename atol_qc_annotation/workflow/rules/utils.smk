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
    params:
        mem_pct=95,  # amount to assign to java
    log:
        Path(logs_directory, "collect_genome_fasta_file.log"),
    benchmark:
        Path(logs_directory, "collect_genome_fasta_file.stats")
    retries: 5
    resources:
        mem=lambda wildcards, attempt: f"{int(2** attempt)}GB",
    shell:
        "mem_mb=$(( {resources.mem_mb} * {params.mem_pct} / 100 )) ; "
        "reformat.sh "
        "-Xmx${{mem_mb}}m "
        "fixheaders=t "
        "trimreaddescription=t "
        "ignorejunk=f "
        "in={input} "
        "out={output} "
        "2>{log} "
