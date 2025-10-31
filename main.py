import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass, field
from typing import List, Dict
from copy import deepcopy 

@dataclass
class Surec:
    pid: str
    varis: int
    patlama: int
    kalan: int = field(init=False)
    baslama_zamani: int = field(default=-1)
    bitis_zamani: int = field(default=-1)

    def __post_init__(self):
        self.kalan = self.patlama


def fcfs(surecler: List[Surec]) -> Dict[str, Surec]:
    sirali = sorted(surecler, key=lambda s: (s.varis, s.pid))
    zaman = 0
    for s in sirali:
        if zaman < s.varis:
            zaman = s.varis
        s.baslama_zamani = zaman
        zaman += s.patlama
        s.bitis_zamani = zaman
    return {s.pid: s for s in sirali}

def sjf(surecler: List[Surec]) -> Dict[str, Surec]:
    
    zaman = 0
    kalan_surecler = deepcopy(surecler)
    bitenler = []
    while kalan_surecler:
        hazir = [s for s in kalan_surecler if s.varis <= zaman]
        if not hazir:
            zaman = min(s.varis for s in kalan_surecler)
            continue
        secilen = min(hazir, key=lambda s: s.patlama)
        secilen.baslama_zamani = zaman
        zaman += secilen.patlama
        secilen.bitis_zamani = zaman
        bitenler.append(secilen)
        kalan_surecler.remove(secilen)
    return {s.pid: s for s in bitenler}

def srtf(surecler: List[Surec]) -> Dict[str, Surec]:
    zaman = 0
    kalan_surecler = deepcopy(surecler)
    bitenler = []
    while kalan_surecler:
        hazir = [s for s in kalan_surecler if s.varis <= zaman and s.kalan > 0]
        if not hazir:
            zaman += 1
            continue
        secilen = min(hazir, key=lambda s: s.kalan)
        if secilen.baslama_zamani == -1:
            secilen.baslama_zamani = zaman
        secilen.kalan -= 1
        zaman += 1
        if secilen.kalan == 0:
            secilen.bitis_zamani = zaman
            bitenler.append(secilen)
            kalan_surecler.remove(secilen)
    return {s.pid: s for s in bitenler}

def round_robin(surecler: List[Surec], quantum: int) -> Dict[str, Surec]:
    zaman = 0
    kuyruk = []
    kalan_surecler = deepcopy(surecler)
    bitenler = []
    while kalan_surecler or kuyruk:
        for s in list(kalan_surecler):
            if s.varis <= zaman and s not in kuyruk and s.kalan > 0:
                kuyruk.append(s)
        if not kuyruk:
           
            nxt = min([s.varis for s in kalan_surecler if s.kalan > 0], default=None)
            if nxt is None:
                break
            zaman = max(zaman, nxt)
            continue
        aktif = kuyruk.pop(0)
        if aktif.baslama_zamani == -1:
            aktif.baslama_zamani = zaman
        calisma = min(quantum, aktif.kalan)
        aktif.kalan -= calisma
        zaman += calisma
        
        for s in list(kalan_surecler):
            if s.varis <= zaman and s not in kuyruk and s.kalan > 0 and s is not aktif:
                kuyruk.append(s)
        if aktif.kalan == 0:
            aktif.bitis_zamani = zaman
            bitenler.append(aktif)
            if aktif in kalan_surecler:
                kalan_surecler.remove(aktif)
        else:
            kuyruk.append(aktif)
    return {s.pid: s for s in bitenler}

def hrrn(surecler: List[Surec]) -> Dict[str, Surec]:
    
    zaman = 0
    kalan_surecler = deepcopy(surecler)
    bitenler = []
    while kalan_surecler:
        hazir = [s for s in kalan_surecler if s.varis <= zaman]
        if not hazir:
            zaman = min(s.varis for s in kalan_surecler)
            continue
       
        secilen = max(hazir, key=lambda s: ((zaman - s.varis + s.patlama) / s.patlama))
        secilen.baslama_zamani = zaman
        zaman += secilen.patlama
        secilen.bitis_zamani = zaman
        bitenler.append(secilen)
        kalan_surecler.remove(secilen)
    return {s.pid: s for s in bitenler}

