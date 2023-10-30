output_file_path = 'D:/DoAc/trainset/g-final-set-100-modified-plus.txt'
a = 0
with open(output_file_path, encoding='utf-8') as f:
    for i in f:
        a+=1
        if a%700 == 0:
            print(a)
            print(i)
print(a)