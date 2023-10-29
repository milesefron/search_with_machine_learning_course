import argparse
import glob
import os
import xml.etree.ElementTree as ET
from pathlib import Path
import json

# Directory for product data
directory = r'/workspace/datasets/product_data/products/'

parser = argparse.ArgumentParser(description='Process some integers.')
general = parser.add_argument_group("general")
general.add_argument("--output", default="/workspace/datasets/fasttext/output.fasttext", help="the file to output to")


args = parser.parse_args()
output_file = args.output
path = Path(output_file)
output_dir = path.parent
if os.path.isdir(output_dir) == False:
        os.mkdir(output_dir)



cat_counts = {}

def _label_filename(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    for child in root:
        # Check to make sure category name is valid and not in music or movies
        if (child.find('name') is not None and child.find('name').text is not None and
            child.find('categoryPath') is not None and len(child.find('categoryPath')) > 0 and
            child.find('categoryPath')[len(child.find('categoryPath')) - 1][0].text is not None and
            child.find('categoryPath')[0][0].text == 'cat00000' and
            child.find('categoryPath')[1][0].text != 'abcat0600000'):
                # text
                cat = child.find('categoryPath')[len(child.find('categoryPath')) - 1][1].text.replace(' ', '_')

                # code
                #cat = child.find('categoryPath')[len(child.find('categoryPath')) - 1][0].text
                # Replace newline chars with spaces so fastText doesn't complain
                name = child.find('name').text.replace('\n', ' ')

                if cat in cat_counts:
                    cat_counts[cat] += 1
                else:
                    cat_counts[cat] = 1


if __name__ == '__main__':
    files = glob.glob(f'{directory}/*.xml')
    print("Writing results to %s" % output_file)
    all_labels = []
    i=1
    for file in files:
        print(str(i) + '/' + str(len(files)) + ': ' +  file)
        _label_filename(file)
        i+=1

    with open(output_file, 'w') as output:
        output.write(json.dumps(cat_counts))

    