def aging(surecler: List[Surec], factor: float = 1.0) -> Dict[str, Surec]:
    
    zaman = 0
    kalan_surecler = deepcopy(surecler)
    bitenler = []
    while kalan_surecler:
        hazir = [s for s in kalan_surecler if s.varis <= zaman]
        if not hazir:
            zaman = min(s.varis for s in kalan_surecler)
            continue
        eff_list = []
        for s in hazir:
            waiting = max(0, zaman - s.varis)
            eff = max(0.1, s.patlama - factor * waiting)  
            eff_list.append((eff, s))
        secilen = min(eff_list, key=lambda x: x[0])[1]
        secilen.baslama_zamani = zaman
        zaman += secilen.patlama
        secilen.bitis_zamani = zaman
        bitenler.append(secilen)
        kalan_surecler.remove(secilen)
    return {s.pid: s for s in bitenler}

def metrik_hesapla(sozluk: Dict[str, Surec]) -> str:
    sonuc = ""
    toplam_bekleme = 0
    toplam_donus = 0
    n = len(sozluk)
    for s in sozluk.values():
        donus = s.bitis_zamani - s.varis
        bekleme = donus - s.patlama
        sonuc += f"Süreç {s.pid}: Bekleme={bekleme}, Dönüş={donus}\n"
        toplam_bekleme += bekleme
        toplam_donus += donus
    ort_bekleme = toplam_bekleme / n if n else 0
    ort_donus = toplam_donus / n if n else 0
    sonuc += f"\nOrtalama Bekleme Süresi: {ort_bekleme:.2f}\nOrtalama Dönüş Süresi: {ort_donus:.2f}"
    return sonuc


