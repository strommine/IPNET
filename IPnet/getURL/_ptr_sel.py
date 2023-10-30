import json
from collections import Counter


def load_and_process_data(data_file):
    with open(data_file, 'r') as file:
        data = [json.loads(line.strip()) for line in file.readlines()]

    # 移除最后两个字段，并计算所有字段的出现次数
    all_ptr_splits = [split for item in data for split in list(item.values())[0].split('.')[:-2]]
    counter = Counter(all_ptr_splits)

    return data, counter


def process_ptr_record(item, counter):
    ptr_record = list(item.values())[0]
    ptr_split = [x for x in ptr_record.split('.')[:-1] if x]
    # 在当前ptr记录中，找出在整个语料库中出现次数最多的两个字段
    ptr_split_counts = [(split, counter[split]) for split in ptr_split]
    selected_ptr_splits = [split for split, _ in sorted(ptr_split_counts, key=lambda x: x[1], reverse=False)[:-2]]
    return list(item.keys())[0], ' '.join(selected_ptr_splits)
