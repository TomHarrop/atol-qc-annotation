#!/usr/bin/env python3
rule agat_sp_statistics:
    input:
        gff=Path(outdir, "agat.fix_cds_phases.gff"),
        fasta=Path(workingdir, "genome.fasta"),
    output:
        txt=Path(outdir, "agat.stats"),
        yaml=Path(outdir, "agat.stats.yaml"),
    log:
        Path(logs_directory, "agat_sp_statistics.log"),
    container:
        containers["agat"]
    shadow:
        "minimal"
    shell:
        "agat_sp_statistics.pl "
        "--gff {input.gff} "
        "-f {input.fasta} "
        "--yaml "
        "--output {output.txt} "
        "&> {log}"


rule agat_sp_fix_cds_phases:
    input:
        gff=Path(workingdir, "agat.flag_premature.gff"),
        fasta=Path(workingdir, "genome.fasta"),
    output:
        gff=Path(outdir, "agat.fix_cds_phases.gff"),
    log:
        Path(logs_directory, "agat_sp_fix_cds_phases.log"),
    container:
        containers["agat"]
    shadow:
        "minimal"
    shell:
        "agat_sp_fix_cds_phases.pl "
        "--gff {input.gff} "
        "--fasta {input.fasta} "
        "--output {output.gff} "
        "&> {log}"


rule agat_sp_flag_premature_stop_codons:
    input:
        gff=Path(workingdir, "agat.filter_incomplete.gff"),
        fasta=Path(workingdir, "genome.fasta"),
    output:
        gff=temp(Path(workingdir, "agat.flag_premature.gff")),
    log:
        Path(logs_directory, "agat_sp_flag_premature_stop_codons.log"),
    container:
        containers["agat"]
    shadow:
        "minimal"
    shell:
        "agat_sp_flag_premature_stop_codons.pl "
        "--gff {input.gff} "
        "--fasta {input.fasta} "
        "--output {output.gff} "
        "&> {log}"


rule agat_sp_filter_incomplete_gene_coding_models:
    input:
        gtf=Path(workingdir, "input.gtf"),
        fasta=Path(workingdir, "genome.fasta"),
    output:
        gff=temp(Path(workingdir, "agat.filter_incomplete.gff")),
    log:
        Path(
            logs_directory, "agat_sp_filter_incomplete_gene_coding_models.log"
        ).as_posix(),
    container:
        containers["agat"]
    shadow:
        "minimal"
    shell:
        "agat_sp_filter_incomplete_gene_coding_models.pl "
        "--gff {input.gtf} "
        "--fasta {input.fasta} "
        "--add_flag "
        "--output {output.gff} "
        "&> {log} "
