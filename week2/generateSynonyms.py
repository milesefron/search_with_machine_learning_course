import fasttext
import re

SCORE_THRESHOLD = 0.8

model = fasttext.load_model('/workspace/datasets/fasttext/models/title_model.bin')


input_file = '/workspace/datasets/fasttext/top_words.txt'
f = open(input_file, 'r')
words = f.readlines()
f.close()

for word in words:
    word = word.rstrip()
    predictions = model.get_nearest_neighbors(word, 20)
    out_line = word + ','
    for (score, term) in predictions:
        if score > SCORE_THRESHOLD:
            out_line += term + ','
    out_line = re.sub(',$', '', out_line)
    if(',' in out_line):
        print(out_line)