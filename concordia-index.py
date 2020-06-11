from concordia_blocks import create_blocks
print("Creating Blocks")

# Replace with path to the files to scrape
file_path = "spiderfolder\\spiderfolder\\spiders\\files"
create_blocks(file_path)

print("Merging blocks")
import concordia_merge_blocks

print("Queries")
from concordia_query import query_index
query_index()
