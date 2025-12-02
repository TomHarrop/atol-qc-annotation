#!/usr/bin/env python
"""
OMArk - Quality assesment of coding-gene repertoire annotation
(C) 2022 Yannis Nevers <yannis.nevers@unil.ch>
This file is part of OMArk.
OMArk is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
OMArk is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License
along with OMArk. If not, see <http://www.gnu.org/licenses/>.
"""


import pandas as pd
import re
import sys


def read_stdin():
    return sys.stdin.read().splitlines(True)


# Parse a summary file from OMArk and return a tuple representing the data. First element of the tuple is a Dictionnary containing all OMArk metrics about the proteome of interest.
# The second element is a list of dictionnary, with one entry per contaminant. The list is empty if there is no detected contaminant
def parse_sum(lines):
    in_cont = False
    detected_species = list()
    main_data = dict()
    for line in lines:
        if not in_cont:
            protein_nr_line = re.search(
                r"On the whole proteome, there \w+ ([0-9]+) proteins", line
            )
            if protein_nr_line:
                main_data["Protein_number"] = int(protein_nr_line.group(1))
            # S:Single:S, D:Duplicated[U:Unexpected,E:Expected],M:Missing
            # resultline =  re.search("F:([-0-9.]+)%,D:([-0-9.]+)%,O:([-0-9.]+)%,U:([-0-9.]+)%,L:([-0-9.]+)", line)
            resultline = re.search(
                r"S:([-0-9.]+)%,D:([-0-9.]+)%\[U:([-0-9.]+)%,E:([-0-9.]+)%\],M:([-0-9.]+)",
                line,
            )

            if resultline:
                results = resultline

                main_data["Complete"] = float(resultline.group(1)) + float(
                    resultline.group(2)
                )
                main_data["Single"] = float(resultline.group(1))
                main_data["Duplicated"] = float(resultline.group(2))
                main_data["Expected_Duplicated"] = float(resultline.group(3))
                main_data["Unexpected_Duplicated"] = float(resultline.group(4))
                main_data["Missing"] = float(resultline.group(5))

            # C:Placements in correct lineage [P:Partial hits, F:Fragmented], E: Erroneous placement [P:Partial hits, F:Fragmented], N: no mapping
            # conservline =  re.search("C:([-0-9.]+)%,L:([-0-9.]+)%,O:([-0-9.]+)%,U:([-0-9.]+)%", line)
            conservline = re.search(
                r"A:([-0-9.]+)%\[P:([-0-9.]+)%,F:([-0-9.]+)%\],I:([-0-9.]+)%\[P:([-0-9.]+)%,F:([-0-9.]+)%\],C:([-0-9.]+)%\[P:([-0-9.]+)%,F:([-0-9.]+)%\],U:([-0-9.]+)%",
                line,
            )
            if conservline:
                main_data["Consistent"] = float(conservline.group(1))
                main_data["Consistent_Partially_Mapping"] = float(conservline.group(2))
                main_data["Consistent_Fragments"] = float(conservline.group(3))
                main_data["Consistent_Structurally_Consistent"] = (
                    float(conservline.group(1))
                    - float(conservline.group(2))
                    - float(conservline.group(3))
                )
                main_data["Inconsistent"] = float(conservline.group(4))
                main_data["Inconsistent_Partially_Mapping"] = float(
                    conservline.group(5)
                )
                main_data["Inconsistent_Fragments"] = float(conservline.group(6))
                main_data["Inconsistent_Structurally_Consistent"] = (
                    float(conservline.group(4))
                    - float(conservline.group(5))
                    - float(conservline.group(6))
                )
                main_data["Contaminant"] = float(conservline.group(7))
                main_data["Contaminant_Partially_Mapping"] = float(conservline.group(8))
                main_data["Contaminant_Fragments"] = float(conservline.group(9))
                main_data["Contaminant_Structurally_Consistent"] = (
                    float(conservline.group(7))
                    - float(conservline.group(8))
                    - float(conservline.group(9))
                )
                main_data["Unknown"] = float(conservline.group(10))

            if line == "#From HOG placement, the detected species are:\n":
                in_cont = True
        else:
            if line[0] == "#" or line == "\n":
                continue
            detected_species.append(line.strip("\n").split("\t"))
    main_data["Contaminant"] = [x[0] for x in detected_species[1:]]
    main_data["Detected_Main_Species"] = detected_species[0][0]

    contaminant_data = list()
    if len(detected_species) > 1:
        for sup_detect_species in detected_species[1:]:
            contaminant_data.append(
                {
                    "Main_Taxon": detected_species[0][0],
                    "Contaminant": sup_detect_species[0],
                    "Contaminant_Taxid": sup_detect_species[1],
                    "Number_of_Proteins": sup_detect_species[2],
                }
            )
    return main_data, contaminant_data

if __name__ == "__main__":
    x = read_stdin()
    y = parse_sum(x)
    raise ValueError(y)
