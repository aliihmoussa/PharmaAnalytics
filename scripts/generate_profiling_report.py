"""Batch profiling script with parallel processing for performance."""

import sys
import os
import json
from pathlib import Path
from datetime import date
from typing import List, Dict
from concurrent.futures import ProcessPoolExecutor, as_completed
import argparse

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from sqlalchemy import distinct, func
from backend.app.database.models import DrugTransaction
from backend.app.database.session import get_db_session
from backend.app.modules.ml.diagnostics import DrugProfiler
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_all_drug_codes(limit: int = None) -> List[str]:
    """Get all unique drug codes from database."""
    session = get_db_session()
    try:
        query = session.query(distinct(DrugTransaction.drug_code))
        if limit:
            query = query.limit(limit)
        drug_codes = [row[0] for row in query.all()]
        logger.info(f"Found {len(drug_codes)} drug codes")
        return drug_codes
    finally:
        session.close()


def profile_drug(drug_code: str, output_dir: Path) -> Dict:
    """Profile a single drug (for parallel processing)."""
    try:
        profiler = DrugProfiler(use_cache=False)  # Don't use cache in batch mode
        result = profiler.profile(drug_code=drug_code)
        
        # Save individual report
        report_file = output_dir / f"{drug_code}.json"
        with open(report_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        return {
            'drug_code': drug_code,
            'success': True,
            'category': result.get('classification', {}).get('category', 'unknown')
        }
    except Exception as e:
        logger.error(f"Error profiling {drug_code}: {str(e)}")
        return {
            'drug_code': drug_code,
            'success': False,
            'error': str(e)
        }


def generate_summary_report(results: List[Dict], output_dir: Path):
    """Generate summary report from all profiling results."""
    summary = {
        'total_drugs': len(results),
        'successful': sum(1 for r in results if r.get('success')),
        'failed': sum(1 for r in results if not r.get('success')),
        'classifications': {},
        'data_quality_summary': {
            'high_quality': 0,
            'medium_quality': 0,
            'low_quality': 0
        }
    }
    
    # Count classifications
    for result in results:
        if result.get('success'):
            category = result.get('category', 'unknown')
            summary['classifications'][category] = summary['classifications'].get(category, 0) + 1
    
    # Generate markdown summary
    markdown = f"""# Drug Profiling Summary Report

Generated: {date.today().isoformat()}

## Overview

- **Total Drugs**: {summary['total_drugs']}
- **Successfully Profiled**: {summary['successful']}
- **Failed**: {summary['failed']}

## Drug Classifications

"""
    
    for category, count in sorted(summary['classifications'].items(), key=lambda x: x[1], reverse=True):
        percentage = (count / summary['successful'] * 100) if summary['successful'] > 0 else 0
        markdown += f"- **{category.capitalize()}**: {count} ({percentage:.1f}%)\n"
    
    markdown += f"""
## Recommendations

1. **Fast-moving drugs**: Use ML models with high-frequency features
2. **Seasonal drugs**: Use seasonal models (Prophet, SARIMA)
3. **Intermittent drugs**: Use specialized intermittent demand forecasting
4. **Erratic drugs**: Use robust models with regularization
5. **Slow-moving drugs**: Use simple baseline models

## Next Steps

1. Review individual drug reports in `profiling_reports/`
2. Use classifications to select appropriate forecasting models
3. Address data quality issues for low-quality drugs
4. Set up automated profiling pipeline

"""
    
    # Save summary
    summary_file = output_dir / 'summary.md'
    with open(summary_file, 'w') as f:
        f.write(markdown)
    
    # Save JSON summary
    summary_json_file = output_dir / 'summary.json'
    with open(summary_json_file, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    logger.info(f"Summary report saved to {summary_file}")
    return summary


def main():
    """Main function for batch profiling."""
    parser = argparse.ArgumentParser(description='Generate profiling reports for all drugs')
    parser.add_argument('--limit', type=int, help='Limit number of drugs to profile')
    parser.add_argument('--output-dir', type=str, default='docs/profiling_reports',
                       help='Output directory for reports')
    parser.add_argument('--workers', type=int, default=4,
                       help='Number of parallel workers')
    parser.add_argument('--drug-code', type=str, help='Profile single drug code')
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Workers: {args.workers}")
    
    # Get drug codes
    if args.drug_code:
        drug_codes = [args.drug_code]
        logger.info(f"Profiling single drug: {args.drug_code}")
    else:
        drug_codes = get_all_drug_codes(limit=args.limit)
        logger.info(f"Profiling {len(drug_codes)} drugs")
    
    # Profile drugs in parallel
    results = []
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        # Submit all tasks
        future_to_drug = {
            executor.submit(profile_drug, drug_code, output_dir): drug_code
            for drug_code in drug_codes
        }
        
        # Collect results
        for future in as_completed(future_to_drug):
            drug_code = future_to_drug[future]
            try:
                result = future.result()
                results.append(result)
                if result.get('success'):
                    logger.info(f"✅ Profiled {drug_code}: {result.get('category', 'unknown')}")
                else:
                    logger.warning(f"❌ Failed to profile {drug_code}: {result.get('error')}")
            except Exception as e:
                logger.error(f"❌ Exception profiling {drug_code}: {str(e)}")
                results.append({
                    'drug_code': drug_code,
                    'success': False,
                    'error': str(e)
                })
    
    # Generate summary
    if not args.drug_code:
        summary = generate_summary_report(results, output_dir)
        logger.info(f"\n📊 Summary: {summary['successful']}/{summary['total_drugs']} successful")
        logger.info(f"Classifications: {summary['classifications']}")
    
    logger.info(f"\n✅ Profiling complete! Reports saved to {output_dir}")


if __name__ == '__main__':
    main()

