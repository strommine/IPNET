import ast
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from transformers import BertTokenizer, BertForSequenceClassification, AdamW
import torch


# 读取文件中的数据
def load_data(filepath):
    texts = []
    labels = []

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = ast.literal_eval(line.strip())
                if len(data) >= 5:
                    texts.append(data[3])
                    labels.append(data[4])
            except SyntaxError as e:
                print(f"Skipping line due to SyntaxError: {e}")
                continue

    return texts, labels


def classify_with_tfidf_sgd(directory):
    # 1. 加载数据
    texts, labels = load_data(directory)

    # 2. 数据预处理
    # 将数据划分为训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)

    # 3. 特征提取
    tfidf_vectorizer = TfidfVectorizer(max_features=5000)  # 限制特征数量
    X_train_transformed = tfidf_vectorizer.fit_transform(X_train)
    X_test_transformed = tfidf_vectorizer.transform(X_test)

    # 4. 模型训练
    sgd_classifier = SGDClassifier()
    sgd_classifier.fit(X_train_transformed, y_train)

    # 5. 模型评估
    y_pred = sgd_classifier.predict(X_test_transformed)
    # print(y_test)
    # print(y_pred)
    print(classification_report(y_test, y_pred, zero_division=0))

    return sgd_classifier, tfidf_vectorizer


def classify_with_bert(directory):
    # 1. 加载数据
    texts, labels = load_data(directory)

    num_labels = len(set(labels))  # 获取类别的数量

    # 2. 数据预处理
    # 使用BERT的tokenizer
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    max_length = 512  # BERT的最大序列长度
    X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)

    train_encodings = tokenizer(X_train, truncation=True, padding='max_length', max_length=max_length,
                                return_tensors="pt")
    test_encodings = tokenizer(X_test, truncation=True, padding='max_length', max_length=max_length,
                               return_tensors="pt")

    # 创建PyTorch数据集和数据加载器
    class Dataset(torch.utils.data.Dataset):
        def __init__(self, encodings, labels):
            self.encodings = encodings
            self.labels = labels

        def __getitem__(self, idx):
            item = {key: val[idx] for key, val in self.encodings.items()}
            item['labels'] = torch.tensor(self.labels[idx])
            return item

        def __len__(self):
            return len(self.labels)

    train_dataset = Dataset(train_encodings, y_train)
    test_dataset = Dataset(test_encodings, y_test)

    # 3. 初始化BERT模型
    model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=num_labels)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # 4. 训练BERT模型
    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=4, shuffle=True)
    optimizer = AdamW(model.parameters(), lr=5e-5)

    model.train()
    for epoch in range(3):  # 运行3个epoch
        for batch in train_loader:
            optimizer.zero_grad()
            inputs = {key: val.to(device) for key, val in batch.items()}
            outputs = model(**inputs)
            loss = outputs.loss
            loss.backward()
            optimizer.step()

    # 5. 模型评估
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=4)
    model.eval()
    preds, true_labels = [], []
    with torch.no_grad():
        for batch in test_loader:
            inputs = {key: val.to(device) for key, val in batch.items()}
            outputs = model(**inputs)
            _, pred = torch.max(outputs.logits, dim=1)
            preds.extend(pred.cpu().tolist())
            true_labels.extend(batch['labels'].cpu().tolist())

    print(classification_report(true_labels, preds))

    return model, tokenizer


def main():
    directory = "D:/DoAc/trainset/trainset.txt"  # 按照你描述的路径
    classifier, vectorizer = classify_with_tfidf_sgd(directory)

    # 使用BERT
    # directory = "D:/DoAc/html/ctext/"
    # bert_classifier, bert_tokenizer = classify_with_bert(directory)


if __name__ == "__main__":
    main()
