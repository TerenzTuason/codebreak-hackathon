import json
import numpy as np
from pathlib import Path
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sentence_transformers import SentenceTransformer
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm import tqdm

class IntentDataset(Dataset):
    def __init__(self, embeddings, labels):
        self.embeddings = torch.FloatTensor(embeddings)
        self.labels = torch.LongTensor(labels)
        
    def __len__(self):
        return len(self.labels)
    
    def __getitem__(self, idx):
        return self.embeddings[idx], self.labels[idx]

class IntentClassifier(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes, dropout_rate=0.3):
        super(IntentClassifier, self).__init__()
        
        self.input_layer = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.LayerNorm(hidden_size),
            nn.Dropout(dropout_rate)
        )
        
        self.hidden_layer1 = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.LayerNorm(hidden_size // 2),
            nn.Dropout(dropout_rate)
        )
        
        self.hidden_layer2 = nn.Sequential(
            nn.Linear(hidden_size // 2, hidden_size // 4),
            nn.ReLU(),
            nn.LayerNorm(hidden_size // 4),
            nn.Dropout(dropout_rate)
        )
        
        self.output_layer = nn.Linear(hidden_size // 4, num_classes)
        
    def forward(self, x):
        x = self.input_layer(x)
        x = self.hidden_layer1(x)
        x = self.hidden_layer2(x)
        return self.output_layer(x)

class HealthcareSupportAI:
    def __init__(self):
        self.intent_labels = []
        self.sentence_encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {self.device}")
        
    def preprocess_data(self, data_path):
        """Load and preprocess the healthcare support dataset"""
        with open(data_path, 'r') as f:
            data = json.load(f)
            
        X = []  # Input sentences
        y = []  # Intent labels
        
        # Process queries section
        for query in data['queries']:
            intent = query['intent']
            if intent not in self.intent_labels:
                self.intent_labels.append(intent)
            
            # Add example queries
            for example in query['examples']:
                X.append(example)
                y.append(self.intent_labels.index(intent))
                
        # Convert text to embeddings using sentence transformer
        print("Converting text to embeddings...")
        X_embeddings = self.sentence_encoder.encode(X, show_progress_bar=True)
        
        return X_embeddings, y
    
    def evaluate_model(self, model, data_loader):
        """Evaluate model performance"""
        model.eval()
        all_preds = []
        all_labels = []
        total_loss = 0
        criterion = nn.CrossEntropyLoss()
        
        with torch.no_grad():
            for inputs, labels in data_loader:
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                total_loss += loss.item()
                
                _, predicted = outputs.max(1)
                all_preds.extend(predicted.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
        
        # Calculate metrics
        precision, recall, f1, _ = precision_recall_fscore_support(
            all_labels, all_preds, average='weighted'
        )
        
        return {
            'loss': total_loss / len(data_loader),
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'predictions': all_preds,
            'true_labels': all_labels
        }
    
    def plot_confusion_matrix(self, true_labels, predictions, save_path='models/confusion_matrix.png'):
        """Plot and save confusion matrix"""
        cm = confusion_matrix(true_labels, predictions)
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            cm, 
            annot=True, 
            fmt='d',
            xticklabels=self.intent_labels,
            yticklabels=self.intent_labels
        )
        plt.title('Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()
    
    def train(self, data_path, epochs=50, batch_size=8, learning_rate=0.001):
        """Train the model on the healthcare support dataset"""
        # Preprocess data
        X, y = self.preprocess_data(data_path)
        
        # Data augmentation: Add small random noise to embeddings
        X_aug = []
        y_aug = []
        for i in range(len(X)):
            # Original sample
            X_aug.append(X[i])
            y_aug.append(y[i])
            # Augmented samples with noise
            for _ in range(2):  # Create 2 noisy copies
                noise = np.random.normal(0, 0.01, X[i].shape)
                X_aug.append(X[i] + noise)
                y_aug.append(y[i])
        
        X = np.array(X_aug)
        y = np.array(y_aug)
        
        # Split into train and validation sets
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Create datasets and dataloaders
        train_dataset = IntentDataset(X_train, y_train)
        val_dataset = IntentDataset(X_val, y_val)
        
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size)
        
        # Initialize model
        input_size = X_train.shape[1]
        hidden_size = 512  # Increased hidden size
        num_classes = len(self.intent_labels)
        
        self.model = IntentClassifier(input_size, hidden_size, num_classes).to(self.device)
        
        # Define loss function and optimizer
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.AdamW(self.model.parameters(), lr=learning_rate, weight_decay=0.01)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode='min', factor=0.5, patience=5
        )
        
        # Training loop
        best_val_loss = float('inf')
        best_model_state = None
        current_lr = learning_rate
        
        for epoch in range(epochs):
            # Training phase
            self.model.train()
            train_loss = 0
            train_correct = 0
            train_total = 0
            
            progress_bar = tqdm(train_loader, desc=f'Epoch {epoch+1}/{epochs}')
            for inputs, labels in progress_bar:
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                
                optimizer.zero_grad()
                outputs = self.model(inputs)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item()
                _, predicted = outputs.max(1)
                train_total += labels.size(0)
                train_correct += predicted.eq(labels).sum().item()
                
                # Update progress bar
                progress_bar.set_postfix({
                    'loss': f'{train_loss/train_total:.3f}',
                    'acc': f'{100.*train_correct/train_total:.2f}%'
                })
            
            # Validation phase
            val_metrics = self.evaluate_model(self.model, val_loader)
            
            print(f'\nEpoch {epoch+1}/{epochs}:')
            print(f'Train Loss: {train_loss/len(train_loader):.3f} | '
                  f'Train Acc: {100.*train_correct/train_total:.2f}%')
            print(f'Val Loss: {val_metrics["loss"]:.3f} | '
                  f'Val Precision: {val_metrics["precision"]:.3f} | '
                  f'Val Recall: {val_metrics["recall"]:.3f} | '
                  f'Val F1: {val_metrics["f1"]:.3f}\n')
            
            # Learning rate scheduling
            old_lr = optimizer.param_groups[0]['lr']
            scheduler.step(val_metrics['loss'])
            new_lr = optimizer.param_groups[0]['lr']
            if new_lr != old_lr:
                print(f'Learning rate decreased from {old_lr:.6f} to {new_lr:.6f}')
            
            # Save best model
            if val_metrics['loss'] < best_val_loss:
                best_val_loss = val_metrics['loss']
                best_model_state = self.model.state_dict().copy()
                print("New best model saved!")
        
        # Load best model and create final evaluation
        self.model.load_state_dict(best_model_state)
        final_metrics = self.evaluate_model(self.model, val_loader)
        
        # Plot confusion matrix
        self.plot_confusion_matrix(
            final_metrics['true_labels'],
            final_metrics['predictions']
        )
        
        # Save the model and intent labels
        self.save_model()
        
        return final_metrics
    
    def save_model(self, model_dir='models'):
        """Save the trained model and intent labels"""
        Path(model_dir).mkdir(exist_ok=True)
        torch.save(self.model.state_dict(), f'{model_dir}/healthcare_support_model.pth')
        
        with open(f'{model_dir}/intent_labels.json', 'w') as f:
            json.dump(self.intent_labels, f)
    
    def load_model(self, model_dir='models'):
        """Load a trained model"""
        with open(f'{model_dir}/intent_labels.json', 'r') as f:
            self.intent_labels = json.load(f)
            
        input_size = 384  # Size of sentence embeddings
        hidden_size = 512  # Match the training hidden size
        num_classes = len(self.intent_labels)
        
        self.model = IntentClassifier(input_size, hidden_size, num_classes).to(self.device)
        self.model.load_state_dict(torch.load(f'{model_dir}/healthcare_support_model.pth'))
        self.model.eval()
    
    def predict(self, text):
        """Predict intent for given text"""
        if not self.model:
            raise ValueError("Model not trained yet!")
            
        # Convert text to embedding
        embedding = self.sentence_encoder.encode([text])
        
        # Convert to tensor and move to device
        embedding_tensor = torch.FloatTensor(embedding).to(self.device)
        
        # Get prediction
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(embedding_tensor)
            probabilities = torch.softmax(outputs, dim=1)
            confidence, predicted = probabilities.max(1)
        
        return {
            'intent': self.intent_labels[predicted.item()],
            'confidence': confidence.item()
        }

if __name__ == '__main__':
    # Initialize and train the model
    ai = HealthcareSupportAI()
    metrics = ai.train('datasets/healthcare_support_data.json')
    
    print("\nFinal Model Performance:")
    print(f"Precision: {metrics['precision']:.3f}")
    print(f"Recall: {metrics['recall']:.3f}")
    print(f"F1 Score: {metrics['f1']:.3f}") 