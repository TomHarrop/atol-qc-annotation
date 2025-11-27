#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from importlib import resources
from importlib.metadata import metadata, files
from pathlib import Path
from snakemake.logging import logger
import argparse
import tempfile
from snakemake.api import (
    ConfigSettings,
    DAGSettings,
    DeploymentSettings,
    ExecutionSettings,
    OutputSettings,
    ResourceSettings,
    SnakemakeApi,
    StorageSettings,
)
from snakemake.settings.enums import Quietness, RerunTrigger
from snakemake.settings.types import DeploymentMethod


def parse_arguments():
    parser = argparse.ArgumentParser()

    # options
    parser.add_argument("-t", "--threads", type=int, default=16, dest="threads")
    parser.add_argument("-n", help="Dry run", dest="dry_run", action="store_true")

    # inputs
    input_group = parser.add_argument_group("Input")
    input_group.add_argument(
        "--fasta",
        "-f",
        required=True,
        type=Path,
        help="Path to the genome assembly FASTA file",
        dest="fasta",
    )
    annot_group = input_group.add_mutually_exclusive_group(required=True)

    annot_group.add_argument(
        "--gtf",
        type=Path,
        help="Path to the genome annotation GTF file.",
        dest="gtf",
    )

    annot_group.add_argument(
        "--gff",
        "-g",
        type=Path,
        help=(
            "Path to the genome annotation GFF file"
            "NOTE: will be converted to GTF for analysis."
        ),
        dest="gff",
    )

    # tool settings
    busco_group = parser.add_argument_group("BUSCO settings")

    busco_group.add_argument(
        "--lineage_dataset",
        "-l",
        default="eukaryota_odb10",
        type=str,
        help="Specify the name of the BUSCO lineage to be used. Default: eukaryota_odb10",
        dest="lineage_dataset",
    )

    busco_group.add_argument(
        "--lineages_path",
        type=Path,
        help="Path to the BUSCO lineages directory.",
        dest="lineages_path",
    )

    # outputs
    output_group = parser.add_argument_group("Output")

    output_group.add_argument(
        "--outdir",
        required=True,
        type=posixpath,
        help="Output directory",
        dest="outdir",
    )

    output_group.add_argument(
        "--logs",
        required=False,
        type=posixpath,
        help="Log output directory. Default: logs are discarded.",
        dest="logs_directory",
    )

    return parser.parse_args()


def posixpath(x):
    return Path(x).as_posix()


def main():
    # print version info
    pkg_metadata = metadata(__package__)

    pkg_name = pkg_metadata.get("Name")
    pkg_version = pkg_metadata.get("Version")

    logger.warning(f"{pkg_name} version {pkg_version}")

    # get the snakefile
    package_path = resources.files(__package__)
    snakefile = Path(package_path, "workflow", "Snakefile")

    if snakefile.is_file():
        logger.debug(f"Using snakefile {snakefile}")
    else:
        raise FileNotFoundError("Could not find a Snakefile")

    container_config = Path(package_path, "config", "containers.yaml")
    if container_config.is_file():
        logger.debug(f"Using container_config {container_config}")
    else:
        raise FileNotFoundError("Could not find container_config")

    # get arguments
    args = parse_arguments()
    logger.debug(f"Entrypoint args:\n    {args}")

    # set up a working directory for this run
    workingdir = tempfile.mkdtemp()
    args.workingdir = workingdir

    # control output
    output_settings = OutputSettings(
        quiet={
            Quietness.HOST,
            Quietness.REASON,
            Quietness.PROGRESS,
        },
        printshellcmds=True,
    )

    # set cores.
    resource_settings = ResourceSettings(
        cores=args.threads,
        overwrite_resource_scopes={
            "mem": "global",
            "threads": "global",
        },
    )

    # control rerun triggers
    dag_settings = DAGSettings(rerun_triggers={RerunTrigger.INPUT})

    # other settings
    config_settings = ConfigSettings(
        config=args.__dict__, configfiles=[container_config]
    )
    execution_settings = ExecutionSettings(lock=False)
    storage_settings = StorageSettings(notemp=True)
    deployment_settings = DeploymentSettings(
        deployment_method=[DeploymentMethod.APPTAINER]
    )

    with SnakemakeApi(output_settings) as snakemake_api:
        workflow_api = snakemake_api.workflow(
            snakefile=snakefile,
            resource_settings=resource_settings,
            config_settings=config_settings,
            storage_settings=storage_settings,
            deployment_settings=deployment_settings,
        )
        dag = workflow_api.dag(dag_settings=dag_settings)

        dag.execute_workflow(
            executor="dryrun" if args.dry_run else "local",
            execution_settings=execution_settings,
        )


if __name__ == "__main__":
    main()
