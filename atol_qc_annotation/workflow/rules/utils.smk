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
        mem_mb=lambda wildcards, resources: int(resources.mem_mb * 0.9),
    log:
        Path(logs_directory, "collect_genome_fasta_file.log"),
    benchmark:
        Path(logs_directory, "collect_genome_fasta_file.stats")
    resources:
        mem="2GB",
    shell:
        "reformat.sh "
        "-Xmx{params.mem_mb}m "
        "fixheaders=t "
        "trimreaddescription=t "
        "ignorejunk=f "
        "in={input} "
        "out={output} "
        "2>{log}"
