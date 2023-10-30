import ast
from gensim.models import KeyedVectors
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from sklearn.model_selection import RandomizedSearchCV
from sklearn.linear_model import SGDClassifier
from nltk.stem import PorterStemmer
import re
from transformers import BertTokenizer, BertForSequenceClassification, AdamW
import torch
import numpy as np
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.model_selection import train_test_split
from transformers import get_linear_schedule_with_warmup


# 读取文件内容
def read_file(filepath):
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                lst = ast.literal_eval(line.strip())
                if len(lst) >= 4:
                    label, text = lst[2], lst[3]
                    # 清洗和处理标签
                    label = label.replace(" ", "_").replace(",", "_").replace("&", "_")
                    if len(text.split()) >= 20:
                        data.append((text, label))
            except SyntaxError as e:
                print(f"Skipping line due to SyntaxError: {e}")
                continue
    return data


def preprocess_text(text):
    # 清洗文本
    text = re.sub(r'http\S+', '', text)  # 移除URL
    text = re.sub(r'<.*?>', '', text)    # 移除HTML标签
    text = re.sub(r'[^\w\s]', '', text)  # 移除标点符号
    text = re.sub(r'\d+', '', text)      # 移除数字
    text = text.lower()                  # 转换为小写

    # 词干提取
    stemmer = PorterStemmer()
    text = ' '.join([stemmer.stem(word) for word in text.split() if word not in ENGLISH_STOP_WORDS])

    return text


# 使用TF-IDF和随机森林进行分类
def classify_with_rf(data):
    texts, labels = zip(*data)

    # 划分数据集
    X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)

    # 特征提取
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    X_train_tf = vectorizer.fit_transform(X_train)
    X_test_tf = vectorizer.transform(X_test)

    # 参数分布
    param_dist = {
        'n_estimators': [50, 100, 200, 300],
        'max_depth': [5, 10, 20, 30, None],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4],
        'bootstrap': [True, False]
    }

    # 随机森林分类器
    rf = RandomForestClassifier(random_state=42)

    # 随机搜索交叉验证
    rf_random = RandomizedSearchCV(estimator=rf, param_distributions=param_dist,
                                   n_iter=100, cv=3, verbose=2, random_state=42, n_jobs=-1)
    rf_random.fit(X_train_tf, y_train)

    print("Best parameters found: ", rf_random.best_params_)

    # 使用最佳参数进行预测
    best_rf = rf_random.best_estimator_
    y_pred = best_rf.predict(X_test_tf)
    print("Random Forest Classification Report:")
    print(classification_report(y_test, y_pred))


# 使用LSTM进行分类
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.layers import Bidirectional, Dropout
from tensorflow.keras.callbacks import EarlyStopping


def classify_with_lstm(data):
    texts, labels = zip(*data)

    # Tokenization and padding
    tokenizer = Tokenizer(num_words=5000, oov_token='<OOV>')
    tokenizer.fit_on_texts(texts)
    sequences = tokenizer.texts_to_sequences(texts)
    padded = pad_sequences(sequences, maxlen=100, truncating='post', padding='post')

    # Label encoding
    label_encoder = LabelEncoder()
    encoded_labels = label_encoder.fit_transform(labels)
    num_labels = len(set(encoded_labels))

    X_train, X_test, y_train, y_test = train_test_split(padded, encoded_labels, test_size=0.2, random_state=42)

    model = Sequential([
        Embedding(5000, 64, input_length=100),
        Bidirectional(LSTM(64, return_sequences=True)),
        Dropout(0.5),
        LSTM(64),
        Dense(64, activation='relu'),
        Dropout(0.5),
        Dense(num_labels, activation='softmax')  # Use num_labels instead of hardcoding the number
    ])

    model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    early_stopping = EarlyStopping(monitor='val_loss', patience=3)

    model.fit(X_train, y_train, epochs=10, validation_data=(X_test, y_test), callbacks=[early_stopping])

    loss, accuracy = model.evaluate(X_test, y_test)
    print(f"LSTM Model Accuracy: {accuracy}")


def classify_with_tfidf_sgd(data):
    # 1. 加载数据
    texts, labels = zip(*data)

    # 2. 数据预处理
    # 将数据划分为训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=1234)

    # 3. 特征提取
    tfidf_vectorizer = TfidfVectorizer(max_features=5000)  # 限制特征数量
    X_train_transformed = tfidf_vectorizer.fit_transform(X_train)
    X_test_transformed = tfidf_vectorizer.transform(X_test)

    # 4. 定义超参数分布
    param_dist = {
        'alpha': [1e-4, 1e-3, 1e-2, 1e-1, 1e0, 1e1],
        'loss': ['hinge', 'log', 'modified_huber', 'squared_hinge', 'perceptron'],
        'penalty': ['l2', 'l1', 'elasticnet'],
        'max_iter': [5, 10, 20, 50, 80, 100, 200, 500, 1000],
        'tol': [None, 1e-3, 1e-4, 1e-5]
    }

    # 5. 初始化分类器和随机搜索
    sgd_classifier = SGDClassifier()
    sgd_random_search = RandomizedSearchCV(estimator=sgd_classifier, param_distributions=param_dist,
                                           n_iter=50, cv=5, verbose=2, random_state=42, n_jobs=-1)
    sgd_random_search.fit(X_train_transformed, y_train)

    # 打印最佳参数
    print("Best parameters found: ", sgd_random_search.best_params_)

    # 6. 使用最佳参数进行预测
    best_sgd = sgd_random_search.best_estimator_
    y_pred = best_sgd.predict(X_test_transformed)

    print(classification_report(y_test, y_pred, zero_division=0))

    return best_sgd, tfidf_vectorizer


