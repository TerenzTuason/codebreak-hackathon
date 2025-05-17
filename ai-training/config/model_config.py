from dataclasses import dataclass

@dataclass
class ModelConfig:
    # Model parameters
    model_name: str = "roberta-base"
    max_length: int = 512
    batch_size: int = 16
    learning_rate: float = 5e-5
    num_epochs: int = 5
    warmup_steps: int = 1000
    weight_decay: float = 0.01
    
    # Training parameters
    train_split: float = 0.8
    eval_split: float = 0.1
    test_split: float = 0.1
    
    # Task-specific parameters
    hidden_dropout_prob: float = 0.2
    
    # Paths
    train_data_path: str = "data/train.json"
    eval_data_path: str = "data/eval.json"
    model_output_dir: str = "models/healthcare-support-bot"
    
    # Logging configuration
    enable_logging: bool = False
    wandb_project: str = "healthcare-support-bot"
    
    # Intent classes
    intent_labels: list = None
    
    def __post_init__(self):
        if self.intent_labels is None:
            self.intent_labels = [
                "schedule_appointment",
                "interpret_report",
                "general_inquiry",
                "escalate_to_human",
                "other"
            ] 