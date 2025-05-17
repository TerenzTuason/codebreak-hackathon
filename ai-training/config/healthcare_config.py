from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class HealthcareConfig:
    # Model Configuration
    model_name: str = "microsoft/DialoGPT-medium"  # Base model to fine-tune
    max_length: int = 512
    num_train_epochs: int = 3
    batch_size: int = 8
    learning_rate: float = 2e-5
    warmup_steps: int = 500
    
    # Task-specific Configuration
    tier0_max_turns: int = 3  # Maximum conversation turns before escalation
    confidence_threshold: float = 0.85  # Minimum confidence for Tier 0 responses
    
    # Supported Tasks
    supported_tasks: List[str] = field(default_factory=lambda: [
        "appointment_scheduling",
        "report_interpretation",
        "medication_inquiry",
        "general_health_info"
    ])
    
    # Escalation Rules
    escalation_triggers: List[str] = field(default_factory=lambda: [
        "emergency",
        "urgent",
        "critical",
        "immediate attention",
        "severe pain",
        "system error"
    ])
    
    # Response Templates
    greeting_template: str = "Hello! I'm your healthcare assistant. How can I help you today?"
    escalation_template: str = "I'll connect you with a specialist who can better assist you with this matter."
    
    # Logging Configuration
    enable_logging: bool = True
    log_dir: str = "logs/healthcare"
    wandb_project: str = "healthcare-support-bot"
    
    # API Configuration
    api_version: str = "v1"
    api_prefix: str = "/api/v1/healthcare"
    max_request_size: int = 10 * 1024 * 1024  # 10MB 