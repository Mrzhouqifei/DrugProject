import pandas as pd
import numpy as np
from sentiment_classify.moiveRnn import Model
from sentiment_classify.wordProcess import *

import torch.nn as nn
from torch.autograd import Variable
from torch import optim
import torch
import os
import pickle
device = 'cuda' if torch.cuda.is_available() else 'cpu'

precessed_data = pd.read_excel('../data/zhendong.xlsx')

# 词云
import warnings
warnings.filterwarnings("ignore")
import jieba   # 分词包
import pandas as pd

stopwords = pd.read_csv("../data/stopwords.txt"
                  ,index_col=False
                  ,quoting=3
                  ,sep="\t"
                  ,names=['stopword']
                  ,encoding='utf-8') # quoting=3 全不引用
stopwords = list(stopwords['stopword'])

def preprocess_text(line):
    # 转换所以大写字符为小写
    line=line.lower().strip()
    res = False
    try:
        segs=jieba.lcut(line)
        segs = filter(lambda x:x not in stopwords, segs)
        res = " ".join(segs)
    except:
        print(line)
    return res

vocabLimit = 50000
max_sequence_len = 500
obj1 = wordIndex()
embedding_dim = 50
hidden_dim = 100

print('reading the lines')
for comment in precessed_data.content:
    comment = str(comment)
    comment = preprocess_text(comment).strip()
    if comment != False:
        obj1.add_text(comment)
print('read all the lines')
print(len(obj1.word_to_idx))
limitDict(vocabLimit, obj1)

model = Model(embedding_dim, hidden_dim, vocabLimit).to(device)

loss_function = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=1e-3)
best_acc = 0
checkpoint = torch.load('../data/movie.pth')
model.load_state_dict(checkpoint['net'])
best_acc = checkpoint['acc']
print('best_acc: %.2f' % best_acc)

NUM_EPOCHS=2
total_length = len(precessed_data)
range_index = np.arange(total_length)
np.random.shuffle(range_index)

for i in range(NUM_EPOCHS):
    sum_loss = 0.0
    right = 0
    num = 0
    for idx in range_index:
        num += 1
        comment = str(precessed_data.iloc[idx,2])
        comment = preprocess_text(comment).strip()
        input_data = [obj1.word_to_idx[word] for word in comment.split(' ')]
        if len(input_data) > max_sequence_len:
            input_data = input_data[0:max_sequence_len]
        input_data = Variable(torch.LongTensor(input_data)).to(device)

        target = int(precessed_data.iloc[idx,1])
        target_data = Variable(torch.LongTensor([target])).to(device)

        if i%2==1:
            y_pred, embeddings = model(input_data)
            model.zero_grad()
            loss = loss_function(y_pred, target_data)
            sum_loss += loss.data.item()
            loss.backward()
            optimizer.step()
        else:
            y_pred, embeddings = model(input_data)
            _, predicted = y_pred.max(1)
#             print(predicted)
            right += predicted.eq(target).sum().item()
    if i%2!=1:
        acc = right / total_length
        if acc >= best_acc:
            best_acc = acc
            print('save checkpoint!')
            state = {
                'net': model.state_dict(),
                'acc': acc,
            }
            if not os.path.isdir('checkpoint'):
                os.mkdir('checkpoint')
            torch.save(state, '../data/movie.pth')

    print('train_loss %d epochs is %g' % ((i + 1), (sum_loss / 20000)))
    print('test acc:', acc)
    print('-'*30)

with open('../data/dict.pkl', 'wb') as f:
    pickle.dump(obj1.word_to_idx, f)