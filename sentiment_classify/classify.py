from sentiment_classify.moiveRnn import Model
import pickle
import torch
from torch.autograd import Variable
device = 'cuda' if torch.cuda.is_available() else 'cpu'
import warnings
import pandas as pd
import jieba
warnings.filterwarnings("ignore")

def predict(comments):
    stopwords = pd.read_csv("data/stopwords.txt"
                            , index_col=False
                            , quoting=3
                            , sep="\t"
                            , names=['stopword']
                            , encoding='utf-8')  # quoting=3 全不引用
    stopwords = list(stopwords['stopword'])

    def preprocess_text(line):
        # 转换所以大写字符为小写
        line = line.lower().strip()
        res = False
        try:
            segs = jieba.lcut(line)
            segs = filter(lambda x: x not in stopwords, segs)
            res = " ".join(segs)
        except:
            print(line)
        return res

    vocabLimit = 50000
    max_sequence_len = 500
    embedding_dim = 50
    hidden_dim = 100

    with open('data/dict.pkl','rb') as f :
        word_dict = pickle.load(f)

    model = Model(embedding_dim, hidden_dim, vocabLimit).to(device)

    checkpoint = torch.load('data/movie.pth')
    model.load_state_dict(checkpoint['net'])
    best_acc = checkpoint['acc']
    print('best_acc: %.2f' % best_acc)

    res = []
    for comment in comments:
        comment = preprocess_text(comment)
        input_data = [word_dict[word] for word in comment.split(' ')]
        if len(input_data) > max_sequence_len:
            input_data = input_data[0:max_sequence_len]
        input_data = Variable(torch.LongTensor(input_data)).to(device)

        y_pred, embeddings = model(input_data)
        _, predicted = y_pred.max(1)
        res.append(predicted.item())
    return res

