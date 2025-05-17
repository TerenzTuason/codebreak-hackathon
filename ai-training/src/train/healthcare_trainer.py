import os
import torch
import wandb
from transformers import (
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
    default_data_collator
)
from typing import Dict, List
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

class HealthcareTrainer:
    def __init__(self, config):
        self.config = config
        self.model = AutoModelForSequenceClassification.from_pretrained(
            config.model_name,
            num_labels=len(config.intent_labels)
        )
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        
    def compute_metrics(self, eval_pred):
        """Compute metrics for evaluation."""
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        
        precision, recall, f1, _ = precision_recall_fscore_support(
            labels,
            predictions,
            average='weighted'
        )
        
        accuracy = accuracy_score(labels, predictions)
        
        return {
            'accuracy': accuracy,
            'f1': f1,
            'precision': precision,
            'recall': recall
        }
    
    def train(self, train_dataset, eval_dataset, output_dir: str):
        """Train the model."""
        if self.config.enable_logging:
            wandb.init(
                project=self.config.wandb_project,
                config=self.config.__dict__
            )
        
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=self.config.num_epochs,
            per_device_train_batch_size=self.config.batch_size,
            per_device_eval_batch_size=self.config.batch_size,
            warmup_steps=self.config.warmup_steps,
            learning_rate=self.config.learning_rate,
            weight_decay=self.config.weight_decay,
            logging_dir=os.path.join(output_dir, 'logs'),
            logging_steps=100,
            eval_steps=500,
            save_steps=500,
            save_total_limit=2,
            load_best_model_at_end=True,
            metric_for_best_model="f1",
            report_to=["wandb"] if self.config.enable_logging else [],
            remove_unused_columns=True,
            dataloader_drop_last=False,
            dataloader_num_workers=0
        )
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=default_data_collator,
            compute_metrics=self.compute_metrics
        )
        
        trainer.train()
        
        trainer.save_model(output_dir)
        
        if self.config.enable_logging:
            wandb.finish()
        
        return trainer
    
    def evaluate(self, trainer, test_dataset) -> Dict:
        """Evaluate the model on test dataset."""
        results = trainer.evaluate(test_dataset)
        return results 