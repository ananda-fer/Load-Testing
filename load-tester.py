#!/usr/bin/env python3

import os
import sys
import time
import requests
import concurrent.futures
from datetime import datetime

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

class ClearLoadTester:
    def __init__(self):
        self.target_url = ""
        self.concurrent_users = 50
        self.duration = 30
        self.results = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'start_time': None,
            'end_time': None
        }
    
    def show_header(self):
        print("""
╔══════════════════════════════════════╗
║                                      ║
║       🚀 LOAD TESTING TOOL           ║
║                                      ║
╚══════════════════════════════════════╝
""")
    
    def get_input(self, prompt, default=""):
        """Dapatkan input dari user"""
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            return user_input if user_input else default
        else:
            return input(f"{prompt}: ").strip()
    
    def collect_inputs(self):
        """Kumpulkan semua input dari user"""
        clear_screen()
        self.show_header()
        
        print("📝 MASUKKAN DETAIL TESTING")
        print("="*40)
        
        # Input target URL
        self.target_url = self.get_input("Target URL (website Anda)", "http://localhost:3000")
        if not self.target_url.startswith('http'):
            self.target_url = 'http://' + self.target_url
        
        # Input concurrent users
        while True:
            try:
                users_input = self.get_input("Jumlah concurrent users", "50")
                self.concurrent_users = int(users_input)
                if 1 <= self.concurrent_users <= 500:
                    break
                else:
                    print("[!] Masukkan angka 1-500")
            except ValueError:
                print("[!] Masukkan angka yang valid")
        
        # Input duration
        while True:
            try:
                dur_input = self.get_input("Durasi testing (detik)", "30")
                self.duration = int(dur_input)
                if 1 <= self.duration <= 600:
                    break
                else:
                    print("[!] Masukkan 1-600 detik")
            except ValueError:
                print("[!] Masukkan angka yang valid")
        
        # Konfirmasi
        clear_screen()
        self.show_header()
        print("🔍 KONFIRMASI SETTINGS")
        print("="*40)
        print(f"🎯 Target: {self.target_url}")
        print(f"👥 Concurrent Users: {self.concurrent_users}")
        print(f"⏱️  Duration: {self.duration} detik")
        print(f"📊 Est. Requests: {self.concurrent_users * self.duration:,}")
        print("="*40)
        
        confirm = input("\n[?] Mulai testing? (Y/n): ").strip().lower()
        return confirm in ['y', 'yes', '']
    
    def make_request(self, worker_id):
        """Buat request ke target"""
        try:
            headers = {
                'User-Agent': f'LoadTestBot/{worker_id}',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            
            response = requests.get(
                self.target_url,
                headers=headers,
                timeout=5,
                allow_redirects=True
            )
            
            return {
                'success': response.status_code < 400,
                'status': response.status_code,
                'worker': worker_id
            }
            
        except Exception:
            return {'success': False, 'status': 0, 'worker': worker_id}
    
    def update_display(self, elapsed, total_time):
        """Update display dengan progress"""
        clear_screen()
        
        # Progress bar
        progress = min(elapsed / total_time, 1.0)
        bar_width = 40
        filled = int(bar_width * progress)
        bar = '█' * filled + '░' * (bar_width - filled)
        
        # Hitung metrics
        total = self.results['total']
        success = self.results['success']
        failed = self.results['failed']
        rps = total / (elapsed + 0.001)
        
        if total > 0:
            success_rate = (success / total) * 100
        else:
            success_rate = 0
        
        print(f"""
╔══════════════════════════════════════╗
║      🚀 LOAD TESTING - LIVE         ║
╚══════════════════════════════════════╝

🎯 Target: {self.target_url[:40]:<40}
⏱️  Progress: [{bar}] {progress*100:.1f}%
📊 Status: {int(elapsed)}s / {total_time}s

📈 PERFORMANCE METRICS:
├─ 📊 Total Requests: {total:,}
├─ ✅ Successful: {success:,}
├─ ❌ Failed: {failed:,}
├─ 📈 Success Rate: {success_rate:.1f}%
├─ ⚡ RPS: {rps:.1f}/detik
└─ 👥 Active Workers: {self.concurrent_users}

{'='*40}
💡 Tekan Ctrl+C untuk menghentikan...
        """)
    
    def run_test(self):
        """Jalankan load testing"""
        self.results['start_time'] = time.time()
        stop_test = False
        
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.concurrent_users) as executor:
                # Submit initial batch of workers
                futures = []
                for i in range(self.concurrent_users):
                    future = executor.submit(self.make_request, i)
                    futures.append(future)
                
                # Main loop
                start_time = time.time()
                last_display_update = 0
                
                while not stop_test and (time.time() - start_time) < self.duration:
                    current_time = time.time()
                    elapsed = current_time - start_time
                    
                    # Update display setiap 0.5 detik
                    if current_time - last_display_update > 0.5:
                        self.update_display(elapsed, self.duration)
                        last_display_update = current_time
                    
                    # Process completed futures
                    done_futures = [f for f in futures if f.done()]
                    
                    for future in done_futures:
                        try:
                            result = future.result()
                            self.results['total'] += 1
                            
                            if result['success']:
                                self.results['success'] += 1
                            else:
                                self.results['failed'] += 1
                            
                            # Submit new request untuk worker yang sama
                            if not stop_test:
                                new_future = executor.submit(self.make_request, result['worker'])
                                futures.append(new_future)
                                
                        except Exception:
                            self.results['failed'] += 1
                            self.results['total'] += 1
                        
                        # Remove processed future
                        futures.remove(future)
                    
                    time.sleep(0.01)  # Small delay to prevent CPU overload
                
                # Wait for remaining futures
                stop_test = True
                for future in futures:
                    try:
                        future.result(timeout=1)
                    except:
                        pass
        
        except KeyboardInterrupt:
            print("\n\n[!] Testing dihentikan oleh user")
        
        finally:
            self.results['end_time'] = time.time()
            self.show_results()
    
    def show_results(self):
        """Tampilkan hasil akhir"""
        clear_screen()
        
        total_time = self.results['end_time'] - self.results['start_time']
        total = self.results['total']
        success = self.results['success']
        failed = self.results['failed']
        
        if total > 0:
            success_rate = (success / total) * 100
            rps = total / total_time
        else:
            success_rate = 0
            rps = 0
        
        print(f"""
╔══════════════════════════════════════╗
║         📊 HASIL TESTING            ║
╚══════════════════════════════════════╝

🎯 Target: {self.target_url}
⏱️  Durasi: {total_time:.2f} detik
👥 Concurrent Users: {self.concurrent_users}

{'='*40}

📈 METRIK KINERJA:
├─ 📊 Total Requests: {total:,}
├─ ✅ Successful: {success:,}
├─ ❌ Failed: {failed:,}
├─ 📈 Success Rate: {success_rate:.1f}%
├─ ⚡ Average RPS: {rps:.1f}/detik
└─ 🎯 Target Duration: {self.duration}s

{'='*40}

💡 ANALISIS:
""")
        
        if success_rate > 95 and rps > 50:
            print("✅ Website sangat stabil dan responsif")
            print("   Dapat menangani beban tinggi dengan baik")
        elif success_rate > 80:
            print("⚠️  Website cukup stabil")
            print("   Pertimbangkan optimasi untuk beban lebih tinggi")
        else:
            print("❌ Website mengalami kesulitan")
            print("   Perlu optimasi server dan aplikasi")
        
        print(f"\n🕒 Selesai: {datetime.now().strftime('%H:%M:%S')}")
        print("="*40)
        
        # Tanya apakah mau test lagi
        retry = input("\n[?] Test lagi dengan setting berbeda? (y/N): ").strip().lower()
        if retry == 'y':
            self.__init__()  # Reset object
            if self.collect_inputs():
                self.run_test()

def main():
    """Fungsi utama"""
    try:
        tester = ClearLoadTester()
        
        if tester.collect_inputs():
            tester.run_test()
        else:
            clear_screen()
            print("\n[!] Testing dibatalkan\n")
    
    except KeyboardInterrupt:
        clear_screen()
        print("\n[!] Program dihentikan\n")
    
    except Exception as e:
        clear_screen()
        print(f"\n[!] Error: {e}\n")

if __name__ == "__main__":
    # Clear screen saat mulai
    os.system('clear' if os.name == 'posix' else 'cls')
    main()
