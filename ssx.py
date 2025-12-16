#!/usr/bin/env python3
"""
xss_tester.py - XSS Vulnerability Scanner untuk website sendiri
Hanya untuk testing dengan izin!
"""

import requests
from urllib.parse import quote

class XSSTester:
    def __init__(self, target_url):
        self.target = target_url
        self.vulnerable_params = []
        
        # Payload XSS untuk testing
        self.payloads = [
            '<script>alert("XSS")</script>',
            '<img src=x onerror=alert("XSS")>',
            '" onmouseover="alert(\'XSS\')',
            'javascript:alert("XSS")',
            '<svg onload=alert("XSS")>',
            '<body onload=alert("XSS")>'
        ]
    
    def test_form(self, form_url, params):
        """Test form input untuk XSS"""
        print(f"\n[+] Testing form: {form_url}")
        
        for param_name, param_value in params.items():
            for payload in self.payloads:
                # Ganti value dengan payload
                test_params = params.copy()
                test_params[param_name] = payload
                
                try:
                    response = requests.post(
                        form_url, 
                        data=test_params,
                        timeout=10
                    )
                    
                    # Cek jika payload ada di response
                    if payload.replace('<', '&lt;') not in response.text:
                        print(f"  [!] Potensi XSS di parameter: {param_name}")
                        print(f"      Payload: {payload[:50]}...")
                        self.vulnerable_params.append({
                            'url': form_url,
                            'parameter': param_name,
                            'payload': payload
                        })
                        
                except Exception as e:
                    print(f"  [-] Error: {e}")
    
    def test_url_params(self):
        """Test URL parameters untuk XSS"""
        print("\n[+] Testing URL parameters...")
        
        base_url = self.target.split('?')[0]
        
        # Jika ada query parameters
        if '?' in self.target:
            query_string = self.target.split('?')[1]
            params = dict(p.split('=') for p in query_string.split('&'))
            
            for param_name in params.keys():
                for payload in self.payloads:
                    test_url = f"{base_url}?{param_name}={quote(payload)}"
                    
                    try:
                        response = requests.get(test_url, timeout=10)
                        
                        if payload in response.text:
                            print(f"  [!] Potensi XSS di URL param: {param_name}")
                            self.vulnerable_params.append({
                                'url': test_url,
                                'parameter': param_name,
                                'payload': payload
                            })
                            
                    except Exception as e:
                        print(f"  [-] Error testing {param_name}: {e}")
    
    def generate_report(self):
        """Generate laporan testing"""
        print("\n" + "="*50)
        print("XSS TESTING REPORT")
        print("="*50)
        
        if self.vulnerable_params:
            print(f"\n[!] Ditemukan {len(self.vulnerable_params)} potensi kerentanan:")
            for vuln in self.vulnerable_params:
                print(f"\n  URL: {vuln['url']}")
                print(f"  Parameter: {vuln['parameter']}")
                print(f"  Payload: {vuln['payload']}")
        else:
            print("\n[✓] Tidak ditemukan kerentanan XSS (basic test)")
        
        print("\n[!] Rekomendasi:")
        print("  1. Gunakan output encoding (HTML Entity)")
        print("  2. Implementasi Content Security Policy (CSP)")
        print("  3. Validasi input user")
        print("  4. Gunakan library/framework yang aman")

# Contoh penggunaan
if __name__ == "__main__":
    print("=== XSS VULNERABILITY TESTER ===")
    print("Hanya untuk testing website sendiri!\n")
    
    target = input("Masukkan URL website Anda: ")
    
    if not target.startswith('http'):
        target = 'http://' + target
    
    print(f"\n[+] Testing: {target}")
    print("[+] Hanya test basic XSS payloads")
    
    tester = XSSTester(target)
    
    # Test URL parameters
    tester.test_url_params()
    
    print("\n[+] Testing selesai!")
    tester.generate_report()
