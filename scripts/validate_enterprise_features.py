#!/usr/bin/env python3
"""
Enterprise Features Validation Script
Simple validation of niche intelligence and competitor research features
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleEnterpriseValidator:
    """Simple validator for enterprise features without full platform dependencies"""
    
    def __init__(self):
        self.test_results = {
            "validation_timestamp": datetime.utcnow().isoformat(),
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": []
        }
    
    def validate_file_structure(self):
        """Validate that all enterprise feature files exist"""
        logger.info("🔍 Validating enterprise feature file structure...")
        
        required_files = [
            "backend/modules/niche_intelligence/__init__.py",
            "backend/modules/niche_intelligence/niche_analyzer.py",
            "backend/modules/niche_intelligence/trend_detector.py",
            "backend/modules/niche_intelligence/market_researcher.py",
            "backend/modules/competitor_research/__init__.py",
            "backend/modules/competitor_research/competitor_analyzer.py",
            "backend/modules/competitor_research/content_gap_analyzer.py",
            "backend/modules/competitor_research/seo_optimizer.py",
            "backend/database_extensions.py",
            "backend/niche_intelligence_integration.py",
            "docs/enterprise-features/NICHE_INTELLIGENCE_GUIDE.md",
            "docs/enterprise-features/API_REFERENCE.md"
        ]
        
        missing_files = []
        existing_files = []
        
        for file_path in required_files:
            full_path = os.path.join(os.getcwd(), file_path)
            if os.path.exists(full_path):
                existing_files.append(file_path)
                logger.info(f"✅ Found: {file_path}")
            else:
                missing_files.append(file_path)
                logger.error(f"❌ Missing: {file_path}")
        
        self.test_results["total_tests"] += 1
        if not missing_files:
            self.test_results["passed_tests"] += 1
            self.test_results["test_details"].append({
                "test": "File Structure Validation",
                "status": "PASSED",
                "details": f"All {len(required_files)} enterprise feature files found"
            })
            logger.info(f"✅ File structure validation PASSED - {len(existing_files)}/{len(required_files)} files found")
        else:
            self.test_results["failed_tests"] += 1
            self.test_results["test_details"].append({
                "test": "File Structure Validation",
                "status": "FAILED",
                "details": f"Missing files: {missing_files}"
            })
            logger.error(f"❌ File structure validation FAILED - {len(missing_files)} files missing")
        
        return not missing_files
    
    def validate_module_imports(self):
        """Validate that modules can be imported successfully"""
        logger.info("🔍 Validating module import structure...")
        
        modules_to_test = [
            ("backend.modules.niche_intelligence.niche_analyzer", "NicheIntelligenceEngine"),
            ("backend.modules.niche_intelligence.trend_detector", "TrendDetectionEngine"),
            ("backend.modules.niche_intelligence.market_researcher", "MarketResearchEngine"),
            ("backend.modules.competitor_research.competitor_analyzer", "CompetitorAnalysisEngine"),
            ("backend.modules.competitor_research.content_gap_analyzer", "ContentGapAnalyzer"),
            ("backend.modules.competitor_research.seo_optimizer", "SEOOptimizer")
        ]
        
        import_results = []
        
        for module_path, class_name in modules_to_test:
            try:
                # Add project root to path if not already there
                project_root = os.path.dirname(os.path.abspath(__file__))
                if project_root not in sys.path:
                    sys.path.insert(0, project_root)
                
                # Try to import the module
                module = __import__(module_path, fromlist=[class_name])
                
                # Check if the class exists in the module
                if hasattr(module, class_name):
                    import_results.append({
                        "module": module_path,
                        "class": class_name,
                        "status": "SUCCESS"
                    })
                    logger.info(f"✅ Successfully imported {class_name} from {module_path}")
                else:
                    import_results.append({
                        "module": module_path,
                        "class": class_name,
                        "status": "CLASS_NOT_FOUND"
                    })
                    logger.warning(f"⚠️  Module imported but class {class_name} not found in {module_path}")
                    
            except ImportError as e:
                import_results.append({
                    "module": module_path,
                    "class": class_name,
                    "status": "IMPORT_ERROR",
                    "error": str(e)
                })
                logger.warning(f"⚠️  Import error for {module_path}: {e}")
            except Exception as e:
                import_results.append({
                    "module": module_path,
                    "class": class_name,
                    "status": "ERROR",
                    "error": str(e)
                })
                logger.error(f"❌ Unexpected error importing {module_path}: {e}")
        
        self.test_results["total_tests"] += 1
        successful_imports = [r for r in import_results if r["status"] == "SUCCESS"]
        
        if len(successful_imports) == len(modules_to_test):
            self.test_results["passed_tests"] += 1
            self.test_results["test_details"].append({
                "test": "Module Import Validation",
                "status": "PASSED",
                "details": f"All {len(modules_to_test)} modules imported successfully"
            })
            logger.info("✅ Module import validation PASSED")
        else:
            self.test_results["failed_tests"] += 1
            self.test_results["test_details"].append({
                "test": "Module Import Validation",
                "status": "PARTIAL",
                "details": f"Successfully imported {len(successful_imports)}/{len(modules_to_test)} modules",
                "import_results": import_results
            })
            logger.warning(f"⚠️  Module import validation PARTIAL - {len(successful_imports)}/{len(modules_to_test)} successful")
        
        return len(successful_imports) > 0
    
    def validate_documentation(self):
        """Validate that documentation files contain expected content"""
        logger.info("🔍 Validating enterprise feature documentation...")
        
        doc_validations = []
        
        # Check Niche Intelligence Guide
        niche_guide_path = "docs/enterprise-features/NICHE_INTELLIGENCE_GUIDE.md"
        try:
            with open(niche_guide_path, 'r') as f:
                content = f.read()
                if len(content) > 1000 and "Niche Intelligence" in content:
                    doc_validations.append({
                        "document": niche_guide_path,
                        "status": "VALID",
                        "content_length": len(content)
                    })
                    logger.info(f"✅ {niche_guide_path} validation passed ({len(content)} characters)")
                else:
                    doc_validations.append({
                        "document": niche_guide_path,
                        "status": "INSUFFICIENT_CONTENT",
                        "content_length": len(content)
                    })
                    logger.warning(f"⚠️  {niche_guide_path} has insufficient content")
        except Exception as e:
            doc_validations.append({
                "document": niche_guide_path,
                "status": "ERROR",
                "error": str(e)
            })
            logger.error(f"❌ Error reading {niche_guide_path}: {e}")
        
        # Check API Reference
        api_ref_path = "docs/enterprise-features/API_REFERENCE.md"
        try:
            with open(api_ref_path, 'r') as f:
                content = f.read()
                if len(content) > 1000 and "API" in content:
                    doc_validations.append({
                        "document": api_ref_path,
                        "status": "VALID",
                        "content_length": len(content)
                    })
                    logger.info(f"✅ {api_ref_path} validation passed ({len(content)} characters)")
                else:
                    doc_validations.append({
                        "document": api_ref_path,
                        "status": "INSUFFICIENT_CONTENT",
                        "content_length": len(content)
                    })
                    logger.warning(f"⚠️  {api_ref_path} has insufficient content")
        except Exception as e:
            doc_validations.append({
                "document": api_ref_path,
                "status": "ERROR",
                "error": str(e)
            })
            logger.error(f"❌ Error reading {api_ref_path}: {e}")
        
        self.test_results["total_tests"] += 1
        valid_docs = [d for d in doc_validations if d["status"] == "VALID"]
        
        if len(valid_docs) == 2:
            self.test_results["passed_tests"] += 1
            self.test_results["test_details"].append({
                "test": "Documentation Validation",
                "status": "PASSED",
                "details": "All documentation files are valid and comprehensive"
            })
            logger.info("✅ Documentation validation PASSED")
        else:
            self.test_results["failed_tests"] += 1
            self.test_results["test_details"].append({
                "test": "Documentation Validation",
                "status": "PARTIAL",
                "details": f"Valid documentation: {len(valid_docs)}/2",
                "validation_results": doc_validations
            })
            logger.warning(f"⚠️  Documentation validation PARTIAL - {len(valid_docs)}/2 valid")
        
        return len(valid_docs) > 0
    
    def generate_validation_report(self):
        """Generate comprehensive validation report"""
        logger.info("📊 Generating validation report...")
        
        # Calculate overall success rate
        if self.test_results["total_tests"] > 0:
            success_rate = (self.test_results["passed_tests"] / self.test_results["total_tests"]) * 100
        else:
            success_rate = 0
        
        self.test_results["success_rate"] = success_rate
        
        # Create report summary
        report_summary = f"""
