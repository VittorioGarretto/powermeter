import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
import pandas as pd
import numpy as np

BATCH_SIZE = 16
EPOCHS = 2000


class Autoencoder(nn.Module):
    def __init__(self, input_dim):
        """
        Autoencoder that denoises the last features while keeping the first feature unchanged.

        Args:
            input_dim (int): Total number of input features
        """
        super(Autoencoder, self).__init__()
        # The code dimension has to be the same as the input one
        self.hidden_dim = input_dim - 1
        
        # Encoder
        self.encoder = nn.Sequential(
            nn.Linear(input_dim-1, 30),
            nn.ReLU(),
            nn.Linear(30, self.hidden_dim),
            nn.Tanh()
        )

        # Decoder
        self.decoder = nn.Sequential(
            nn.Linear(self.hidden_dim, 30),
            nn.ReLU(),
            nn.Linear(30, input_dim-1),
            nn.Tanh()
        )

    def forward(self, x):
        """
        Forward pass of the autoencoder.

        Args:
            x (Tensor): Input tensor of shape (batch_size, input_dim).

        Returns:
            Tuple[Tensor, Tensor]: 
                - The full reconstructed output (batch_size, input_dim).
                - The denoised version of the last features (batch_size, input_dim - 1).
        """
        first_feature = x[:, 0].unsqueeze(1)
        noisy_features = x[:, 1:]

        denoised_features = self.encoder(noisy_features)
        hidden = torch.cat((first_feature, denoised_features), dim=1)

        output = torch.cat((first_feature, self.decoder(denoised_features)), dim=1) 

        return output, hidden
    

class CustomLoss(nn.Module):
    def __init__(self, lambda_denoise=0.5, lambda_sum=1.0, lambda_recon=1.0):
        """
        Custom loss function for the autoencoder.
        
        Args:
            lambda_denoise (float): Weight for the denoising loss.
            lambda_sum (float): Weight for the sum constraint loss.
            lambda_recon (float): Weight for the reconstruction loss.
        """
        super(CustomLoss, self).__init__()
        self.lambda_denoise = lambda_denoise 
        self.lambda_sum = lambda_sum  
        self.lambda_recon = lambda_recon

    def forward(self, input, output, denoised_features):
        """
        Computes the loss function.

        Args:
            input (Tensor): Original input tensor (batch_size, num_features).
            output (Tensor): Reconstructed output tensor (batch_size, num_features).
            denoised_features (Tensor): The denoised version of the last features.

        Returns:
            Tensor: The total loss value.
        """

        # 1. Typical reconstruction loss
        reconstruction_loss = F.mse_loss(output, input)

        # 2. Encourage the denoised features to be close to the original noisy features
        denoising_loss = F.mse_loss(denoised_features, input[:, 1:])

        # 3. Enforce the sum of the last denoised features to be equal to the first feature
        sum_constraint_loss = torch.abs(denoised_features.sum(dim=1) - input[:, 0]).mean()

        # Combine the losses with their respective weights
        total_loss = (
            self.lambda_recon*reconstruction_loss
            + self.lambda_denoise*denoising_loss 
            + self.lambda_sum*sum_constraint_loss
        )

        return total_loss


if __name__ == '__main__':

    torch.set_float32_matmul_precision('high')

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Creating the torch dataset
    x_train_df = pd.read_csv('../3060ti/X_train_3060ti.csv')
    y_train_df = pd.read_csv('../3060ti/Y_train_3060ti.csv')

    y_train_df = y_train_df.iloc[0:800][['gpu_power']]
    x_train_df = x_train_df.drop(columns=['timestamp', 'ac_frequency', 'current', 'nvme_power', 
                                      'device_temperature', 'energy', 'linkquality', 'state', 'voltage', 'psu_eff'])
    x_train_df = x_train_df.iloc[0:800]
    
    
    x_train_df['gpu_power'] = y_train_df['gpu_power']
    # Rearrange the columns
    cols = list(x_train_df.columns)  
    cols.insert(1, cols.pop(-1))
    x_train_df = x_train_df[cols]

    # Normalize the data wrt the max value of the df (for the sum constraint 
    # is mandatory to normalize everything by the same amount)
    max_val = x_train_df.to_numpy().max()
    x_train_df /= max_val

    dataset = torch.tensor(x_train_df.values, dtype=torch.float32)
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

    # Now setup the model
    input_dim = x_train_df.shape[1]
    model = Autoencoder(input_dim).to(device)
    model = torch.compile(model)

    criterion = CustomLoss(lambda_denoise=1.0, lambda_sum=1.0, lambda_recon=1.0)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.00001)

    # Training 
    for epoch in range(EPOCHS):
        total_loss = 0

        for batch in dataloader:
            batch = batch.to(device)
            optimizer.zero_grad()

            # Forward pass
            output, hidden = model(batch)

            # Compute loss
            loss = criterion(batch, output, hidden[:, 1:])
            # Backward pass and optimization step
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        if epoch % 10 == 0:
            print(f"Epoch {epoch}, Loss: {total_loss / len(dataloader):.4f}")


    # Testing the model to see the results
    model.eval()
    input_data = torch.tensor(x_train_df.values, dtype=torch.float32).to(device)

    with torch.no_grad():
        output, hidden = model(input_data)

    x_denoised_df = pd.DataFrame(hidden.cpu().numpy(), columns=x_train_df.columns)
    x_recon_df = pd.DataFrame(output.cpu().numpy(), columns=x_train_df.columns)
    
    x_train_df["diff"] = x_train_df.iloc[:, 1:].sum(axis=1) - x_train_df.iloc[:, 0]
    x_denoised_df["diff"] = x_denoised_df.iloc[:, 1:].sum(axis=1) - x_denoised_df.iloc[:, 0]
    
    x_train_df *= max_val
    x_denoised_df *= max_val
    x_recon_df *= max_val

    print(x_train_df, '\n', x_denoised_df, '\n', x_recon_df, '\n')
    print(f"Err after denoise {x_denoised_df['diff'].mean()} with std {x_denoised_df['diff'].std()}\n")
    print(f"Err before {x_train_df['diff'].mean()} with std {x_train_df['diff'].std()}")