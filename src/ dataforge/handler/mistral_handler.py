import logging
import random
import re
from typing import Dict, List

logger = logging.getLogger(__name__)

class MistralHandler:
    """Enhanced Mistral handler with improved prompting techniques"""
    
    def __init__(self, config):
        self.config = config
        self.model_name = config.get('model_name', 'mistral')
        self.max_tokens = config.get('max_tokens', 2000)
        self.temperature = config.get('temperature', 0.7)
        
        # Advanced prompt templates based on research
        self.prompt_templates = {
            'healthcare': self._get_healthcare_template(),
            'finance': self._get_finance_template(),
            'education': self._get_education_template(),
            'retail': self._get_retail_template(),
            'default': self._get_default_template()
        }
        
        self._verify_ollama()
    
    def _verify_ollama(self):
        """Verify Ollama connection"""
        try:
            import ollama
            models = ollama.list()
            available = [m.get('name', '') for m in models.get('models', [])]
            
            if any(self.model_name in name for name in available):
                logger.info(f"Verified Ollama model: {self.model_name}")
                self.ollama = ollama
                self.available = True
            else:
                logger.warning(f"Model {self.model_name} not found, using fallback")
                self.ollama = None
                self.available = False
        except Exception as e:
            logger.error(f"Ollama verification failed: {e}")
            self.ollama = None
            self.available = False
    
    def generate(self, schema: Dict, num_rows: int, keyword: str = "") -> str:
        """Generate synthetic data with enhanced prompts"""
        
        # Select appropriate template
        template_key = keyword.lower() if keyword.lower() in self.prompt_templates else 'default'
        template = self.prompt_templates[template_key]
        
        # Build enhanced prompt
        prompt = self._build_enhanced_prompt(schema, num_rows, template, keyword)
        
        if self.available and self.ollama:
            try:
                response = self.ollama.generate(
                    model=self.model_name,
                    prompt=prompt,
                    options={
                        'num_predict': self.max_tokens,
                        'temperature': self.temperature,
                        'top_p': 0.9,
                        'repeat_penalty': 1.1
                    }
                )
                result = response.get('response', '')
                if result and len(result.strip()) > 50:
                    cleaned = self._clean_and_validate_csv(result, schema)
                    if cleaned:
                        return cleaned
            except Exception as e:
                logger.error(f"Ollama generation failed: {e}")
        
        # Enhanced fallback generation
        return self._generate_enhanced_fallback(schema, num_rows, keyword)
    
    def _build_enhanced_prompt(self, schema: Dict, num_rows: int, template: Dict, keyword: str) -> str:
        """Build enhanced prompt using research-based techniques"""
        
        columns = schema.get('columns', [])
        sample_data = schema.get('sample_data', {})
        
        # Extract column information
        column_specs = []
        for col in columns:
            col_name = col['name']
            col_type = col['dtype']
            sample_val = sample_data.get(col_name, '')
            
            # Enhanced type specification
            if 'int' in col_type.lower() or col_name.lower() in ['id', 'age', 'count', 'number']:
                spec = f"{col_name}: integer values (like {sample_val})"
            elif 'float' in col_type.lower() or col_name.lower() in ['price', 'amount', 'rate', 'score']:
                spec = f"{col_name}: decimal values (like {sample_val})"
            elif col_name.lower() in ['date', 'time', 'created', 'updated']:
                spec = f"{col_name}: date/time values (format like {sample_val})"
            elif col_name.lower() in ['email', 'phone', 'address']:
                spec = f"{col_name}: realistic {col_name.lower()} format"
            else:
                spec = f"{col_name}: text values (like {sample_val})"
            
            column_specs.append(spec)
        
        # Build comprehensive prompt
        prompt = f"""You are an expert synthetic data generator specializing in {keyword} domain data.

TASK: Generate exactly {num_rows} rows of realistic CSV data.

DOMAIN CONTEXT: {template['context']}

COLUMN SPECIFICATIONS:
{chr(10).join(f"- {spec}" for spec in column_specs)}

DATA QUALITY REQUIREMENTS:
{template['quality_requirements']}

OUTPUT FORMAT:
- Start with header row: {','.join(col['name'] for col in columns)}
- Follow with exactly {num_rows} data rows
- Use proper CSV formatting (comma-separated, no extra quotes unless needed)
- Ensure realistic, domain-appropriate values
- Maintain data consistency and relationships

EXAMPLE STRUCTURE:
{template['example']}

Generate the CSV data now:"""

        return prompt
    
    def _get_healthcare_template(self) -> Dict:
        """Healthcare domain template based on research [2][5]"""
        return {
            'context': "Healthcare and medical data with patient records, treatments, and medical terminology. Focus on realistic medical scenarios while maintaining privacy.",
            'quality_requirements': """
- Use realistic medical terminology and codes
- Maintain logical relationships (age vs conditions)
- Include diverse demographic representation
- Follow medical data standards (ICD codes, etc.)
- Ensure temporal consistency in dates""",
            'example': "patient_id,age,gender,diagnosis,treatment_cost,admission_date\n1001,45,Female,Hypertension,2500.50,2024-01-15"
        }
    
    def _get_finance_template(self) -> Dict:
        """Finance domain template"""
        return {
            'context': "Financial and banking data including transactions, accounts, and market data. Focus on realistic financial patterns and regulations.",
            'quality_requirements': """
- Use realistic financial amounts and ranges
- Maintain transaction balance logic
- Include diverse account types and statuses
- Follow financial data formats (currency, percentages)
- Ensure regulatory compliance patterns""",
            'example': "account_id,balance,transaction_type,amount,date\nACC001,15000.75,credit,1200.00,2024-01-15"
        }
    
    def _get_education_template(self) -> Dict:
        """Education domain template"""
        return {
            'context': "Educational data including students, courses, grades, and academic performance. Focus on realistic academic scenarios.",
            'quality_requirements': """
- Use realistic grade ranges and academic terms
- Maintain logical course-grade relationships
- Include diverse student demographics
- Follow academic calendar patterns
- Ensure grade progression consistency""",
            'example': "student_id,course_name,grade,credits,semester\nSTU001,Mathematics,85.5,3,Fall2024"
        }
    
    def _get_retail_template(self) -> Dict:
        """Retail domain template"""
        return {
            'context': "Retail and e-commerce data including products, sales, and customer transactions. Focus on realistic shopping patterns.",
            'quality_requirements': """
- Use realistic product names and categories
- Maintain logical price-quantity relationships
- Include seasonal shopping patterns
- Follow retail data standards
- Ensure inventory consistency""",
            'example': "product_id,product_name,category,price,stock_quantity\nPRD001,Wireless Headphones,Electronics,89.99,150"
        }
    
    def _get_default_template(self) -> Dict:
        """Default template for general data"""
        return {
            'context': "General business data with realistic patterns and relationships appropriate for the specified domain.",
            'quality_requirements': """
- Use realistic and consistent data values
- Maintain logical relationships between columns
- Include appropriate data distributions
- Follow common data standards and formats
- Ensure data quality and completeness""",
            'example': "id,name,category,value,status\n1,Sample Item,Category A,100.0,active"
        }
    
    def _clean_and_validate_csv(self, output: str, schema: Dict) -> str:
        """Enhanced CSV cleaning and validation"""
        try:
            lines = output.strip().split('\n')
            csv_lines = []
            expected_cols = len(schema.get('columns', []))
            
            # Find header line
            header_found = False
            for i, line in enumerate(lines):
                if ',' in line and len(line.split(',')) == expected_cols:
                    # Potential header or data line
                    if not header_found:
                        # First valid line is header
                        csv_lines.append(line.strip())
                        header_found = True
                    else:
                        # Data line
                        cleaned_line = self._clean_csv_line(line.strip())
                        if cleaned_line:
                            csv_lines.append(cleaned_line)
                
                # Limit to prevent excessive data
                if len(csv_lines) > 101:  # Header + 100 rows max
                    break
            
            if len(csv_lines) >= 2:  # At least header + 1 data row
                return '\n'.join(csv_lines)
            
        except Exception as e:
            logger.error(f"CSV cleaning failed: {e}")
        
        return None
    
    def _clean_csv_line(self, line: str) -> str:
        """Clean individual CSV line"""
        # Remove common artifacts
        line = re.sub(r'^[^a-zA-Z0-9]', '', line)  # Remove leading non-alphanumeric
        line = re.sub(r'[^a-zA-Z0-9,.\-_@\s]', '', line)  # Remove special chars except CSV-safe ones
        
        # Ensure proper CSV format
        if ',' in line and len(line.split(',')) >= 2:
            return line
        
        return None
    
    def _generate_enhanced_fallback(self, schema: Dict, num_rows: int, keyword: str) -> str:
        """Enhanced fallback generation with domain awareness"""
        columns = schema.get('columns', [])
        if not columns:
            return self._generate_basic_fallback(num_rows)
        
        # Create header
        headers = [col['name'] for col in columns]
        csv_lines = [','.join(headers)]
        
        # Domain-specific value generators
        domain_generators = self._get_domain_generators(keyword)
        
        # Generate data rows
        for row_num in range(min(num_rows, 100)):
            row = []
            for col in columns:
                col_name = col['name'].lower()
                col_type = col['dtype'].lower()
                
                # Generate value based on column name and type
                value = self._generate_column_value(col_name, col_type, row_num, domain_generators)
                row.append(str(value))
            
            csv_lines.append(','.join(row))
        
        return '\n'.join(csv_lines)
    
    def _get_domain_generators(self, keyword: str) -> Dict:
        """Get domain-specific value generators"""
        keyword = keyword.lower()
        
        if 'health' in keyword or 'medical' in keyword:
            return {
                'names': ['John Smith', 'Sarah Johnson', 'Michael Brown', 'Emily Davis', 'David Wilson'],
                'conditions': ['Hypertension', 'Diabetes', 'Asthma', 'Arthritis', 'Migraine'],
                'departments': ['Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics', 'Emergency']
            }
        elif 'finance' in keyword or 'bank' in keyword:
            return {
                'names': ['Alice Cooper', 'Bob Johnson', 'Carol White', 'David Lee', 'Eva Martinez'],
                'account_types': ['Checking', 'Savings', 'Credit', 'Investment', 'Loan'],
                'transaction_types': ['Deposit', 'Withdrawal', 'Transfer', 'Payment', 'Fee']
            }
        elif 'education' in keyword or 'school' in keyword:
            return {
                'names': ['Alex Chen', 'Maria Garcia', 'James Kim', 'Lisa Wang', 'Tom Anderson'],
                'courses': ['Mathematics', 'Science', 'English', 'History', 'Art'],
                'majors': ['Computer Science', 'Biology', 'Business', 'Psychology', 'Engineering']
            }
        else:
            return {
                'names': ['Person A', 'Person B', 'Person C', 'Person D', 'Person E'],
                'categories': ['Category 1', 'Category 2', 'Category 3', 'Category 4', 'Category 5'],
                'statuses': ['Active', 'Inactive', 'Pending', 'Completed', 'Cancelled']
            }
    
    def _generate_column_value(self, col_name: str, col_type: str, row_num: int, generators: Dict) -> str:
        """Generate realistic column value"""
        
        # ID columns
        if 'id' in col_name:
            return str(1000 + row_num)
        
        # Name columns
        if 'name' in col_name:
            return random.choice(generators.get('names', ['Sample Name']))
        
        # Age columns
        if 'age' in col_name:
            return str(random.randint(18, 85))
        
        # Email columns
        if 'email' in col_name:
            name = generators.get('names', ['user'])[row_num % len(generators.get('names', ['user']))]
            domain = random.choice(['gmail.com', 'yahoo.com', 'company.com'])
            return f"{name.lower().replace(' ', '.')}@{domain}"
        
        # Date columns
        if 'date' in col_name or 'time' in col_name:
            return f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        
        # Numeric columns
        if 'int' in col_type or 'number' in col_name:
            if 'price' in col_name or 'cost' in col_name or 'amount' in col_name:
                return f"{random.uniform(10, 1000):.2f}"
            else:
                return str(random.randint(1, 1000))
        
        if 'float' in col_type:
            return f"{random.uniform(1, 100):.2f}"
        
        # Category/Status columns
        if 'category' in col_name:
            return random.choice(generators.get('categories', ['Category A']))
        
        if 'status' in col_name:
            return random.choice(generators.get('statuses', ['Active']))
        
        # Default text value
        return f"{col_name.title()}_{row_num + 1}"
    
    def _generate_basic_fallback(self, num_rows: int) -> str:
        """Basic fallback when schema is unavailable"""
        headers = ['id', 'name', 'value', 'category', 'status']
        csv_lines = [','.join(headers)]
        
        categories = ['A', 'B', 'C', 'D', 'E']
        statuses = ['active', 'inactive', 'pending']
        
        for i in range(min(num_rows, 50)):
            row = [
                str(i + 1),
                f"Item_{i + 1}",
                f"{random.uniform(10, 1000):.2f}",
                random.choice(categories),
                random.choice(statuses)
            ]
            csv_lines.append(','.join(row))
        
        return '\n'.join(csv_lines)
