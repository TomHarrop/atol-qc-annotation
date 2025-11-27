#!/usr/bin/env python3

if gff:

    # gtf variable is set by this rule
    include: "convert_gff_to_gtf.smk"

else:

    rule collect_gtf:
        input:
            gtf,
        output:
            Path(workingdir, "input.gtf"),
        shell:
            "cp {input} {output}"


rule collect_genome_fasta_file:
    input:
        fasta=fasta,
    output:
        Path(workingdir, "genome.fasta"),
    log:
        Path(logs_directory, "collect_genome_fasta_file.log"),
    container:
        containers["bbmap"]
    shell:
        "reformat.sh "
        "fixheaders=t "
        "trimreaddescription=t "
        "ignorejunk=f "
        "in={input} "
        "out={output} "
        "2>{log}"
