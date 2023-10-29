import argparse
import multiprocessing
import glob
from tqdm import tqdm
import os
import xml.etree.ElementTree as ET
from pathlib import Path
import json
import re

f = open('/workspace/datasets/fasttext/products_cat_freqs.json', 'r')
cat_counts = json.load(f)
f.close()

def transform_name(product_name):
    #product_name = re.sub('\W+', ' ', product_name).replace('  ', ' ').strip()
    #product_name = product_name + ' ' + product_name.strip()
    return product_name

# Directory for product data
directory = r'/workspace/datasets/product_data/products/'

parser = argparse.ArgumentParser(description='Process some integers.')
general = parser.add_argument_group("general")
general.add_argument("--input", default=directory,  help="The directory containing product data")
general.add_argument("--output", default="/workspace/datasets/fasttext/output.fasttext", help="the file to output to")
general.add_argument("--label", default="id", help="id is default and needed for downsteam use, but name is helpful for debugging")

# IMPLEMENT: Setting min_products removes infrequent categories and makes the classifier's task easier.
general.add_argument("--min_products", default=0, type=int, help="The minimum number of products per category (default is 0).")

args = parser.parse_args()
output_file = args.output
path = Path(output_file)
output_dir = path.parent
if os.path.isdir(output_dir) == False:
        os.mkdir(output_dir)

if args.input:
    directory = args.input
# IMPLEMENT: Track the number of items in each category and only output if above the min
min_products = args.min_products
names_as_labels = False
if args.label == 'name':
    names_as_labels = True

def _label_filename(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    labels = []
    for child in root:
        # Check to make sure category name is valid and not in music or movies
        if (child.find('name') is not None and child.find('name').text is not None and
            child.find('categoryPath') is not None and len(child.find('categoryPath')) > 0 and
            child.find('categoryPath')[len(child.find('categoryPath')) - 1][0].text is not None and
            child.find('categoryPath')[0][0].text == 'cat00000' and
            child.find('categoryPath')[1][0].text != 'abcat0600000'):

                i = 0
                while len(child.find('categoryPath')) - i >= 0:
                    i += 1
                    # Choose last element in categoryPath as the leaf categoryId or name
                    if names_as_labels:
                        cat = child.find('categoryPath')[len(child.find('categoryPath')) - i][1].text.replace(' ', '_')
                    else:
                        cat = child.find('categoryPath')[len(child.find('categoryPath')) - i][0].text
                    # Replace newline chars with spaces so fastText doesn't complain

                    if cat in cat_counts and cat_counts[cat] > min_products+1:
                        name = child.find('name').text.replace('\n', ' ')
                        labels.append((cat, transform_name(name)))
                        
                        if i > 1:
                            print(f'{str(i)}: {cat}, {filename} :: {name}')
                        break
          
    return labels

if __name__ == '__main__':
    files = glob.glob(f'{directory}/*.xml')
    print("Writing results to %s" % output_file)
    with multiprocessing.Pool() as p:
        all_labels = tqdm(p.imap(_label_filename, files), total=len(files))
        with open(output_file, 'w') as output:
            for label_list in all_labels:
                for (cat, name) in label_list:
                    output.write(f'__label__{cat} {name}\n')