class PlanlamaArayuzu:
    def __init__(self, pencere):
        self.pencere = pencere
        pencere.title("CPU Planlama Metinsel Simülatör")

        sol = ttk.Frame(pencere, padding=10)
        sol.grid(row=0, column=0, sticky="ns")

        ttk.Label(sol, text="Süreç ID:").grid(row=0, column=0, sticky="w")
        self.pid = ttk.Entry(sol, width=10)
        self.pid.grid(row=0, column=1, pady=2)

        ttk.Label(sol, text="Varış Zamanı:").grid(row=1, column=0, sticky="w")
        self.varis = ttk.Entry(sol, width=10)
        self.varis.grid(row=1, column=1, pady=2)

        ttk.Label(sol, text="Patlama Süresi:").grid(row=2, column=0, sticky="w")
        self.patlama = ttk.Entry(sol, width=10)
        self.patlama.grid(row=2, column=1, pady=2)

        ttk.Button(sol, text="Süreç Ekle", command=self.surec_ekle).grid(row=3, column=0, columnspan=2, pady=6)
        ttk.Separator(sol, orient="horizontal").grid(row=4, column=0, columnspan=2, sticky="ew", pady=6)

        ttk.Label(sol, text="Algoritma:").grid(row=5, column=0, sticky="w")
        self.algo = tk.StringVar(value="FCFS")
        ttk.Combobox(sol, values=["FCFS", "SJF", "SRTF", "RR", "SPN", "HRRN", "AGING"], textvariable=self.algo, state="readonly").grid(row=5, column=1)

        ttk.Label(sol, text="Zaman Dilimi (RR):").grid(row=6, column=0, sticky="w")
        self.quantum = ttk.Entry(sol, width=10)
        self.quantum.insert(0, "2")
        self.quantum.grid(row=6, column=1)

        ttk.Label(sol, text="Aging Faktörü:").grid(row=7, column=0, sticky="w")
        self.aging_factor = ttk.Entry(sol, width=10)
        self.aging_factor.insert(0, "1.0")
        self.aging_factor.grid(row=7, column=1)

        ttk.Button(sol, text="Simülasyonu Başlat", command=self.simulasyon_baslat).grid(row=8, column=0, columnspan=2, pady=8)
        ttk.Button(sol, text="Temizle", command=self.temizle).grid(row=9, column=0, columnspan=2)

        ttk.Label(sol, text="Eklenen Süreçler:").grid(row=10, column=0, sticky="w", pady=(8, 0))
        self.liste = tk.Listbox(sol, width=30, height=10)
        self.liste.grid(row=11, column=0, columnspan=2, pady=4)

        ttk.Label(sol, text="Sonuçlar:").grid(row=12, column=0, sticky="w", pady=(8,0))
        self.sonuc_text = tk.Text(sol, width=50, height=15)
        self.sonuc_text.grid(row=13, column=0, columnspan=2, pady=4)

        self.surecler: List[Surec] = []

    def surec_ekle(self):
        pid = self.pid.get().strip()
        varis = self.varis.get().strip()
        patlama = self.patlama.get().strip()

        if not pid or not varis.isdigit() or not patlama.isdigit():
            messagebox.showerror("Hata", "Geçerli bir PID, varış ve patlama süresi girin.")
            return

        if any(s.pid == pid for s in self.surecler):
            messagebox.showerror("Hata", "Bu PID zaten eklenmiş.")
            return

        s = Surec(pid, int(varis), int(patlama))
        self.surecler.append(s)
        self.liste.insert(tk.END, f"{pid} | Varış: {varis} | Patlama: {patlama}")

        self.pid.delete(0, tk.END)
        self.varis.delete(0, tk.END)
        self.patlama.delete(0, tk.END)

    def temizle(self):
        self.surecler.clear()
        self.liste.delete(0, tk.END)
        self.sonuc_text.delete(1.0, tk.END)

    def gantt_ciz(self, sozluk: Dict[str, Surec]):
        top = tk.Toplevel(self.pencere)
        top.title("Gantt Grafiği")
        canvas_width = 700
        canvas_height = 50 + 30*len(sozluk)
        canvas = tk.Canvas(top, width=canvas_width, height=canvas_height, bg="white")
        canvas.pack()

        renkler = ["#FF9999","#99FF99","#9999FF","#FFFF99","#FF99FF","#99FFFF","#FFCC99","#CCFF99"]

        max_zaman = max(s.bitis_zamani for s in sozluk.values())
        if max_zaman == 0:
            max_zaman = 1
        scale = (canvas_width - 80) / max_zaman

        for i, s in enumerate(sozluk.values()):
            x1 = 50 + s.baslama_zamani * scale
            x2 = 50 + s.bitis_zamani * scale
            y1 = 20 + i*30
            y2 = 50 + i*30
            color = renkler[i % len(renkler)]
            canvas.create_rectangle(x1, y1, x2, y2, fill=color)
            canvas.create_text((x1+x2)/2, (y1+y2)/2, text=s.pid)

        for t in range(max_zaman+1):
            x = 50 + t*scale
            canvas.create_line(x, 15, x, canvas_height-5, fill="#CCCCCC")
            canvas.create_text(x, 10, text=str(t))

    def simulasyon_baslat(self):
        if not self.surecler:
            messagebox.showwarning("Uyarı", "Önce süreç ekleyin.")
            return

        
        kopya = deepcopy(self.surecler)
        for s in kopya:
            s.kalan = s.patlama
            s.baslama_zamani = -1
            s.bitis_zamani = -1

        algo = self.algo.get()

        try:
            if algo == "FCFS":
                sozluk = fcfs(kopya)
            elif algo == "SJF" or algo == "SPN":
                sozluk = sjf(kopya)
            elif algo == "SRTF":
                sozluk = srtf(kopya)
            elif algo == "RR":
                q = self.quantum.get().strip()
                if not q.isdigit() or int(q) <= 0:
                    messagebox.showerror("Hata", "Geçerli bir zaman dilimi girin.")
                    return
                sozluk = round_robin(kopya, int(q))
            elif algo == "HRRN":
                sozluk = hrrn(kopya)
            elif algo == "AGING":
                try:
                    factor = float(self.aging_factor.get().strip())
                except ValueError:
                    messagebox.showerror("Hata", "Aging faktörü float olmalıdır (ör: 1.0).")
                    return
                sozluk = aging(kopya, factor)
            else:
                messagebox.showerror("Hata", "Algoritma bulunamadı.")
                return
        except Exception as e:
            messagebox.showerror("Hata", f"Simülasyon sırasında hata oluştu:\n{e}")
            return

        sonuc = metrik_hesapla(sozluk)
        self.sonuc_text.delete(1.0, tk.END)
        self.sonuc_text.insert(tk.END, sonuc)
        self.gantt_ciz(sozluk)

def main():
    pencere = tk.Tk()
    app = PlanlamaArayuzu(pencere)
    pencere.mainloop()

if __name__ == "__main__":
    main()
