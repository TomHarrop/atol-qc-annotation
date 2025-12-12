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

    parser.add_argument(
        "-m",
        "--mem",
        help="Intended maximum RAM in GB.",
        type=int,
        default=32,
        dest="mem_gb",
    )

    parser.add_argument(
        "--dev_container",
        help="For development use. Specify a container to run all the jobs in.",
        type=str,
        dest="dev_container",
    )

    parser.add_argument("-n", help="Dry run", dest="dry_run", action="store_true")

    # inputs
    input_group = parser.add_argument_group("Input")
    input_group.add_argument(
        "--fasta",
        "-f",
        required=True,
        type=posixpath,
        help="Path to the genome assembly FASTA file",
        dest="fasta",
    )
    input_group.add_argument(
        "--annot",
        type=posixpath,
        help=(
            "Path to the genome annotation file. "
            "Any annotation format recognised by agat_sp_extract_sequences works."
        ),
        dest="annot_file",
    )

    # tool settings
    busco_group = parser.add_argument_group("BUSCO settings")

    busco_group.add_argument(
        "--lineage_dataset",
        "-l",
        required=True,
        default="eukaryota_odb10",
        type=str,
        help="Specify the name of the BUSCO lineage to be used. Default: eukaryota_odb10",
        dest="lineage_dataset",
    )

    busco_group.add_argument(
        "--lineages_path",
        required=True,
        type=posixpath,
        help="Path to the BUSCO lineages directory.",
        dest="lineages_path",
    )

    omark_group = parser.add_argument_group("OMArk settings")
    omark_group.add_argument(
        "--db",
        type=posixpath,
        help="OMAmer database",
        required=True,
        dest="omamer_db",
    )
    omark_group.add_argument(
        "--taxid",
        type=int,
        help="NCBI Taxonomy ID",
        required=True,
        dest="taxid",
    )

    omark_group.add_argument(
        "--ete_ncbi_db",
        type=posixpath,
        help="Path to the ete3 NCBI database to be used.",
        required=True,
        dest="ete_ncbi_db",
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

    # get arguments
    args = parse_arguments()
    logger.debug(f"Entrypoint args:\n    {args}")

    # set up a working directory for this run
    workingdir = Path(args.outdir, "tmp").as_posix()
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
        resources={"mem_mb": int(args.mem_gb * 1024)},
        overwrite_resource_scopes={
            "mem": "global",
            "threads": "global",
        },
    )

    # control rerun triggers
    dag_settings = DAGSettings(rerun_triggers={RerunTrigger.INPUT})

    # other settings
    config_settings = ConfigSettings(config=args.__dict__)
    execution_settings = ExecutionSettings(lock=False)
    storage_settings = StorageSettings(notemp=True if args.dev_container else False)

    # use apptainer if there is a dev container
    deployment_method = [DeploymentMethod.APPTAINER] if args.dev_container else []
    deployment_settings = DeploymentSettings(deployment_method=deployment_method)

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
