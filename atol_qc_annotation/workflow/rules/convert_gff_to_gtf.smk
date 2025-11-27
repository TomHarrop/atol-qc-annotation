#!/usr/bin/env python3


rule convert_gff_to_gtf:
    input:
        gff,
    output:
        Path(workingdir, "input.gtf"),
    container:
        containers["gffread"]
    shell:
        "echo {input} ; exit 1 "
