#!/usr/bin/env python3
"""
Load Testing Tool untuk Termux
Versi Ringan untuk Android
"""

import requests
import concurrent.futures
import time
import sys
import os

class TermuxLoadTester:
    def __init__(self, target, threads=10, duration=30):
        self.target = target
        self.threads = min(threads, 20)  # Batasi untuk Termux
        self.duration = duration
        self.total_requests = 0
        self.success = 0
        self.failed = 0
        self.active = False
        
        # User-Agent untuk Termux
        self.headers = {
            'User-Agent': 'Termux-LoadTest/1.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
    
    def clear_screen(self):
        """Clear terminal screen untuk Termux"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def show_banner(self):
        """Tampilkan banner"""
        self.clear_screen()
        print("""
╔══════════════════════════════════════╗
║    TERMUX LOAD TESTING TOOL v1.0     ║
║              Testing Website         ║
╚══════════════════════════════════════╝
        """)
    
    def make_request(self):
        """Single request dengan timeout pendek"""
        try:
            response = requests.get(
                self.target, 
                headers=self.headers,
                timeout=5,
                verify=False  # Nonaktifkan SSL verify untuk testing lokal
            )
            return response.status_code == 200
        except:
            return False
    
    def worker(self, worker_id):
        """Worker untuk membuat requests"""
        local_count = 0
        while self.active:
            if self.make_request():
                self.success += 1
            else:
                self.failed += 1
            
            self.total_requests += 1
            local_count += 1
            
            # Beri jeda kecil untuk mencegah overload
            if local_count % 10 == 0:
                time.sleep(0.1)
    
    def run(self):
        """Jalankan testing"""
        self.show_banner()
        
        print(f"[📱] Target: {self.target}")
        print(f"[⚡] Threads: {self.threads}")
        print(f"[⏱️] Durasi: {self.duration} detik")
        print(f"[📊] Mode: Termux (Android)")
        print("\n" + "="*40)
        
        # Konfirmasi
        print("\n[⚠️] PERINGATAN:")
        print("1. Hanya untuk website MILIK ANDA")
        print("2. Jangan gunakan untuk tujuan ilegal")
        
        confirm = input("\n[?] Lanjutkan? (y/n): ").lower()
        if confirm != 'y':
            print("[✖] Dibatalkan!")
            return
        
        print("\n[🚀] Memulai load testing...")
        print("[ℹ️] Tekan Ctrl+C untuk berhenti\n")
        
        self.active = True
        start_time = time.time()
        
        try:
            # Buat thread pool
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
                # Submit semua workers
                futures = [executor.submit(self.worker, i) for i in range(self.threads)]
                
                # Monitor progress
                while time.time() - start_time < self.duration:
                    elapsed = time.time() - start_time
                    remaining = self.duration - elapsed
                    
                    # Update display setiap 2 detik
                    if int(elapsed) % 2 == 0:
                        self.update_display(elapsed, remaining)
                    
                    time.sleep(1)
                
                # Stop semua workers
                self.active = False
                
                # Tunggu semua thread selesai
                concurrent.futures.wait(futures, timeout=5)
        
        except KeyboardInterrupt:
            print("\n\n[⚠️] Dihentikan oleh user!")
            self.active = False
        
        finally:
            total_time = time.time() - start_time
            self.show_results(total_time)
    
    def update_display(self, elapsed, remaining):
        """Update display status"""
        rps = self.total_requests / (elapsed + 0.001)
        
        print("\033[H\033[J")  # Clear screen untuk update
        print(f"""
╔══════════════════════════════════════╗
║        LIVE TESTING STATUS           ║
╠══════════════════════════════════════╣
║  🎯 Target: {self.target[:30]:<10}
║  ⏱️  Waktu: {int(elapsed)}s / {self.duration}s
║  ⏳ Sisa: {int(remaining)} detik
╠══════════════════════════════════════╣
║  📊 Total Requests: {self.total_requests}
║  ✅ Success: {self.success}
║  ❌ Failed: {self.failed}
║  ⚡ RPS: {rps:.2f}/detik
║  📈 Success Rate: {(self.success/(self.total_requests+0.001)*100):.1f}%
╚══════════════════════════════════════╝
        """)
    
    def show_results(self, total_time):
        """Tampilkan hasil akhir"""
        self.clear_screen()
        
        print("""
╔══════════════════════════════════════╗
║          HASIL TESTING               ║
╠══════════════════════════════════════╣
        """)
        
        print(f"║  🎯 Target: {self.target}")
        print(f"║  ⏱️  Durasi: {total_time:.2f} detik")
        print(f"║  👥 Threads: {self.threads}")
        print(f"╠══════════════════════════════════════╣")
        print(f"║  📊 Total Requests: {self.total_requests}")
        print(f"║  ✅ Requests Berhasil: {self.success}")
        print(f"║  ❌ Requests Gagal: {self.failed}")
        print(f"║  ⚡ Rata-rata RPS: {(self.total_requests/total_time):.2f}")
        
        if self.total_requests > 0:
            success_rate = (self.success / self.total_requests) * 100
            print(f"║  📈 Success Rate: {success_rate:.2f}%")
        
        print(f"╠══════════════════════════════════════╣")
        print(f"║  💡 Rekomendasi:")
        
        if self.success_rate > 95:
            print(f"║  Website stabil, bisa handle load")
        elif self.success_rate > 80:
            print(f"║  Website cukup stabil")
        else:
            print(f"║  Website mungkin butuh optimasi")
        
        print(f"╚══════════════════════════════════════╝")
        
        # Simpan log
        self.save_log(total_time)
    
    def save_log(self, total_time):
        """Simpan hasil ke file log"""
        try:
            log_file = "termux_loadtest.log"
            with open(log_file, "a") as f:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"\n{'='*50}\n")
                f.write(f"Test Time: {timestamp}\n")
                f.write(f"Target: {self.target}\n")
                f.write(f"Duration: {total_time:.2f}s\n")
                f.write(f"Threads: {self.threads}\n")
                f.write(f"Total Requests: {self.total_requests}\n")
                f.write(f"Success: {self.success}\n")
                f.write(f"Failed: {self.failed}\n")
                f.write(f"RPS: {(self.total_requests/total_time):.2f}\n")
            
            print(f"\n[💾] Log disimpan di: {log_file}")
        except:
            pass

def main():
    """Main function dengan menu interaktif"""
    
    os.system('clear')
    print("""
╔══════════════════════════════════════╗
║    TERMUX LOAD TESTER - MENU UTAMA   ║
╚══════════════════════════════════════╝
    """)
    
    # Input target
    target = input("[?] Masukkan URL target (ex: http://localhost:8080): ").strip()
    
    if not target:
        print("[✖] URL tidak boleh kosong!")
        return
    
    # Tambahkan http:// jika tidak ada
    if not target.startswith('http'):
        target = 'http://' + target
    
    # Pilihan threads
    print("\n[⚡] Pilih jumlah threads:")
    print("  1) Ringan (5 threads)")
    print("  2) Medium (10 threads)")
    print("  3) Berat (15 threads)")
    print("  4) Custom")
    
    choice = input("\n[?] Pilihan (1-4): ").strip()
    
    if choice == '1':
        threads = 5
    elif choice == '2':
        threads = 10
    elif choice == '3':
        threads = 15
    elif choice == '4':
        try:
            threads = int(input("[?] Jumlah threads (max 20): "))
            threads = min(threads, 20)  # Batasi untuk Termux
        except:
            print("[✖] Input tidak valid, menggunakan default 10")
            threads = 10
    else:
        threads = 10
    
    # Durasi
    try:
        duration = int(input("[?] Durasi testing (detik, max 120): "))
        duration = min(duration, 120)  # Batasi durasi
    except:
        duration = 30
    
    # Jalankan tester
    tester = TermuxLoadTester(target, threads, duration)
    tester.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[✖] Program dihentikan")
    except Exception as e:
        print(f"\n[❌] Error: {e}")
