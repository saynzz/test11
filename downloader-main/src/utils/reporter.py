import os
import time
import json

class Reporter:
    def save_report(self, results):
        """Сохраняет отчет о загрузках"""
        try:
            report_dir = os.path.join(os.getcwd(), "reports")
            if not os.path.exists(report_dir):
                os.makedirs(report_dir)
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            report_file = os.path.join(report_dir, f"report_{timestamp}.txt")
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("=== VIDEO DOWNLOAD REPORT ===\n")
                f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n\n")
                
                success_count = sum(1 for r in results.values() if r.get('status') == 'success')
                total_count = len(results)
                
                f.write(f"Total downloads: {total_count}\n")
                f.write(f"Successful: {success_count}\n")
                f.write(f"Failed: {total_count - success_count}\n\n")
                
                f.write("DETAILS:\n")
                f.write("=" * 50 + "\n")
                
                for url, result in results.items():
                    f.write(f"URL: {url}\n")
                    if result.get('status') == 'success':
                        f.write(f"Status: ✅ SUCCESS\n")
                        f.write(f"Title: {result.get('title', 'Unknown')}\n")
                        f.write(f"File: {result.get('path', 'Unknown')}\n")
                    else:
                        f.write(f"Status: ❌ ERROR\n")
                        f.write(f"Error: {result.get('message', 'Unknown error')}\n")
                    f.write("-" * 50 + "\n")
            
            return True
        except Exception as e:
            print(f"Error saving report: {e}")
            return False