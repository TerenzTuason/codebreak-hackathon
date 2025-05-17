import json
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer
from typing import List, Dict, Any
import pandas as pd
from sklearn.model_selection import train_test_split
import logging

logger = logging.getLogger(__name__)

class HealthcareSupportDataset(Dataset):
    def __init__(self, conversations: List[Dict[str, Any]], tokenizer, config, max_length: int = 512):
        self.conversations = conversations
        self.tokenizer = tokenizer
        self.config = config
        self.max_length = max_length

    def __len__(self):
        return len(self.conversations)

    def __getitem__(self, idx):
        conversation = self.conversations[idx]
        
        # Combine messages into a single text
        messages = conversation['messages']
        text = ""
        for msg in messages:
            role_prefix = "User: " if msg['role'] == 'user' else "Assistant: "
            text += role_prefix + msg['content'] + " [SEP] "
        
        # Tokenize the text
        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        # Get intent label
        intent_label = self.config.intent_labels.index(messages[-1]['intent'])
        
        return {
            'input_ids': encoding['input_ids'].squeeze(),
            'attention_mask': encoding['attention_mask'].squeeze(),
            'labels': torch.tensor(intent_label, dtype=torch.long)
        }

def load_and_process_data(config):
    # Load data
    with open(config.train_data_path, 'r') as f:
        data = json.load(f)
    
    # Log dataset size
    logger.info(f"Loaded {len(data)} conversations from dataset")
    
    # For small datasets, use a larger portion for training
    if len(data) < 10:
        logger.warning("Small dataset detected. Adjusting split ratios.")
        train_size = 0.8
        eval_size = 0.1
        test_size = 0.1
    else:
        train_size = config.train_split
        eval_size = config.eval_split
        test_size = config.test_split
    
    # Create multiple instances of each conversation for training
    augmented_data = []
    for conv in data:
        # Add original conversation
        augmented_data.append(conv)
        # Add conversation with only the last message (for inference)
        last_message = {
            "conversation_id": f"{conv['conversation_id']}_last",
            "tier": conv['tier'],
            "scenario": conv['scenario'],
            "messages": [conv['messages'][-1]],
            "metadata": conv['metadata']
        }
        augmented_data.append(last_message)
    
    logger.info(f"Augmented dataset size: {len(augmented_data)} conversations")
    
    # Split data
    train_data, temp_data = train_test_split(
        augmented_data,
        test_size=(1 - train_size),
        random_state=42
    )
    
    if len(temp_data) > 1:
        eval_data, test_data = train_test_split(
            temp_data,
            test_size=test_size/(eval_size + test_size),
            random_state=42
        )
    else:
        # If we have very little data, use the same data for eval and test
        logger.warning("Very small dataset. Using same data for evaluation and testing.")
        eval_data = temp_data
        test_data = temp_data
    
    # Initialize tokenizer
    tokenizer = AutoTokenizer.from_pretrained(config.model_name)
    
    # Create datasets
    train_dataset = HealthcareSupportDataset(train_data, tokenizer, config)
    eval_dataset = HealthcareSupportDataset(eval_data, tokenizer, config)
    test_dataset = HealthcareSupportDataset(test_data, tokenizer, config)
    
    logger.info(f"Dataset splits - Train: {len(train_data)}, Eval: {len(eval_data)}, Test: {len(test_data)}")
    
    return train_dataset, eval_dataset, test_dataset, tokenizer 