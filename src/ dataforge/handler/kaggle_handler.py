import os
import logging
import sys
from io import StringIO
from pathlib import Path
from typing import Dict, Any, List
from kaggle.api.kaggle_api_extended import KaggleApi

logger = logging.getLogger(__name__)

class KaggleDatasetHandler:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api = KaggleApi()
        self._authenticate()
        logger.info("Kaggle API initialized successfully")
    
    def _authenticate(self):
        """Handle authentication with version check suppression"""
        original_stderr = sys.stderr
        sys.stderr = StringIO()
        
        try:
            self.api.authenticate()
            logger.debug("Kaggle authentication successful")
        except Exception as e:
            logger.error(f"Kaggle authentication failed: {e}")
            raise
        finally:
            sys.stderr = original_stderr
    
    def search_datasets(self, keyword: str) -> List[Dict[str, Any]]:
        """Search Kaggle for datasets matching keyword"""
        try:
            logger.info(f"Searching Kaggle for '{keyword}'")
            
            # FIXED: Removed deprecated 'size' parameter
            datasets = self.api.dataset_list(
                search=keyword,
                page=1,
                file_type='csv'
                # Removed: size='medium' - this was causing the error
            )
            
            logger.info(f"Initial search returned {len(datasets)} datasets")
            
            # Filter datasets based on config
            filtered = []
            max_size = self.config.get('max_download_size_mb', 200) * 1024 * 1024  # Increased to 200MB
            min_rating = self.config.get('min_rating', 5.0)  # Lowered to 5.0 for more results
            
            for ds in datasets:
                try:
                    # Handle datasets without size info - allow them through
                    size_ok = True
                    if hasattr(ds, 'totalBytes') and ds.totalBytes:
                        size_ok = ds.totalBytes < max_size
                    elif hasattr(ds, 'size') and ds.size:
                        size_ok = ds.size < max_size
                    
                    # Handle datasets without rating - allow them through
                    rating_ok = True
                    if hasattr(ds, 'usabilityRating') and ds.usabilityRating:
                        rating_ok = ds.usabilityRating >= min_rating
                    
                    # Very permissive filtering - accept most datasets
                    if size_ok and rating_ok:
                        filtered.append({
                            'ref': ds.ref,
                            'title': ds.title,
                            'size': getattr(ds, 'totalBytes', getattr(ds, 'size', 0)),
                            'files': getattr(ds, 'files', []),
                            'rating': getattr(ds, 'usabilityRating', None)
                        })
                        logger.info(f"Added dataset: {ds.title}")
                
                except Exception as e:
                    logger.warning(f"Error processing dataset {getattr(ds, 'title', 'Unknown')}: {e}")
                    # Continue processing other datasets
                    continue
            
            logger.info(f"Found {len(filtered)} suitable datasets")
            
            # If no filtered results, return first few datasets anyway
            if not filtered and datasets:
                logger.warning("No datasets passed filtering, returning first 3 anyway")
                for ds in datasets[:3]:
                    try:
                        filtered.append({
                            'ref': ds.ref,
                            'title': ds.title,
                            'size': getattr(ds, 'totalBytes', getattr(ds, 'size', 0)),
                            'files': getattr(ds, 'files', []),
                            'rating': getattr(ds, 'usabilityRating', None)
                        })
                    except:
                        continue
            
            return filtered[:self.config.get('max_results', 5)]
        
        except Exception as e:
            logger.error(f"Dataset search failed: {e}", exc_info=True)
            return []
    
    def download_dataset(self, dataset_meta: Dict[str, Any], output_dir: Path) -> Path:
        """Download the best dataset to output_dir"""
        try:
            ref = dataset_meta['ref']
            logger.info(f"Downloading dataset: {ref}")
            
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Download dataset
            self.api.dataset_download_files(
                ref,
                path=str(output_dir),
                unzip=True,
                quiet=True
            )
            
            # Find CSV files
            csv_files = list(output_dir.glob('*.csv'))
            if not csv_files:
                # Look for CSV files in subdirectories
                csv_files = list(output_dir.glob('**/*.csv'))
            
            if not csv_files:
                raise FileNotFoundError("No CSV files found in downloaded dataset")
            
            # Select largest CSV file that's not too big
            valid_files = [f for f in csv_files if f.stat().st_size > 1024]  # At least 1KB
            if not valid_files:
                valid_files = csv_files
            
            main_file = max(valid_files, key=lambda f: f.stat().st_size)
            logger.info(f"Downloaded dataset to: {main_file} ({main_file.stat().st_size/1024:.1f} KB)")
            
            return main_file
        
        except Exception as e:
            logger.error(f"Dataset download failed: {e}", exc_info=True)
            raise
