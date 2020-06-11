from pathlib import Path
import codecs
from bs4 import BeautifulSoup
import re
from nltk.corpus import stopwords
import collections
from operator import itemgetter
from nltk.stem import PorterStemmer

ps = PorterStemmer()


def compress(word):
    # Remove any punctuation in the words
    pattern = re.compile('[\W_]+')
    word = pattern.sub('', word)

    # Remove numbers and lowercase
    word = re.sub('[0-9]', '', word)
    word = word.lower()
    word = ps.stem(word)
    return word


# Take the block that is docID => [entire text]
def parse_block(block_to_parse):
    doc_ids = block_to_parse.keys()
    new_dic = {}

    for doc_id in doc_ids:
        block_data = block_to_parse.get(doc_id)
        words = block_data.split()
        for word in words:
            word = compress(word)

            if word != '':
                if word in new_dic:
                    # if int(doc_id) not in new_dic[word]:
                    new_dic[word].append(int(doc_id))
                else:
                    new_dic[word] = [int(doc_id)]

    new_dic = {k: v for k, v in new_dic.items() if not k.isdigit()}

    # Remove stopwords
    stop_words = list(stopwords.words('english'))
    stopw_150 = stop_words[0:150]
    temp_dict = new_dic.copy()

    for term in temp_dict:
        if term in stopw_150:
            new_dic.pop(term)

    for term in new_dic:
        counter = collections.Counter(new_dic[term])
        new_dic[term] = sorted(counter.most_common(), key=itemgetter(0))

    return new_dic


def create_blocks(path_string):
    file_path = Path(path_string)
    disk_path = Path("DISK")
    if not disk_path.exists():
        disk_path.mkdir()

    doc_id = 1
    count = 0
    block_num = 1

    block = {}
    doc_id_pair_dic = {}
    doc_lengths = []

    for filename in file_path.glob('*'):
        opened_file = open(filename, mode='r', encoding='utf8')
        file_contents = opened_file.read()
        opened_file.close()

        doc_id_pair_dic[doc_id] = str(filename).split("\\")[4:]

        soup = BeautifulSoup(file_contents, "html.parser")
        divs = soup.find(class_="content-main")
        if not divs:
            divs = soup.find(id="content-main")
        print(f"{type(divs)}, name {filename} and id {doc_id}")

        if divs is not None:
            tags = ['p', 'li', 'h1', 'h2', 'h3']
            content = ""
            for tag in tags:
                content += '\n' + '\n'.join([el.text for el in divs.find_all(tag)])

            block[doc_id] = content
            doc_lengths.insert(doc_id, len(content.split()) - 1)
            doc_id += 1
            count += 1

            if count == 1000:
                block = parse_block(block)

                if block_num < 10:
                    f = codecs.open(f'DISK\\Block0{block_num}.txt', encoding='utf-8', mode='w')
                else:
                    f = codecs.open(f'DISK\\Block{block_num}.txt', encoding='utf-8', mode='w')

                # Sort and write to the file
                for key in sorted(block.keys()):
                    block_data = block.get(key)
                    f.write(f"{key}:{block_data}" + "\n")
                f.close()

                print(f"Block{block_num} is finished with size {len(block)}")
                count = 0
                block_num += 1
                block = {}

    # Write the remainder
    block = parse_block(block)
    if block_num < 10:
        f = codecs.open(f'DISK\\Block0{block_num}.txt', encoding='utf-8', mode='w')
    else:
        f = codecs.open(f'DISK\\Block{block_num}.txt', encoding='utf-8', mode='w')

    # Sort and write to the file
    for key in sorted(block.keys()):
        block_data = block.get(key)
        f.write(f"{key}:{block_data}" + "\n")
    f.close()

    print(f"Block{block_num} is finished with size {len(block)}")

    with open('document_lengths.txt', 'w') as f:  # Write document lengths to a file
        for doc in doc_lengths:
            f.write(f"{doc}\n")

    with open('doc_id_pairs.txt', 'w') as f:  # Write document lengths to a file
        for key in sorted(doc_id_pair_dic.keys()):
            block_data = doc_id_pair_dic.get(key)
            f.write(f"{key}:{block_data[0]}" + "\n")


# files = "spiderfolder\\spiderfolder\\spiders\\files"
# create_blocks(files)
