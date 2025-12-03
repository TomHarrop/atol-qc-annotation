#!/usr/bin/env python3

"""
Inspired by / based on https://github.com/DessimozLab/OMArk/blob/main/utils/plot_all_results.py
"""

from pathlib import Path
import argparse
import json
import re
import sys
import tables


def get_db_version(database):
    with tables.open_file(database, mode="r") as db:
        db_version = db.get_node_attr("/", "omamer_version")
    return db_version


def get_omamer_version(omamer_search_log):
    log_text = omamer_search_log.read_text()
    # OMAmer version (line like: " - version: 2.1.0")
    m = re.search(r"^\s*-\s*version:\s*([0-9.]+)\s*$", log_text, re.MULTILINE)
    omamer_version = m.group(1) if m else None
    return omamer_version


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sum_file", type=Path, required=True)
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--omamer_search_log", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def parse_single_line(line, type_to_return, regex_string, result_index):
    results = re.search(regex_string, line)
    if not results:
        return False, None
    val = results.group(result_index)
    if val is None or val == "":
        return True, None
    return True, type_to_return(val)


def parse_sum_file(sum_file):
    in_contaminant_line = False
    results_dict = {}
    detected_species = []

    lines = [x.rstrip() for x in open(sum_file, "rt").readlines()]
    for line in lines:
        if not in_contaminant_line:
            search_result = single_line_search(line, single_line_regexes)

            if search_result:
                results_dict[search_result[0]] = search_result[1]

            result_counts = results_line_search(
                line, int, result_line_regexes["counts"]
            )
            if result_counts:
                results_dict["results_counts"] = result_counts

            results_pcts = results_line_search(line, float, result_line_regexes["pcts"])
            if results_pcts:
                results_dict["results_pcts"] = results_pcts

            conserv_counts = results_line_search(
                line, int, conserv_line_regexes["counts"]
            )
            if conserv_counts:
                results_dict["conserv_counts"] = conserv_counts

            conserv_pcts = results_line_search(
                line, float, conserv_line_regexes["pcts"]
            )
            if conserv_pcts:
                results_dict["conserv_pcts"] = conserv_pcts

            # The contaminant section comes directly after this header until
            # the end of the file.
            if line == "#From HOG placement, the detected species are:":
                in_contaminant_line = True

        else:
            # THIS IS THE CONTAMINANT SECTION
            # skip blanks
            if line == "":
                continue

            # get headers from the defline
            if line.startswith("#"):
                splits = line.split("\t")
                headers = [
                    re.sub(r"\s+", "_", re.sub(r"[^A-Za-z\s]", "", s)).strip("_")
                    for s in splits
                ]
                continue

            contam_splits = line.strip().split("\t")
            cast_splits = []
            for sp, cl in zip(contam_splits, contam_field_classes):
                try:
                    cast_splits.append(cl(sp))
                except ValueError:
                    cast_splits.append(cl(sp.strip("%")))

            detected_species.append(dict(zip(headers, cast_splits)))

    # add the contaminants ("detected species") to the results
    results_dict["detected_species"] = detected_species

    return results_dict


def results_line_search(line, type_to_return, regex):
    search_result = re.search(regex, line)
    if search_result:
        result_dict = {
            k: type_to_return(v) for k, v in search_result.groupdict().items()
        }
        return result_dict


def single_line_search(line, single_line_regexes):
    for k, v in single_line_regexes.items():
        matched, value = parse_single_line(line, v[0], v[1], v[2])
        if matched:
            return (k, value)


def main():

    args = parse_arguments()

    summary_information = parse_sum_file(args.sum_file)

    summary_information["omamer_version"] = get_omamer_version(args.omamer_search_log)
    summary_information["db_version"] = get_db_version(args.database)

    # write the output
    json.dump(summary_information, open(args.output, "wt"))


# Parsing config. Keys are the name of the item. Value is a tuple of type,
# regex string and index in result.
contam_field_classes = [str, int, int, float]

conserv_line_regexes = {
    "counts": (
        r"""^S:(?P<single>\d+)"""
        r""",D:(?P<duplicated>\d+)"""
        r"""\[U:(?P<duplicated_unexpected>\d+),"""
        r"""E:(?P<duplicated_expected>\d+)\],"""
        r"""M:(?P<missing>\d+)\s*$"""
    ),
    "pcts": (
        r"""^S:(?P<single>\d+(?:\.\d+)?)%"""
        r""",D:(?P<duplicated>\d+(?:\.\d+)?)%"""
        r"""\[U:(?P<duplicated_unexpected>\d+(?:\.\d+)?)%,"""
        r"""E:(?P<duplicated_expected>\d+(?:\.\d+)?)%\],"""
        r"""M:(?P<missing>\d+(?:\.\d+)?)%\s*$"""
    ),
}


single_line_regexes = {
    "selected_clade": (str, r"^#The selected clade was\s?+(\w+)", 1),
    "conserved_hogs": (int, r"^#Number of conserved HOGs is\:\s?+([0-9]+)", 1),
    "results_on_conserved_hogs": (
        int,
        r"^#Results on conserved HOGs is:\s*(\d+)?\s*$",
        1,
    ),
    "proteins_in_proteome": (
        int,
        r"#On the whole proteome, there are (\d+) proteins",
        1,
    ),
}

result_line_regexes = {
    "counts": (
        r"""^A:(?P<consistent>\d+)"""
        r"""\[P:(?P<consistent_partial_hits>\d+),"""
        r"""F:(?P<consistent_fragmented>\d+)\],"""
        r"""I:(?P<inconsistent>\d+)"""
        r"""\[P:(?P<inconsistent_partial_hits>\d+),"""
        r"""F:(?P<inconsistent_fragmented>\d+)\],"""
        r"""C:(?P<likely_contamination>\d+)"""
        r"""\[P:(?P<likely_contamination_partial_hits>\d+),"""
        r"""F:(?P<likely_contamination_fragmented>\d+)\],"""
        r"""U:(?P<unknown>\d+)\s*$"""
    ),
    "pcts": (
        r"""^A:(?P<consistent>\d+(?:\.\d+)?)%"""
        r"""\[P:(?P<consistent_partial_hits>\d+(?:\.\d+)?)%,"""
        r"""F:(?P<consistent_fragmented>\d+(?:\.\d+)?)%\],"""
        r"""I:(?P<inconsistent>\d+(?:\.\d+)?)%"""
        r"""\[P:(?P<inconsistent_partial_hits>\d+(?:\.\d+)?)%,"""
        r"""F:(?P<inconsistent_fragmented>\d+(?:\.\d+)?)%\],"""
        r"""C:(?P<likely_contamination>\d+(?:\.\d+)?)%"""
        r"""\[P:(?P<likely_contamination_partial_hits>\d+(?:\.\d+)?)%,"""
        r"""F:(?P<likely_contamination_fragmented>\d+(?:\.\d+)?)%\],"""
        r"""U:(?P<unknown>\d+(?:\.\d+)?)%\s*$"""
    ),
}

if __name__ == "__main__":
    main()
