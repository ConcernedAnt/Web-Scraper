import json
import linecache
import ast
from pathlib import Path

disk_path = Path("DISK")
num_blocks = len(list(disk_path.glob('Block*.txt')))
list_to_sort = [-1] * num_blocks
final_block = {}
pos_in_block = [1] * num_blocks
last_merged_item = "-1"

num_merged_blocks = 0
block_num = 0


# Gets the path of the block entered
def get_path(block_needed):
    if block_needed < 9:
        block_path = "DISK\\Block0{}.txt"
    else:
        block_path = "DISK\\Block{}.txt"
    block_path = block_path.format(block_needed + 1)
    return block_path


# Takes a string and converts it into a term, postings pair
def convert_txt_to_dict(line_to_convert):
    split = line_to_convert.split(':')
    term = split[0]
    postings = ast.literal_eval(split[1])  # convert a string list to a list
    return term, postings


# Finds the minimum value in the list of minimums from the different blocks
def index_of_min(list_of_mins):
    min_in_list = None
    none_count = 0
    for value in list_of_mins:
        if value is not None:
            if not min_in_list:
                min_in_list = value
            elif value < min_in_list:
                min_in_list = value
        else:
            none_count += 1

    if none_count < len(list_of_mins):
        return list_of_mins.index(min_in_list)
    else:
        return -1


def merge_min(min_index):
    min_path = get_path(min_index)

    block_pos = pos_in_block[min_index]  # Get the item at the current position in the block
    line = linecache.getline(min_path, block_pos)
    if line == "":  # Linecache returns "" when it doesn't encounter any text
        last_merged = ""
    else:
        (key, value) = convert_txt_to_dict(line)

        # Write key, value to the dictionary
        if key not in final_block:
            final_block[key] = value
        else:
            temp_list = final_block.get(key)
            temp_list.extend(value)

        # Increment the position in the block whose min was merged
        pos_in_block[min_index] += 1
        line = linecache.getline(min_path, block_pos + 1)

        # Write a new value to the list of mins if there are still items in the file
        if line == "":
            last_merged = ""
        else:
            last_merged = key
            (key, value) = convert_txt_to_dict(line)
            list_to_sort[min_index] = key
    return last_merged


#  ================================ MAIN ===========================================
# Populate the list of minimums
for index in range(0, num_blocks):
    path = get_path(index)

    first_line = linecache.getline(path, 1)
    (key1, value1) = convert_txt_to_dict(first_line)
    list_to_sort[index] = key1

# Loop while all of the blocks aren't empty
while index_of_min(list_to_sort) != -1:
    index_to_merge = index_of_min(list_to_sort)
    print(index_to_merge)
    last_merged_item = merge_min(index_to_merge)

    if last_merged_item == "":
        list_to_sort[index_to_merge] = None  # Tells the program that the block is empty

    # write the block to the file and create a new one.
    if index_of_min(list_to_sort) == -1:
        # Make sure there are no terms in the blocks that should be in the file before merging
        for index in range(0, len(list_to_sort)):
            while list_to_sort[index] in final_block:
                last_merged_item = merge_min(index)

                if last_merged_item == "":
                    list_to_sort[index] = None  # Tells the program that the block is empty

        with open(f"DISK\\merged_blocks{num_merged_blocks}.json", "w") as write_file:
            json.dump(final_block, write_file)
        num_merged_blocks += 1
        final_block = {}
