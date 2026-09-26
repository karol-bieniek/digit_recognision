import torch
from torch import nn

INPUT_IMG_SIZE = (28, 28)


class NeuralNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        # Convolutional layers analyze the image in 2D
        self.features = nn.Sequential(
            # 1 input channel (grayscale), 8 filters, 4x4 kernel, padding 1
            nn.Conv2d(1, 8, kernel_size=4, padding=1),  # Output: 8x27x27
            nn.ReLU(),
            nn.MaxPool2d(2, 2),  # Reduces: 27x27 -> 13x13 (using floor)
            nn.Conv2d(8, 16, kernel_size=4, padding=1),  # Output: 16x12x12
            nn.ReLU(),
            nn.MaxPool2d(2, 2),  # Reduces: 12x12 -> 6x6
            nn.Conv2d(16, 32, kernel_size=4, padding=1),  # Output: 32x5x5
            nn.ReLU(),
            nn.MaxPool2d(2, 2),  # Reduces: 5x5 -> 2x2 ( floor( (5+0-2)/2 + 1 ) = 2 )
        )

        # Calculated flattened size: 32 channels * 2 * 2 pixels = 128

        # Final linear classifier
        self.classifier = nn.Sequential(
            nn.Flatten(),  # Flatten: (32, 2, 2) -> (128,)
            nn.Linear(128, 128),  # Corrected: nn.Linear(32*2*2, 128)
            nn.ReLU(),
            nn.Linear(128, 10),
        )

    def forward(self, x):
        # x input shape: (Batch, 1, 28, 28)
        x = self.features(x)
        logits = self.classifier(x)
        return logits


device = (
    torch.accelerator.current_accelerator().type
    if torch.accelerator.is_available()
    else "cpu"
)


def train(dataloader, model, loss_fn, optimizer):
    size = len(dataloader.dataset)
    model.train()
    for batch, (X, y) in enumerate(dataloader):
        X, y = X.to(device), y.to(device)

        # Compute prediction error
        pred = model(X)
        loss = loss_fn(pred, y)

        # Backpropagation
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

        if batch % 100 == 0:
            loss, current = loss.item(), (batch + 1) * len(X)
            print(f"loss: {loss:>7f}  [{current:>5d}/{size:>5d}]")


def test(dataloader, model, loss_fn):
    size = len(dataloader.dataset)
    num_batches = len(dataloader)
    model.eval()
    test_loss, correct = 0, 0
    with torch.no_grad():
        for X, y in dataloader:
            X, y = X.to(device), y.to(device)
            pred = model(X)
            test_loss += loss_fn(pred, y).item()
            correct += (pred.argmax(1) == y).type(torch.float).sum().item()
    test_loss /= num_batches
    correct /= size
    print(
        f"Test Error: \n Accuracy: {(100 * correct):>0.1f}%, Avg loss: {test_loss:>8f} \n"
    )
