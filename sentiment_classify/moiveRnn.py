import torch
import torch.nn as nn
from torch.autograd import Variable
device = 'cuda' if torch.cuda.is_available() else 'cpu'

class Model(torch.nn.Module):
    def __init__(self, embedding_dim, hidden_dim, vocabLimit):
        super(Model, self).__init__()
        self.hidden_dim = hidden_dim
        self.embeddings = nn.Embedding(vocabLimit + 1, embedding_dim)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, bidirectional=True)
        self.linearOut = nn.Linear(hidden_dim*2, 2)

    def forward(self, inputs, after_embedding=False):
        hidden = self.init_hidden()
        if not after_embedding:
            embeddings = self.embeddings(inputs).view(len(inputs), 1, -1)
            var_embeddings = embeddings
            # var_embeddings = Variable(embeddings, requires_grad=True)
        else:
            var_embeddings = inputs
        lstm_out, (hn, cn) = self.lstm(var_embeddings, hidden)
        x = hn.view(1, -1)
        # x = lstm_out[-1]
        x = self.linearOut(x)
        return x, var_embeddings

    def init_hidden(self):
        return (Variable(torch.zeros(2, 1, self.hidden_dim)).to(device),
                Variable(torch.zeros(2, 1, self.hidden_dim)).to(device))

