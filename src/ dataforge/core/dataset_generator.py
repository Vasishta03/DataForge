import os
import json
import logging
import time
import random
import string
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Callable

from dataforge.handlers.kaggle_handler import KaggleDatasetHandler
from dataforge.handlers.mistral_handler import MistralHandler

class DatasetGenerator:
    """Core class for generating synthetic datasets."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize handlers
        self.kaggle_handler = KaggleDatasetHandler(config.get('kaggle', {}))
        self.mistral_handler = MistralHandler(config.get('mistral', {}))
        
        self.progress_callback = None
        self.status_callback = None
        self.should_stop = False
        
        # Setup paths
        self.base_path = Path(__file__).resolve().parent.parent.parent
        self.reference_path = self.base_path / self.config.get('paths', {}).get('reference_datasets', 'data/reference_datasets')
        self.generated_path = self.base_path / self.config.get('paths', {}).get('generated_datasets', 'data/generated_datasets')
        
        # Create directories if needed
        self.reference_path.mkdir(parents=True, exist_ok=True)
        self.generated_path.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("DatasetGenerator initialized successfully")
    
    def set_progress_callback(self, callback: Callable[[float, str], None]) -> None:
        self.progress_callback = callback
    
    def set_status_callback(self, callback: Callable[[str], None]) -> None:
        self.status_callback = callback
    
    def _update_progress(self, value: float, message: str) -> None:
        if self.progress_callback:
            self.progress_callback(value, message)
    
    def _update_status(self, message: str) -> None:
        if self.status_callback:
            self.status_callback(message)
    
    def generate_datasets(self, keyword: str, num_rows: int = 500, num_variations: int = 6) -> Dict[str, Any]:
        """Main method to generate synthetic datasets."""
        start_time = time.time()
        results = {
            'keyword': keyword,
            'reference_dataset': None,
            'generated_files': [],
            'total_time': None
        }
        
        try:
            # Step 1: Search and download Kaggle dataset
            self._update_status(f"Searching Kaggle for '{keyword}' datasets")
            self._update_progress(0.1, "Searching Kaggle")
            
            dataset_metadata = self.kaggle_handler.search_datasets(keyword)
            if not dataset_metadata:
                raise ValueError(f"No datasets found for keyword: {keyword}")
                
            # Download the best dataset
            self._update_status(f"Downloading dataset: {dataset_metadata[0]['title']}")
            self._update_progress(0.2, "Downloading dataset")
            
            dataset_file = self.kaggle_handler.download_dataset(
                dataset_metadata[0],
                self.reference_path
            )
            results['reference_dataset'] = str(dataset_file)
            
            # Step 2: Extract schema
            self._update_status("Analyzing dataset schema")
            self._update_progress(0.3, "Extracting schema")
            
            schema = self._extract_schema(dataset_file)
            self.logger.info(f"Extracted schema with {len(schema['columns'])} columns")
            
            # Step 3: Generate variations
            output_dir = self.generated_path / keyword
            output_dir.mkdir(exist_ok=True)
            
            for i in range(num_variations):
                if self.should_stop:
                    self._update_status("Generation stopped by user")
                    return results
                    
                self._update_status(f"Generating variation {i+1}/{num_variations}")
                progress_val = 0.4 + (i / num_variations) * 0.6
                self._update_progress(progress_val, f"Generating dataset {i+1}")
                
                # Create modified schema
                modified_schema = self._modify_schema(schema)
                
                # Generate synthetic data
                csv_data = self._generate_synthetic_data(modified_schema, num_rows)
                
                # Validate CSV format
                if not self._validate_csv(csv_data):
                    self.logger.warning("Generated CSV validation failed. Using fallback")
                    csv_data = self._generate_fallback_data(modified_schema, num_rows)
                
                # Save to file
                filename = f"{keyword}_data_{i+1}.csv"
                output_file = output_dir / filename
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(csv_data)
                
                results['generated_files'].append(str(output_file))
                self.logger.info(f"Saved dataset: {output_file}")
            
            self._update_status("Generation completed successfully")
            self._update_progress(1.0, "Generation complete")
            
        except Exception as e:
            self.logger.error(f"Generation failed: {e}", exc_info=True)
            self._update_status(f"Error: {str(e)}")
            raise
        
        finally:
            results['total_time'] = time.time() - start_time
            self.logger.info(f"Generation completed in {results['total_time']:.1f} seconds")
            return results
    
    def _extract_schema(self, dataset_path: Path) -> Dict[str, Any]:
        """Extract schema from a CSV file."""
        try:
            # Read first 100 rows for schema analysis
            df = pd.read_csv(dataset_path, nrows=100)
            
            schema = {
                'columns': [],
                'sample_data': {}
            }
            
            for col in df.columns:
                # Handle mixed data types
                sample_value = df[col].iloc[0]
                if pd.isna(sample_value):
                    sample_value = ""
                
                col_info = {
                    'name': col,
                    'dtype': str(df[col].dtype),
                    'sample_value': str(sample_value)
                }
                schema['columns'].append(col_info)
                schema['sample_data'][col] = col_info['sample_value']
            
            return schema
        
        except Exception as e:
            self.logger.error(f"Schema extraction failed: {e}", exc_info=True)
            raise
    
    def _modify_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Create a modified version of the schema."""
        modified = json.loads(json.dumps(schema))  # Deep copy
        
        # Random modifications
        modification_type = random.choice(['rename', 'add', 'remove', 'datatype'])
        
        if modification_type == 'rename' and modified['columns']:
            # Rename a random column
            col_to_rename = random.choice(modified['columns'])
            new_name = col_to_rename['name'] + '_' + ''.join(random.choices(string.ascii_lowercase, k=3))
            col_to_rename['name'] = new_name
        
        elif modification_type == 'add' and len(modified['columns']) < 20:
            # Add a new column
            new_col = {
                'name': f"new_column_{len(modified['columns'])+1}",
                'dtype': random.choice(['int', 'float', 'str']),
                'sample_value': str(random.randint(1, 100))
            }
            modified['columns'].append(new_col)
        
        elif modification_type == 'remove' and len(modified['columns']) > 2:
            # Remove a random column
            col_to_remove = random.choice(modified['columns'])
            modified['columns'].remove(col_to_remove)
        
        elif modification_type == 'datatype' and modified['columns']:
            # Change datatype of a column
            col_to_change = random.choice(modified['columns'])
            if col_to_change['dtype'] in ['int64', 'float64']:
                new_type = random.choice(['str', 'bool'])
            else:
                new_type = random.choice(['int', 'float'])
            col_to_change['dtype'] = new_type
        
        return modified
    
    def _generate_synthetic_data(self, schema: Dict[str, Any], num_rows: int) -> str:
        """Generate synthetic CSV data using Mistral."""
        try:
            # Build the prompt
            prompt = f"Generate exactly {num_rows} rows of synthetic CSV data with the following columns:\n"
            
            for col in schema['columns']:
                prompt += f"- {col['name']} ({col['dtype']}): Sample value: {col['sample_value']}\n"
            
            prompt += "\nOutput format:\n"
            prompt += ",".join([col['name'] for col in schema['columns']]) + "\n"
            
            # Add sample data row
            sample_row = ",".join([str(schema['sample_data'].get(col['name'], "")) for col in schema['columns']])
            prompt += f"Example: {sample_row}\n\n"
            
            prompt += "Important: Output ONLY the CSV data with header. No explanations, no markdown, no additional text."
            
            # Generate using Mistral
            return self.mistral_handler.generate(prompt)
            
        except Exception as e:
            self.logger.error(f"Synthetic data generation failed: {e}")
            return self._generate_fallback_data(schema, num_rows)
    
    def _generate_fallback_data(self, schema: Dict[str, Any], num_rows: int) -> str:
        """Generate simple CSV when Mistral fails"""
        headers = [col['name'] for col in schema['columns']]
        csv_content = [",".join(headers)]
        
        for _ in range(num_rows):
            row = []
            for col in schema['columns']:
                if col['dtype'] in ['int', 'int64']:
                    row.append(str(random.randint(1, 100)))
                elif col['dtype'] in ['float', 'float64']:
                    row.append(f"{random.uniform(1, 100):.2f}")
                else:
                    row.append(f"Value{random.randint(1, 100)}")
            csv_content.append(",".join(row))
        
        return "\n".join(csv_content)
    
    def _validate_csv(self, csv_data: str) -> bool:
        """Basic CSV validation"""
        if not csv_data:
            return False
        
        lines = csv_data.strip().split('\n')
        if len(lines) < 2:
            return False
        
        # Check if header and at least one data row exist
        if ',' not in lines[0] or ',' not in lines[1]:
            return False
            
        return True
