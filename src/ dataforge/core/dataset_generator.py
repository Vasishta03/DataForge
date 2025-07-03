import os
import logging
import time
import random
from pathlib import Path
from typing import Dict, Any, Callable
import pandas as pd

from dataforge.handlers.kaggle_handler import KaggleDatasetHandler
from dataforge.handlers.mistral_handler import MistralHandler

class DatasetGenerator:
    """Enhanced dataset generator with improved prompting and API integration"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize handlers with enhanced configuration
        self.kaggle_handler = KaggleDatasetHandler(config.get('kaggle', {}))
        self.mistral_handler = MistralHandler(config.get('mistral', {}))
        
        self.progress_callback = None
        self.status_callback = None
        self.should_stop = False
        
        # Setup paths
        self.base_path = Path.cwd()
        self.reference_path = self.base_path / config.get('paths', {}).get('reference_datasets', 'data/reference_datasets')
        self.generated_path = self.base_path / config.get('paths', {}).get('generated_datasets', 'data/generated_datasets')
        
        # Create directories
        self.reference_path.mkdir(parents=True, exist_ok=True)
        self.generated_path.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("Enhanced DatasetGenerator initialized successfully")
    
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
        self.logger.info(message)
    
    def generate_datasets(self, keyword: str, num_rows: int = 500, num_variations: int = 6) -> Dict[str, Any]:
        """Enhanced dataset generation with improved prompting"""
        start_time = time.time()
        results = {
            'keyword': keyword,
            'reference_dataset': None,
            'generated_files': [],
            'total_time': None,
            'api_info': {
                'base_url': 'http://localhost:5000',
                'endpoints': {
                    'list_datasets': '/api/datasets',
                    'download_zip': f'/api/download-zip/{keyword}',
                    'individual_files': f'/api/download/{keyword}/<filename>'
                },
                'api_key': 'dataforge_api_2025'
            }
        }
        
        try:
            self.should_stop = False
            self._update_progress(0.1, f"🔍 Initializing generation for '{keyword}'")
            
            # Step 1: Get reference data
            self._update_status(f"Searching for {keyword} reference data")
            reference_file = self._get_reference_data(keyword)
            results['reference_dataset'] = str(reference_file)
            
            # Step 2: Enhanced schema extraction
            self._update_progress(0.2, "🔬 Analyzing data structure")
            self._update_status("Extracting enhanced schema")
            schema = self._extract_enhanced_schema(reference_file, keyword)
            
            # Step 3: Generate high-quality variations
            output_dir = self.generated_path / keyword
            output_dir.mkdir(exist_ok=True)
            
            for i in range(num_variations):
                if self.should_stop:
                    self._update_status("Generation stopped by user")
                    break
                
                progress = 0.3 + (i / num_variations) * 0.6
                self._update_progress(progress, f"🎨 Creating dataset {i+1}/{num_variations}")
                self._update_status(f"Generating high-quality synthetic dataset {i+1} of {num_variations}")
                
                # Generate with enhanced prompting
                csv_data = self._generate_enhanced_dataset(schema, num_rows, keyword, i+1)
                
                # Save with meaningful filename
                timestamp = int(time.time())
                filename = f"{keyword}_synthetic_v{i+1}_{timestamp}.csv"
                output_file = output_dir / filename
                
                with open(output_file, 'w', encoding='utf-8', newline='') as f:
                    f.write(csv_data)
                
                results['generated_files'].append(str(output_file))
                self.logger.info(f"✅ Generated: {output_file}")
                
                # Brief pause for UI responsiveness
                time.sleep(0.3)
            
            self._update_progress(1.0, "✨ Generation completed successfully")
            self._update_status(f"🎉 Successfully generated {len(results['generated_files'])} high-quality datasets")
            
        except Exception as e:
            self.logger.error(f"Generation failed: {e}")
            self._update_status(f"❌ Generation failed: {str(e)}")
            
            # Ensure at least one file exists
            if not results['generated_files']:
                try:
                    output_dir = self.generated_path / keyword
                    output_dir.mkdir(exist_ok=True)
                    fallback_file = output_dir / f"{keyword}_fallback.csv"
                    self._create_enhanced_fallback(fallback_file, keyword, num_rows)
                    results['generated_files'].append(str(fallback_file))
                except Exception as fallback_error:
                    self.logger.error(f"Fallback generation failed: {fallback_error}")
        
        finally:
            results['total_time'] = time.time() - start_time
            return results
    
    def _get_reference_data(self, keyword: str) -> Path:
        """Get reference data from Kaggle or create fallback"""
        try:
            dataset_metadata = self.kaggle_handler.search_datasets(keyword)
            
            if dataset_metadata:
                self._update_status(f"📥 Downloading: {dataset_metadata[0]['title']}")
                return self.kaggle_handler.download_dataset(
                    dataset_metadata[0],
                    self.reference_path
                )
            else:
                self._update_status("📋 Creating reference template")
                return self._create_reference_template(keyword)
                
        except Exception as e:
            self.logger.error(f"Reference data acquisition failed: {e}")
            return self._create_reference_template(keyword)
    
    def _create_reference_template(self, keyword: str) -> Path:
        """Create domain-specific reference template"""
        reference_file = self.reference_path / f"{keyword}_reference.csv"
        
        # Domain-specific templates
        templates = {
            'healthcare': {
                'patient_id': range(1001, 1051),
                'age': [random.randint(18, 85) for _ in range(50)],
                'gender': [random.choice(['Male', 'Female', 'Other']) for _ in range(50)],
                'diagnosis': [random.choice(['Hypertension', 'Diabetes', 'Asthma', 'Arthritis']) for _ in range(50)],
                'treatment_cost': [round(random.uniform(100, 5000), 2) for _ in range(50)]
            },
            'finance': {
                'account_id': [f"ACC{i:04d}" for i in range(1, 51)],
                'balance': [round(random.uniform(100, 50000), 2) for _ in range(50)],
                'account_type': [random.choice(['Checking', 'Savings', 'Credit']) for _ in range(50)],
                'transaction_count': [random.randint(1, 100) for _ in range(50)],
                'last_activity': [f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}" for _ in range(50)]
            },
            'education': {
                'student_id': [f"STU{i:04d}" for i in range(1, 51)],
                'course_name': [random.choice(['Mathematics', 'Science', 'English', 'History']) for _ in range(50)],
                'grade': [round(random.uniform(60, 100), 1) for _ in range(50)],
                'credits': [random.choice([1, 2, 3, 4]) for _ in range(50)],
                'semester': [random.choice(['Fall2024', 'Spring2024', 'Summer2024']) for _ in range(50)]
            }
        }
        
        # Select appropriate template
        template_data = templates.get(keyword.lower(), {
            'id': range(1, 51),
            'name': [f"{keyword}_item_{i}" for i in range(1, 51)],
            'value': [round(random.uniform(10, 1000), 2) for _ in range(50)],
            'category': [f"cat_{i%5}" for i in range(50)],
            'status': [random.choice(['active', 'inactive']) for _ in range(50)]
        })
        
        df = pd.DataFrame(template_data)
        df.to_csv(reference_file, index=False)
        self.logger.info(f"Created reference template: {reference_file}")
        return reference_file
    
    def _extract_enhanced_schema(self, dataset_path: Path, keyword: str) -> Dict[str, Any]:
        """Extract enhanced schema with domain context"""
        try:
            df = pd.read_csv(dataset_path, nrows=20)
            schema = {
                'columns': [],
                'sample_data': {},
                'domain': keyword,
                'statistics': {}
            }
            
            for col in df.columns:
                col_info = {
                    'name': str(col).strip(),
                    'dtype': str(df[col].dtype),
                    'sample_value': str(df[col].iloc[0]) if len(df) > 0 else "",
                    'unique_values': min(df[col].nunique(), 10),
                    'null_count': df[col].isnull().sum()
                }
                
                # Add statistical information for numeric columns
                if df[col].dtype in ['int64', 'float64']:
                    col_info['min_value'] = float(df[col].min())
                    col_info['max_value'] = float(df[col].max())
                    col_info['mean_value'] = float(df[col].mean())
                
                schema['columns'].append(col_info)
                schema['sample_data'][col] = col_info['sample_value']
            
            return schema
            
        except Exception as e:
            self.logger.error(f"Enhanced schema extraction failed: {e}")
            return self._get_fallback_schema(keyword)
    
    def _get_fallback_schema(self, keyword: str) -> Dict[str, Any]:
        """Get fallback schema based on domain"""
        domain_schemas = {
            'healthcare': {
                'columns': [
                    {'name': 'patient_id', 'dtype': 'int64', 'sample_value': '1001'},
                    {'name': 'age', 'dtype': 'int64', 'sample_value': '45'},
                    {'name': 'diagnosis', 'dtype': 'object', 'sample_value': 'Hypertension'},
                    {'name': 'treatment_cost', 'dtype': 'float64', 'sample_value': '2500.50'}
                ]
            },
            'finance': {
                'columns': [
                    {'name': 'account_id', 'dtype': 'object', 'sample_value': 'ACC001'},
                    {'name': 'balance', 'dtype': 'float64', 'sample_value': '15000.75'},
                    {'name': 'transaction_type', 'dtype': 'object', 'sample_value': 'credit'},
                    {'name': 'amount', 'dtype': 'float64', 'sample_value': '1200.00'}
                ]
            }
        }
        
        return domain_schemas.get(keyword.lower(), {
            'columns': [
                {'name': 'id', 'dtype': 'int64', 'sample_value': '1'},
                {'name': 'name', 'dtype': 'object', 'sample_value': 'Sample Item'},
                {'name': 'value', 'dtype': 'float64', 'sample_value': '100.0'},
                {'name': 'category', 'dtype': 'object', 'sample_value': 'Category A'}
            ],
            'domain': keyword,
            'sample_data': {}
        })
    
    def _generate_enhanced_dataset(self, schema: Dict, num_rows: int, keyword: str, variation: int) -> str:
        """Generate dataset using enhanced Mistral prompting"""
        try:
            # Use enhanced Mistral handler
            result = self.mistral_handler.generate(schema, num_rows, keyword)
            
            if result and len(result.strip()) > 50:
                # Validate the generated data
                if self._validate_enhanced_csv(result, schema):
                    return result
            
        except Exception as e:
            self.logger.error(f"Enhanced generation failed: {e}")
        
        # Enhanced fallback
        return self._generate_programmatic_enhanced(schema, num_rows, keyword, variation)
    
    def _validate_enhanced_csv(self, csv_data: str, schema: Dict) -> bool:
        """Enhanced CSV validation"""
        try:
            lines = csv_data.strip().split('\n')
            if len(lines) < 2:
                return False
            
            # Check header
            header = lines[0].split(',')
            expected_cols = [col['name'] for col in schema.get('columns', [])]
            
            if len(header) != len(expected_cols):
                return False
            
            # Check at least one data row
            data_row = lines[1].split(',')
            return len(data_row) == len(header)
            
        except Exception:
            return False
    
    def _generate_programmatic_enhanced(self, schema: Dict, num_rows: int, keyword: str, variation: int) -> str:
        """Enhanced programmatic generation with domain awareness"""
        columns = schema.get('columns', [])
        if not columns:
            return self._create_basic_csv(num_rows, keyword)
        
        # Create header
        headers = [col['name'] for col in columns]
        csv_lines = [','.join(headers)]
        
        # Generate enhanced data rows
        for row_num in range(min(num_rows, 200)):
            row = []
            for col in columns:
                value = self._generate_enhanced_value(col, row_num, keyword, variation)
                row.append(str(value))
            
            csv_lines.append(','.join(row))
        
        return '\n'.join(csv_lines)
    
    def _generate_enhanced_value(self, col: Dict, row_num: int, keyword: str, variation: int) -> str:
        """Generate enhanced realistic values"""
        col_name = col['name'].lower()
        col_type = col.get('dtype', 'object').lower()
        
        # Add variation to make each dataset unique
        seed_modifier = variation * 1000 + row_num
        
        # Domain-specific generation
        if 'health' in keyword.lower():
            return self._generate_healthcare_value(col_name, col_type, seed_modifier)
        elif 'finance' in keyword.lower():
            return self._generate_finance_value(col_name, col_type, seed_modifier)
        elif 'education' in keyword.lower():
            return self._generate_education_value(col_name, col_type, seed_modifier)
        else:
            return self._generate_generic_value(col_name, col_type, seed_modifier)
    
    def _generate_healthcare_value(self, col_name: str, col_type: str, seed: int) -> str:
        """Generate healthcare-specific values"""
        random.seed(seed)
        
        if 'patient' in col_name or 'id' in col_name:
            return str(1000 + (seed % 10000))
        elif 'age' in col_name:
            return str(random.randint(1, 95))
        elif 'diagnosis' in col_name or 'condition' in col_name:
            conditions = ['Hypertension', 'Diabetes Type 2', 'Asthma', 'Arthritis', 'Migraine', 'Pneumonia', 'Depression']
            return random.choice(conditions)
        elif 'cost' in col_name or 'price' in col_name:
            return f"{random.uniform(50, 8000):.2f}"
        elif 'date' in col_name:
            return f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        else:
            return f"Health_Value_{seed % 100}"
    
    def _generate_finance_value(self, col_name: str, col_type: str, seed: int) -> str:
        """Generate finance-specific values"""
        random.seed(seed)
        
        if 'account' in col_name or 'id' in col_name:
            return f"ACC{(seed % 10000):04d}"
        elif 'balance' in col_name or 'amount' in col_name:
            return f"{random.uniform(100, 100000):.2f}"
        elif 'type' in col_name:
            types = ['Checking', 'Savings', 'Credit', 'Investment', 'Loan']
            return random.choice(types)
        elif 'transaction' in col_name:
            transactions = ['Deposit', 'Withdrawal', 'Transfer', 'Payment', 'Fee']
            return random.choice(transactions)
        elif 'date' in col_name:
            return f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        else:
            return f"Finance_Value_{seed % 100}"
    
    def _generate_education_value(self, col_name: str, col_type: str, seed: int) -> str:
        """Generate education-specific values"""
        random.seed(seed)
        
        if 'student' in col_name or 'id' in col_name:
            return f"STU{(seed % 10000):04d}"
        elif 'grade' in col_name or 'score' in col_name:
            return f"{random.uniform(60, 100):.1f}"
        elif 'course' in col_name or 'subject' in col_name:
            courses = ['Mathematics', 'Science', 'English', 'History', 'Art', 'Computer Science', 'Biology']
            return random.choice(courses)
        elif 'credit' in col_name:
            return str(random.choice([1, 2, 3, 4, 5]))
        elif 'semester' in col_name:
            semesters = ['Fall2024', 'Spring2024', 'Summer2024', 'Fall2023', 'Spring2025']
            return random.choice(semesters)
        else:
            return f"Education_Value_{seed % 100}"
    
    def _generate_generic_value(self, col_name: str, col_type: str, seed: int) -> str:
        """Generate generic realistic values"""
        random.seed(seed)
        
        if 'id' in col_name:
            return str(1000 + (seed % 10000))
        elif 'name' in col_name:
            return f"Item_{seed % 1000}"
        elif 'email' in col_name:
            domains = ['gmail.com', 'yahoo.com', 'company.com', 'business.org']
            return f"user{seed % 1000}@{random.choice(domains)}"
        elif 'int' in col_type:
            return str(random.randint(1, 1000))
        elif 'float' in col_type:
            return f"{random.uniform(1, 1000):.2f}"
        elif 'date' in col_name:
            return f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        else:
            return f"Value_{seed % 1000}"
    
    def _create_enhanced_fallback(self, file_path: Path, keyword: str, num_rows: int):
        """Create enhanced fallback CSV"""
        # Use domain-appropriate structure
        if 'health' in keyword.lower():
            data = {
                'patient_id': [f"P{i:04d}" for i in range(1, min(num_rows + 1, 101))],
                'age': [random.randint(18, 85) for _ in range(min(num_rows, 100))],
                'condition': [random.choice(['Hypertension', 'Diabetes', 'Asthma']) for _ in range(min(num_rows, 100))],
                'cost': [round(random.uniform(100, 5000), 2) for _ in range(min(num_rows, 100))]
            }
        else:
            data = {
                'id': range(1, min(num_rows + 1, 101)),
                'name': [f"{keyword}_item_{i}" for i in range(1, min(num_rows + 1, 101))],
                'value': [round(random.uniform(10, 1000), 2) for _ in range(min(num_rows, 100))],
                'category': [f"category_{i%5}" for i in range(min(num_rows, 100))]
            }
        
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)
        self.logger.info(f"Created enhanced fallback: {file_path}")
    
    def _create_basic_csv(self, num_rows: int, keyword: str) -> str:
        """Create basic CSV when all else fails"""
        headers = ['id', 'name', 'value', 'status']
        csv_lines = [','.join(headers)]
        
        for i in range(min(num_rows, 50)):
            row = [
                str(i + 1),
                f"{keyword}_item_{i + 1}",
                f"{random.uniform(10, 1000):.2f}",
                random.choice(['active', 'inactive'])
            ]
            csv_lines.append(','.join(row))
        
        return '\n'.join(csv_lines)
