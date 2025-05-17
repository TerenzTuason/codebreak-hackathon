import torch
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    EarlyStoppingCallback,
    IntervalStrategy
)
from .data_processor import load_and_process_data
from config.model_config import ModelConfig
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import os
import shutil
import logging

logger = logging.getLogger(__name__)

def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='weighted')
    acc = accuracy_score(labels, preds)
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }

def clean_output_dir(output_dir):
    """Clean up the output directory if it exists"""
    if os.path.exists(output_dir):
        try:
            shutil.rmtree(output_dir)
            logger.info(f"Cleaned up existing output directory: {output_dir}")
        except Exception as e:
            logger.warning(f"Could not clean output directory: {str(e)}")

def save_model_safely(trainer, model, tokenizer, output_dir):
    """Safely save the model and tokenizer"""
    try:
        # Create a temporary directory for saving
        temp_dir = output_dir + "_temp"
        clean_output_dir(temp_dir)
        os.makedirs(temp_dir, exist_ok=True)

        # Save to temporary directory
        trainer.save_model(temp_dir)
        tokenizer.save_pretrained(temp_dir)

        # Clean up the final directory
        clean_output_dir(output_dir)

        # Move from temporary to final directory
        shutil.move(temp_dir, output_dir)
        logger.info(f"Model saved successfully to {output_dir}")
    except Exception as e:
        logger.error(f"Error saving model: {str(e)}")
        raise

def train_model():
    # Initialize config
    config = ModelConfig()
    
    # Load and process data
    train_dataset, eval_dataset, test_dataset, tokenizer = load_and_process_data(config)
    
    # Initialize model
    model = AutoModelForSequenceClassification.from_pretrained(
        config.model_name,
        num_labels=config.num_labels,
        hidden_dropout_prob=config.hidden_dropout_prob
    )
    
    # Create temporary output directory for training
    temp_output_dir = config.model_output_dir + "_training"
    clean_output_dir(temp_output_dir)
    
    # Define training arguments
    training_args = TrainingArguments(
        output_dir=temp_output_dir,
        num_train_epochs=config.num_epochs,
        per_device_train_batch_size=config.batch_size,
        per_device_eval_batch_size=config.batch_size,
        warmup_steps=config.warmup_steps,
        weight_decay=config.weight_decay,
        logging_dir='./logs',
        logging_steps=100,
        eval_steps=500,
        save_steps=500,
        save_total_limit=2,
        save_strategy=IntervalStrategy.STEPS,
        eval_strategy=IntervalStrategy.STEPS,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        report_to="none",  # Disable wandb reporting
        save_safetensors=False  # Disable safetensors to avoid file locking issues
    )
    
    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
    )
    
    try:
        # Train model
        trainer.train()
        
        # Evaluate on test set
        test_results = trainer.evaluate(test_dataset)
        logger.info("\nTest Results:", test_results)
        
        # Save model and tokenizer
        save_model_safely(trainer, model, tokenizer, config.model_output_dir)
        
        return trainer, model, tokenizer
    
    finally:
        # Cleanup temporary directory
        clean_output_dir(temp_output_dir)

if __name__ == "__main__":
    train_model() 