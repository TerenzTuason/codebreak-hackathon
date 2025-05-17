import json
import pandas as pd
from typing import List, Dict, Tuple
from datasets import Dataset
from transformers import AutoTokenizer
from sklearn.model_selection import train_test_split
import numpy as np

class HealthcareDataset:
    def __init__(self, config):
        self.config = config
        self.tokenizer = AutoTokenizer.from_pretrained(config.model_name)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
    def generate_conversation_pairs(self, data: Dict) -> List[Dict]:
        """Generate conversation pairs from the hospital data."""
        conversations = []
        
        # Process each query intent
        for query in data['queries']:
            intent = query['intent']
            examples = query['examples']
            response_template = query['response_template']
            
            # Generate conversations based on intent
            if intent == 'department_services':
                for dept in data['data_sources']['departments']:
                    for example in examples:
                        if dept['name'].lower() in example.lower():
                            response = response_template.format(
                                department=dept['name'],
                                services=', '.join(dept['services'])
                            )
                            conversations.append({
                                'input_text': example,
                                'target_text': response,
                                'intent': intent,
                                'requires_escalation': False
                            })
            
            elif intent == 'doctor_availability':
                for doctor in data['data_sources']['doctors']:
                    for example in examples:
                        if doctor['name'].lower() in example.lower():
                            response = response_template.format(
                                doctor=doctor['name'],
                                availability=', '.join(doctor['availability']),
                                time=doctor['time'],
                                room=doctor['room']
                            )
                            conversations.append({
                                'input_text': example,
                                'target_text': response,
                                'intent': intent,
                                'requires_escalation': False
                            })
            
            elif intent == 'insurance_coverage':
                for insurance in data['data_sources']['insurance_partners']:
                    for example in examples:
                        if insurance['name'].lower() in example.lower():
                            response = response_template.format(
                                insurance_provider=insurance['name'],
                                services_covered=', '.join(insurance['services_covered']),
                                contact=insurance['contact']
                            )
                            conversations.append({
                                'input_text': example,
                                'target_text': response,
                                'intent': intent,
                                'requires_escalation': False
                            })
            
            elif intent == 'appointment_management':
                for appt in data['data_sources']['appointments']:
                    for example in examples:
                        response = response_template.format(
                            doctor=appt['doctor'],
                            date=appt['date'],
                            reason=appt['reason']
                        )
                        conversations.append({
                            'input_text': example,
                            'target_text': response,
                            'intent': intent,
                            'requires_escalation': False
                        })
            
            elif intent == 'lab_results':
                for result in data['data_sources']['lab_results']:
                    for example in examples:
                        if result['test_name'].lower() in example.lower():
                            response = response_template.format(
                                test_name=result['test_name'],
                                result=result['result'],
                                range=result.get('range', 'Not specified'),
                                date=result['date'],
                                doctor=result['doctor']
                            )
                            conversations.append({
                                'input_text': example,
                                'target_text': response,
                                'intent': intent,
                                'requires_escalation': False
                            })
            
            elif intent == 'policy_inquiry':
                for policy_type, policy_text in data['data_sources']['policies'].items():
                    for example in examples:
                        if policy_type.split('_')[0] in example.lower():
                            response = response_template.format(
                                policy_description=policy_text
                            )
                            conversations.append({
                                'input_text': example,
                                'target_text': response,
                                'intent': intent,
                                'requires_escalation': False
                            })
            
            else:  # For medication_refill and test_preparation intents
                for example in examples:
                    response = response_template
                    conversations.append({
                        'input_text': example,
                        'target_text': response,
                        'intent': intent,
                        'requires_escalation': False
                    })
        
        return conversations
    
    def prepare_conversation_data(self, data: Dict) -> Dataset:
        """Convert hospital data into model-ready format."""
        conversations = self.generate_conversation_pairs(data)
        df = pd.DataFrame(conversations)
        return Dataset.from_pandas(df)
    
    def tokenize_data(self, dataset: Dataset) -> Dataset:
        """Tokenize the dataset for model training."""
        def tokenize_function(examples):
            inputs = self.tokenizer(
                examples['input_text'],
                padding='max_length',
                truncation=True,
                max_length=self.config.max_length,
                return_tensors='pt'
            )
            
            targets = self.tokenizer(
                examples['target_text'],
                padding='max_length',
                truncation=True,
                max_length=self.config.max_length,
                return_tensors='pt'
            )
            
            return {
                'input_ids': inputs['input_ids'],
                'attention_mask': inputs['attention_mask'],
                'labels': targets['input_ids'],
                'intent': examples['intent'],
                'requires_escalation': examples['requires_escalation']
            }
        
        tokenized = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=dataset.column_names
        )
        
        return tokenized
    
    def load_and_prepare_data(self, data_path: str) -> Tuple[Dataset, Dataset, Dataset]:
        """Load, prepare and split the dataset."""
        # Load raw data
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Prepare conversation data
        dataset = self.prepare_conversation_data(data)
        
        # Convert to numpy arrays for splitting
        dataset_dict = dataset.to_dict()
        n_samples = len(dataset)
        indices = np.arange(n_samples)
        
        # Split indices
        train_val_idx, test_idx = train_test_split(indices, test_size=0.1, random_state=42)
        train_idx, val_idx = train_test_split(train_val_idx, test_size=0.1, random_state=42)
        
        # Create datasets using indices
        train_dataset = Dataset.from_dict({
            k: [v[i] for i in train_idx] for k, v in dataset_dict.items()
        })
        val_dataset = Dataset.from_dict({
            k: [v[i] for i in val_idx] for k, v in dataset_dict.items()
        })
        test_dataset = Dataset.from_dict({
            k: [v[i] for i in test_idx] for k, v in dataset_dict.items()
        })
        
        # Tokenize datasets
        train_dataset = self.tokenize_data(train_dataset)
        val_dataset = self.tokenize_data(val_dataset)
        test_dataset = self.tokenize_data(test_dataset)
        
        return train_dataset, val_dataset, test_dataset 