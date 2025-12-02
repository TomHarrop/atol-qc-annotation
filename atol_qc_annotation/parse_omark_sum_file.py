#!/usr/bin/env python3

"""
Inspired by / based on https://github.com/DessimozLab/OMArk/blob/main/utils/plot_all_results.py
"""

import re
import sys
import json

# Parsing config. Keys are the name of the item. Value is a tuple of type,
# regex string and index in result.
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


def single_line_search(line, single_line_regexes):
    for k, v in single_line_regexes.items():
        matched, value = parse_single_line(line, v[0], v[1], v[2])
        if matched:
            return (k, value)


def parse_single_line(line, type_to_return, regex_string, result_index):
    results = re.search(regex_string, line)
    if not results:
        return False, None
    val = results.group(result_index)
    if val is None or val == "":
        return True, None
    return True, type_to_return(val)


def results_line_search(line, type_to_return, regex):
    search_result = re.search(regex, line)
    if search_result:
        result_dict = {
            k: type_to_return(v) for k, v in search_result.groupdict().items()
        }
        return result_dict


def main():
    in_contaminant_line = False
    results_dict = {}
    detected_species = []

    lines = [x.rstrip() for x in sys.stdin.read().splitlines()]
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
            # skip blanks and the defline
            if line == "":
                continue

            if line.startswith("#"):
                splits = line.split("\t")
                headers = [
                    re.sub(r"\s+", "_", re.sub(r"[^A-Za-z\s]", "", s)).strip("_")
                    for s in splits
                ]
                continue

            contam_splits = line.strip().split("\t")
            if len(headers) == len(contam_splits):
                detected_species.append(dict(zip(headers, contam_splits)))
            else:
                raise ValueError("wtf")

    # add the contaminants ("detected species") to the results
    results_dict["detected_species"] = detected_species

    # write the output
    json.dump(results_dict, sys.stdout)

if __name__ == "__main__":
    main()
