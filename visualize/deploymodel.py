import torch
import torch.nn as nn


class RNN(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, num_classes):
        super(RNN, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        # Set initial hidden and cell states
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(device)

        # Forward propagate LSTM
        out, _ = self.lstm(x, (h0, c0))  # out: tensor of shape (batch_size, seq_length, hidden_size)

        # Decode the hidden state of the last time step
        out = self.fc(out[:, -1, :])
        return out

    def predict(self, instances):
        with torch.no_grad():
            inputs = torch.Tensor(instances).resize(1, instances.shape[0], instances.shape[1])  # warn("non-inplace resize is deprecated")
            outputs = model(inputs)
            _, predicted = torch.max(outputs.data, 1)  # outputs.data
        return predicted.item()


# hyperparameter
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
input_size = 8
hidden_size = 64
num_layers = 2
num_classes = 2
sequence_length = 20

model = RNN(input_size, hidden_size, num_layers, num_classes).to(device)
model.load_state_dict(torch.load('model.pt'))
model.eval()
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
