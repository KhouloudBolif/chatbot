
#pip install torch torchvision torchaudio
#pip install torch-geometric


import torch
import torch.nn as nn
import torch.nn.functional as F

class GCN(nn.Module):
    def __init__(self, in_features, hidden_features, out_features):
        super(GCN, self).__init__()
        # Définition des couches du modèle GCN
        self.conv1 = nn.Conv1d(in_features, hidden_features, kernel_size=3, padding=1)  # Exemple
        self.conv2 = nn.Conv1d(hidden_features, out_features, kernel_size=3, padding=1)  # Exemple

    def forward(self, x):
        # Passer les données dans le modèle
        x = F.relu(self.conv1(x))
        x = self.conv2(x)
        return x
