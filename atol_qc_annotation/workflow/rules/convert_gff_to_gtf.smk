#!/usr/bin/env python3

# TODO


rule convert_gff_to_gtf:
    input:
        gff,
    output:
        temp(Path(workingdir, "input.gtf")),
    shell:
        "echo {input} ; exit 1 "
