from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import classification_report, confusion_matrix
import ast


def read_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = [ast.literal_eval(line.strip()) for line in file]
    return data


# 提取标签和文本
def extract_labels_and_text(data):
    labels = [item[1] for item in data if item[3] != 'null']
    text_data = [item[3] for item in data if item[3] != 'null']
    return labels, text_data


# 训练模型
def train_and_evaluate_model(labels, text_data):
    # 划分
    X_train, X_test, y_train, y_test = train_test_split(text_data, labels, test_size=0.2, random_state=42)

    # TF-IDF
    vectorizer = TfidfVectorizer(max_features=5000)
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    # SGD
    clf = SGDClassifier(random_state=42)
    clf.fit(X_train_tfidf, y_train)
    y_pred = clf.predict(X_test_tfidf)

    # 评估
    print("Classification Report:")
    print(classification_report(y_test, y_pred))

    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))


def main():
    file_path = 'D:/DoAc/asdb/Gold/success.txt'  # Replace with the actual file path
    data = read_data(file_path)
    labels, text_data = extract_labels_and_text(data)
    train_and_evaluate_model(labels, text_data)


if __name__ == "__main__":
    main()
