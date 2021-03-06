# %%
import os, re
import pandas as pd

if os.getcwd() != "/home/tunasteak/box/projects/dirt":
    os.chdir("/home/tunasteak/box/projects/dirt")


samples = [
    "CO-08-A",
    "CO-12-A",
    "CO-14-A",
    "DL-13-A",
    "DL-17-A",
    "DW-05-A",
    "DW-10-A",
    "DW-16-A",
    "NI-19-A",
    "NI-49-A",
    "NI-69-A",
    "NL-03-A",
    # "NL-07-A",
    "NL-11-A",
    "NR-01-A",
    "NR-04-A",
    # "NR-06-A",
]

# %%
def parse_spades(file_name):
    """
    This function reads in assembly mapping results from the JGI spades pipeline. Specifically, it pulls out "reads used" and "reads map" information.

    Args:
        file_name (string): Name of the sample

    Returns:
        dict: A dict of mapped values, keys are column names, values are float
    """
    spades_map = []
    file_path = "data/mapping_data/README.txt"
    with open(file_path, "rt") as open_file:
        file_lines = open_file.readlines()
        pattern = re.compile("The number of reads used as input to aligner is:")
        line_num = 0
        for line in file_lines:
            line_num += 1
            line = line.strip()
            if pattern.search(line) != None:
                temp = [i.strip() for i in line.split(r":")][1]
                spades_map.append(float(temp))
                break
        temp = file_lines[line_num].strip().split(r" ")[-2:]
        temp[1] = temp[1][1:-2]
        spades_map.extend([float(i) for i in temp])
    test = []
    file_path = "data/mapping_data/_reads_removed.txt"
    with open(file_path, "rt") as open_file:
        file_lines = open_file.readlines()
        pattern = re.compile("Short Read Discards:")
        line_num = 0
        for line in file_lines:
            line_num += 1
            line = line.strip()
            if pattern.search(line) != None:
                temp = [i.strip() for i in line.split("\t")][1]
                temp2 = temp.split(r" ")[::2]
                temp2[1] = temp2[1][1:-2]
                spades_map.extend([float(i) for i in temp2])
                break
        temp = [i.strip() for i in file_lines[line_num].split("\t")][1]
        temp2 = temp.split(r" ")[::2]
        temp2[1] = temp2[1][1:-2]
        spades_map.extend([float(i) for i in temp2])
    keys = [
        "spades_total_reads",
        "spades_reads_map",
        "spades_percent_reads_map",
        "spades_reads_removed_1kbp",
        "spades_reads_removed_percent_1kbp",
        "spades_reads_kept_1kbp",
        "spades_reads_kept_percent_1kbp",
    ]
    return dict(zip(keys, spades_map))

# %%

def parse_megahit(file_name):
    """
    This function reads in assembly mapping results from my megahit  pipeline. Specifically, it pulls out "reads used" and "reads map" information.

    Args:
        file_name (string): Name of the sample

    Returns:
        dict: A dict of mapped values, keys are column names, values are float
    """
    megahit_map = []
    file_path = "data/mapping_data/" + file_name + "_megahit_output.txt"
    with open(file_path, "rt") as open_file:
        file_lines = open_file.readlines()
        pattern = re.compile("Reads Used:")
        for line in file_lines:
            line = line.strip()
            if pattern.search(line) != None:
                temp = [i.strip() for i in line.split("\t")][1]
                megahit_map.append(float(temp))

        pattern = re.compile("mapped:")
        for line in file_lines:
            line = line.strip()
            if pattern.search(line) != None:
                temp = [i.strip() for i in line.split("\t")][1:3]
                temp[0] = temp[0][:-1]
                megahit_map.extend([float(i) for i in temp])
    keys = [
        "mega_total_reads",
        "mega_percent_read1_map",
        "mega_read1_map",
        "mega_precent_read2_map",
        "mega_read2_map",
    ]
    return dict(zip(keys, megahit_map))


def parse_spades_1kbp(file_name):
    """
    This function reads in assembly mapping results pruned metaspades contigs of >1kbp. Specifically, it pulls out "reads used" and "reads map" information.

    Args:
        file_name (string): Name of the sample

    Returns:
        dict: A dict of mapped values, keys are column names, values are float
    """
    spades_map = []
    file_path = "data/mapping_data/" + file_name + "_metaspades_output.txt"
    with open(file_path, "rt") as open_file:
        file_lines = open_file.readlines()
        pattern = re.compile("Reads Used:")
        for line in file_lines:
            line = line.strip()
            if pattern.search(line) != None:
                temp = [i.strip() for i in line.split("\t")][1]
                spades_map.append(float(temp))

        pattern = re.compile("mapped:")
        for line in file_lines:
            line = line.strip()
            if pattern.search(line) != None:
                temp = [i.strip() for i in line.split("\t")][1:3]
                temp[0] = temp[0][:-1]
                spades_map.extend([float(i) for i in temp])
    keys = [
        "spades_1kpb_total_reads",
        "spades_1kpb_percent_read1_map",
        "spades_1kpb_read1_map",
        "spades_1kpb_precent_read2_map",
        "spades_1kpb_read2_map",
    ]
    return dict(zip(keys, spades_map))


def mapped_compare(sample_id):
    """
    This function reads in both JGI and megahit pipline and complies them together into one object.

    Args:
        sample_id (string): sample name used to find identify which files to read in

    Returns:
        dict: A dictionary with both spades and megahit mapping information.
    """
    spades_map = parse_spades(sample_id)
    spades_1kbp_map = parse_spades_1kbp(sample_id)
    megahit_map = parse_megahit(sample_id)
    return {**spades_map, **spades_1kbp_map, **megahit_map}


# %%

## Calls mapping compare and creates a nested dict through dict comprehension. It then pass the nested dict to pandas which parses the outer dict as rows and the inner as columns using the orient = "index" option
mapped_df = pd.DataFrame.from_dict(
    {key: mapped_compare(key) for key in samples}, orient="index"
)

mapped_df.to_csv(
    "mapped/mapped_values_compare.csv", index=True, index_label="sample_id"
)