def classify_with_bert(directory):
    # 1. 加载数据
    texts, labels = zip(*data)

    # 为标签进行编码
    label_encoder = LabelEncoder()
    encoded_labels = label_encoder.fit_transform(labels)

    num_labels = len(set(encoded_labels))  # 获取类别的数量

    # 2. 数据预处理
    # 使用BERT的tokenizer
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    max_length = 512  # BERT的最大序列长度
    X_train, X_test, y_train, y_test = train_test_split(texts, encoded_labels, test_size=0.2, random_state=42)

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
            item['labels'] = self.labels[idx]
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
    optimizer = AdamW(model.parameters(), lr=2e-5)  # Using 2e-5 as learning rate

    # Add learning rate scheduler
    epochs = 3
    total_steps = len(train_loader) * epochs
    scheduler = get_linear_schedule_with_warmup(optimizer,
                                                num_warmup_steps=0,  # Default value in run_glue.py
                                                num_training_steps=total_steps)

    model.train()
    for epoch in range(epochs):
        total_loss = 0
        for batch in train_loader:
            optimizer.zero_grad()
            inputs = {key: val.to(device) for key, val in batch.items()}
            outputs = model(**inputs)
            loss = outputs.loss
            total_loss += loss.item()
            loss.backward()

            # Gradient accumulation can be added here if needed

            optimizer.step()
            scheduler.step()  # Update learning rate

        # Average loss
        avg_train_loss = total_loss / len(train_loader)

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

    return model, tokenizer, label_encoder


def use_pretrained_embeddings(tokenizer, path_to_word2vec_model):
    # 加载预训练的Word2Vec模型
    word2vec_model = KeyedVectors.load_word2vec_format(path_to_word2vec_model, binary=True)

    # 创建嵌入矩阵
    vocabulary_size = len(tokenizer.word_index) + 1
    embedding_dim = 300

    embedding_matrix = np.zeros((vocabulary_size, embedding_dim))

    for word, i in tokenizer.word_index.items():
        if word in word2vec_model:
            embedding_matrix[i] = word2vec_model[word]

    return embedding_matrix, embedding_dim


# 使用LSTM进行分类
def classify_with_lstm_2(data, path_to_word2vec_model):
    texts, labels = zip(*data)
    tokenizer = Tokenizer(num_words=5000, oov_token='<OOV>')
    tokenizer.fit_on_texts(texts)
    sequences = tokenizer.texts_to_sequences(texts)
    padded = pad_sequences(sequences, maxlen=100, truncating='post', padding='post')

    label_tokenizer = Tokenizer(split=None)
    label_tokenizer.fit_on_texts(labels)

    label_seq = label_tokenizer.texts_to_sequences(labels)
    label_seq = np.array([item[0] for item in label_seq])

    X_train, X_test, y_train, y_test = train_test_split(padded, label_seq, test_size=0.2, random_state=42)

    num_labels = len(label_tokenizer.word_index) + 1

    # Load the Word2Vec model
    word2vec_model = KeyedVectors.load_word2vec_format(path_to_word2vec_model, binary=True)

    # Create an embedding matrix
    embedding_dim = word2vec_model.vector_size
    embedding_matrix = np.zeros((len(tokenizer.word_index) + 1, embedding_dim))
    for word, i in tokenizer.word_index.items():
        if word in word2vec_model:
            embedding_matrix[i] = word2vec_model[word]

    model = Sequential([
        Embedding(input_dim=len(tokenizer.word_index) + 1, output_dim=embedding_dim,
                  input_length=100, weights=[embedding_matrix], trainable=False),
        LSTM(64),
        Dense(64, activation='relu'),
        Dense(num_labels, activation='softmax')
    ])

    model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    # Define callbacks
    early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=2, min_lr=0.001)

    # Train the model with early stopping and dynamic learning rate adjustment
    model.fit(X_train, y_train, epochs=100,  # Set epochs to a large number
              validation_data=(X_test, y_test),
              callbacks=[early_stopping, reduce_lr])

    # Evaluate
    loss, accuracy = model.evaluate(X_test, y_test)
    print(f"LSTM Model Accuracy: {accuracy}")


if __name__ == "__main__":
    filepath = "D:/DoAc/trainset/g-final-set-100-modified-plus.txt"
    data = [(preprocess_text(text), label) for text, label in read_file(filepath)]

    _, labels = zip(*data)
    unique_labels = set(labels)
    print("Number of unique labels:", len(unique_labels))

    # 使用随机森林分类
    classify_with_rf(data)

    # 使用LSTM进行分类
    # classify_with_lstm(data)

    # 使用LSTM2进行分类
    # path_to_word2vec_model = 'D:/DoAc/GoogleNews-vectors-negative300.bin.gz'
    # classify_with_lstm_2(data, path_to_word2vec_model)

    # 使用SGD进行分类
    # classify_with_tfidf_sgd(data)

    # classify_with_bert(data)
