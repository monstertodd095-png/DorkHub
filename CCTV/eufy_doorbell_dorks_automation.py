#!/usr/bin/env python3
"""
Eufy Doorbell Google Dorks Automation Script
Automates execution of security research queries for Eufy doorbell systems
Use only for authorized security testing and ethical hacking

Requirements:
    pip install selenium beautifulsoup4 requests
"""

import os
import sys
import time
import json
import csv
import argparse
import webbrowser
from datetime import datetime
from urllib.parse import quote
from typing import List, Dict
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options as ChromeOptions
except ImportError:
    print("⚠️  Selenium not installed. Install with: pip install selenium")
    sys.exit(1)


class EufyDorkAutomation:
    """Automate Google searches for Eufy doorbell security research"""

    GOOGLE_SEARCH_URL = "https://www.google.com/search"

    def __init__(self, headless: bool = False, delay: float = 2.0, timeout: int = 10):
        """
        Initialize the automation script
        
        Args:
            headless: Run browser in headless mode
            delay: Delay between requests in seconds
            timeout: Webdriver timeout in seconds
        """
        self.delay = delay
        self.timeout = timeout
        self.headless = headless
        self.results = []
        self.driver = None

    def init_driver(self) -> webdriver.Chrome:
        """Initialize Chrome WebDriver"""
        chrome_options = ChromeOptions()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(self.timeout)
            return self.driver
        except Exception as e:
            print(f"❌ Failed to initialize Chrome driver: {e}")
            print("   Make sure ChromeDriver is installed and in your PATH")
            sys.exit(1)

    def close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()

    def extract_dorks_from_file(self, filepath: str) -> Dict[str, List[str]]:
        """
        Extract Google dorks from the dorks file organized by category
        
        Args:
            filepath: Path to the dorks file
            
        Returns:
            Dictionary with categories as keys and dork lists as values
        """
        dorks = {}
        current_category = "General"
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                
                # Skip empty lines and comments that start with #
                if not line or line.startswith("#"):
                    # Detect category headers (lines with # and text ending with specific keywords)
                    if line.startswith("# ") and ("Search" in line or "Access" in line or "Queries" in line or "Logs" in line or "Endpoints" in line or "Information" in line or "Integration" in line or "Exposure" in line or "Endpoints" in line or "Enumeration" in line or "Archive" in line or "Combination" in line or "Specific" in line or "Protocol" in line or "Cloud" in line or "Configuration" in line or "Debugging" in line):
                        current_category = line.replace("# ", "").strip()
                        if current_category not in dorks:
                            dorks[current_category] = []
                    continue
                
                # Add dork to current category
                if current_category not in dorks:
                    dorks[current_category] = []
                dorks[current_category].append(line)
        
        except FileNotFoundError:
            print(f"❌ File not found: {filepath}")
            sys.exit(1)
        
        return dorks

    def search_query(self, query: str, open_browser: bool = False) -> Dict:
        """
        Execute a single Google search query
        
        Args:
            query: Google dork query to search
            open_browser: Open result in browser if True
            
        Returns:
            Dictionary with search metadata
        """
        try:
            search_url = f"{self.GOOGLE_SEARCH_URL}?q={quote(query)}"
            
            if open_browser:
                print(f"🌐 Opening in browser: {query}")
                webbrowser.open(search_url)
            else:
                print(f"🔍 Searching: {query}")
                self.driver.get(search_url)
                time.sleep(self.delay)
            
            result = {
                "query": query,
                "url": search_url,
                "timestamp": datetime.now().isoformat(),
                "status": "completed"
            }
            
            return result
        
        except Exception as e:
            print(f"❌ Error searching '{query}': {e}")
            return {
                "query": query,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "status": "failed"
            }

    def run_automated_search(self, dorks_file: str, category: str = None, 
                            limit: int = None, open_browser: bool = False) -> List[Dict]:
        """
        Run automated searches for all or selected dorks
        
        Args:
            dorks_file: Path to dorks file
            category: Specific category to search (None for all)
            limit: Maximum number of queries to execute
            open_browser: Open results in browser instead of using Selenium
            
        Returns:
            List of search results
        """
        dorks = self.extract_dorks_from_file(dorks_file)
        
        # Filter by category if specified
        if category:
            if category not in dorks:
                print(f"❌ Category '{category}' not found. Available: {list(dorks.keys())}")
                return []
            dorks = {category: dorks[category]}
        
        # Initialize driver only if not opening in browser
        if not open_browser:
            self.init_driver()
        
        total_queries = sum(len(queries) for queries in dorks.values())
        if limit:
            total_queries = min(total_queries, limit)
        
        print(f"\n📊 Starting automated Google dork searches")
        print(f"   Categories: {len(dorks)}")
        print(f"   Total queries to execute: {total_queries}\n")
        
        executed = 0
        
        try:
            for cat_name, queries in dorks.items():
                print(f"\n📁 Category: {cat_name} ({len(queries)} queries)")
                print("-" * 60)
                
                for i, query in enumerate(queries, 1):
                    if limit and executed >= limit:
                        break
                    
                    result = self.search_query(query, open_browser)
                    self.results.append(result)
                    executed += 1
                    
                    print(f"   [{executed}/{total_queries}] ✅ {result.get('status', 'unknown')}")
                    
                    if i < len(queries):
                        time.sleep(self.delay)
        
        except KeyboardInterrupt:
            print("\n⚠️  Search interrupted by user")
        
        finally:
            if not open_browser:
                self.close_driver()
        
        print(f"\n✅ Completed {executed} searches")
        return self.results

    def save_results(self, output_file: str, format: str = "json"):
        """
        Save search results to file
        
        Args:
            output_file: Output file path
            format: Output format ('json' or 'csv')
        """
        if not self.results:
            print("⚠️  No results to save")
            return
        
        try:
            if format.lower() == "json":
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            elif format.lower() == "csv":
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=self.results[0].keys())
                    writer.writeheader()
                    writer.writerows(self.results)
            
            print(f"💾 Results saved to: {output_file}")
        
        except Exception as e:
            print(f"❌ Error saving results: {e}")

    def generate_report(self, output_file: str):
        """Generate a detailed search report"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("=" * 70 + "\n")
                f.write("EUFY DOORBELL GOOGLE DORKS - SEARCH REPORT\n")
                f.write("=" * 70 + "\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Searches: {len(self.results)}\n")
                f.write(f"Successful: {sum(1 for r in self.results if r.get('status') == 'completed')}\n")
                f.write(f"Failed: {sum(1 for r in self.results if r.get('status') == 'failed')}\n\n")
                
                f.write("-" * 70 + "\n")
                f.write("SEARCH DETAILS\n")
                f.write("-" * 70 + "\n\n")
                
                for i, result in enumerate(self.results, 1):
                    f.write(f"[{i}] Query: {result['query']}\n")
                    f.write(f"    Status: {result.get('status', 'unknown')}\n")
                    f.write(f"    URL: {result.get('url', 'N/A')}\n")
                    if result.get('error'):
                        f.write(f"    Error: {result['error']}\n")
                    f.write(f"    Timestamp: {result.get('timestamp', 'N/A')}\n\n")
            
            print(f"📄 Report saved to: {output_file}")
        
        except Exception as e:
            print(f"❌ Error generating report: {e}")


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="Automate Eufy doorbell Google dorks security research",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all searches
  python eufy_doorbell_dorks_automation.py

  # Run specific category
  python eufy_doorbell_dorks_automation.py --category "API Endpoints & Backend"

  # Open in browser instead of automated
  python eufy_doorbell_dorks_automation.py --browser

  # Limit to 10 queries
  python eufy_doorbell_dorks_automation.py --limit 10

  # Save results as CSV
  python eufy_doorbell_dorks_automation.py --output results.csv --format csv
        """
    )
    
    parser.add_argument(
        "dorks_file",
        nargs="?",
        default="eufy-doorbell-dorks.txt",
        help="Path to dorks file (default: eufy-doorbell-dorks.txt)"
    )
    parser.add_argument(
        "--category",
        help="Specific category to search"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Maximum number of queries to execute"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="Delay between requests in seconds (default: 2.0)"
    )
    parser.add_argument(
        "--browser",
        action="store_true",
        help="Open results in browser instead of automated Selenium"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode"
    )
    parser.add_argument(
        "--output",
        help="Output file for results"
    )
    parser.add_argument(
        "--format",
        choices=["json", "csv"],
        default="json",
        help="Output format (default: json)"
    )
    parser.add_argument(
        "--report",
        help="Generate detailed report file"
    )
    
    args = parser.parse_args()
    
    # Verify dorks file exists
    if not Path(args.dorks_file).exists():
        print(f"❌ Dorks file not found: {args.dorks_file}")
        sys.exit(1)
    
    # Initialize automation
    automation = EufyDorkAutomation(
        headless=args.headless,
        delay=args.delay
    )
    
    # Run searches
    automation.run_automated_search(
        dorks_file=args.dorks_file,
        category=args.category,
        limit=args.limit,
        open_browser=args.browser
    )
    
    # Save results
    if args.output:
        automation.save_results(args.output, format=args.format)
    
    # Generate report
    if args.report:
        automation.generate_report(args.report)


if __name__ == "__main__":
    main()