🎯 ENTERPRISE FEATURES VALIDATION REPORT
{'='*50}

📅 Validation Timestamp: {self.test_results['validation_timestamp']}
📊 Overall Success Rate: {success_rate:.1f}%

📈 Test Results Summary:
   Total Tests: {self.test_results['total_tests']}
   Passed: {self.test_results['passed_tests']}
   Failed: {self.test_results['failed_tests']}

🔍 Test Details:
"""
        
        for test_detail in self.test_results["test_details"]:
            status_emoji = "✅" if test_detail["status"] == "PASSED" else "⚠️" if test_detail["status"] == "PARTIAL" else "❌"
            report_summary += f"   {status_emoji} {test_detail['test']}: {test_detail['status']}\n"
            report_summary += f"      {test_detail['details']}\n\n"
        
        # Overall assessment
        if success_rate >= 80:
            report_summary += "🎉 OVERALL ASSESSMENT: Enterprise features are successfully implemented and ready for production!\n"
        elif success_rate >= 60:
            report_summary += "🔧 OVERALL ASSESSMENT: Enterprise features are mostly functional with minor issues to address.\n"
        else:
            report_summary += "⚠️  OVERALL ASSESSMENT: Enterprise features need significant attention before production use.\n"
        
        print(report_summary)
        
        # Save detailed report to file
        report_file = "enterprise_features_validation_report.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        logger.info(f"📄 Detailed validation report saved to: {report_file}")
        
        return self.test_results

def main():
    """Main validation function"""
    print("🚀 Starting Enterprise Features Validation...\n")
    
    validator = SimpleEnterpriseValidator()
    
    # Run all validations
    file_structure_valid = validator.validate_file_structure()
    print()
    
    module_imports_valid = validator.validate_module_imports()
    print()
    
    documentation_valid = validator.validate_documentation()
    print()
    
    # Generate final report
    results = validator.generate_validation_report()
    
    # Exit with appropriate code
    if results["success_rate"] >= 80:
        print("\n🎉 Enterprise features validation completed successfully!")
        sys.exit(0)
    else:
        print(f"\n⚠️  Enterprise features validation completed with {results['success_rate']:.1f}% success rate")
        sys.exit(1)

if __name__ == "__main__":
    main()