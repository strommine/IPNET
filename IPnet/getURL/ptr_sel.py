import json


def load_and_process_data(data_file):
    with open(data_file, 'r') as file:
        data = [json.loads(line.strip()) for line in file.readlines()]
    return data


def process_ptr_record(item):
    ptr_record = list(item.values())[0]
    ptr_split = [x for x in ptr_record.split('.') if x]
    if ptr_split[-2] in ['com', 'net'] and len(ptr_split) >= 3:
        selected_ptr_splits = [ptr_split[-3], ptr_split[-2]]
    elif len(ptr_split) >= 2:
        selected_ptr_splits = [ptr_split[-2], ptr_split[-1]]
    else:
        selected_ptr_splits = [ptr_split[-1]] if len(ptr_split) >= 1 else []

    return list(item.keys())[0], ' '.join(selected_ptr_splits)
