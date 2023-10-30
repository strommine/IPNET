#训练集数据清洗

import re
import ast
import nltk

# 确保NLTK数据已下载
# nltk.download('words')

from nltk.corpus import words

# 创建一个单词集合以进行更快的查找
english_word_set = set(words.words())


def filter_english_words(input_file_path, output_file_path):
    with open(input_file_path, 'r', encoding='utf-8') as infile, \
            open(output_file_path, 'w', encoding='utf-8') as outfile:

        for line in infile:
            try:
                line_list = ast.literal_eval(line.strip())
                if len(line_list) < 4:
                    raise IndexError
            except (ValueError, SyntaxError, IndexError):
                print(f"Skipping invalid line: {line.strip()}")
                continue

            text = line_list[3]

            # 仅保留至少两个字母的英文单词
            four_words = re.findall(r'\b[a-zA-Z]{4,}\b', text)
            four_words = [word for word in four_words if all(ord(char) < 128 for char in word)]

            # 过滤：只保留在英文单词列表中的单词
            english_words = [word for word in four_words if word.lower() in english_word_set]

            valid_english_words = []
            consecutive_four_letter_word_count = 0

            for word in english_words:
                if len(word) == 4:
                    consecutive_four_letter_word_count += 1
                else:
                    consecutive_four_letter_word_count = 0

                # 过滤掉连续四个及以上的四个字母单词
                if consecutive_four_letter_word_count < 4:
                    valid_english_words.append(word)

            filtered_text = ' '.join(valid_english_words)
            line_list[3] = filtered_text
            outfile.write(str(line_list) + "\n")


# 使用函数
input_file_path = 'D:/DoAc/trainset/g-final-set-100.txt'
output_file_path = 'D:/DoAc/trainset/g-final-set-100-modified-plus.txt'
filter_english_words(input_file_path, output_file_path)
