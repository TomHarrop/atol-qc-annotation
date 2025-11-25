gff = Path(workingdir, "input.gff")


rule convert_gtf_to_gff:
    input:
        gtf,
    output:
        gff,
    container:
        containers["gffread"]
    shell:
        
