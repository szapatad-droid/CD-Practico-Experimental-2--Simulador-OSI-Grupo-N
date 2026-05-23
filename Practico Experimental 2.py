import tkinter as tk
from tkinter import messagebox, ttk
import random, base64, math

# ─────────────────────────────────────────────
# TEMAS: generados desde paletas base
# ─────────────────────────────────────────────
def _tema(bg, titulo, subtitulo, nota_bg, nota_fg, canal_bg, ca_fg, cb_fg,
          nodo_idle, nodo_active, done_a, done_b, btn_send, btn_reset, btn_fg,
          stats_bg, stats_fg, seq_capa="#00ffcc", seq_ok="#00ff88", seq_err="#ff4444"):
    return dict(
        bg=bg, fg_titulo=titulo, fg_subtitulo=subtitulo,
        nota_bg=nota_bg, nota_fg=nota_fg,
        canal_bg=canal_bg, canal_fg=cb_fg,
        consola_a_bg="#1a1a1a", consola_a_fg=ca_fg,
        consola_b_bg="#1a1a1a", consola_b_fg=cb_fg,
        nodo_idle=nodo_idle, nodo_active=nodo_active,
        nodo_done_a=done_a, nodo_done_b=done_b,
        canal_active=nodo_active, canal_done=done_a,
        btn_send=btn_send, btn_reset=btn_reset, btn_fg=btn_fg,
        stats_bg=stats_bg, stats_fg=stats_fg,
        seq_capa=seq_capa, seq_ok=seq_ok, seq_err=seq_err,
    )

TEMAS = {
    "UNEMI Dark":    _tema("#002147","white","#FFCC00","#f8f9fa","#333333","#001530",
                           "#00ff00","#33ccff","#f8f9fa","#FFCC00","#28a745","#33ccff",
                           "#28a745","#6c757d","white","#001530","#FFCC00"),
    "Cyber Neon":    _tema("#0d0d1a","#ff00ff","#00ffff","#1a1a2e","#00ffff","#0d0d1a",
                           "#ff00ff","#00ffcc","#1a1a2e","#ff00ff","#7700ff","#00ffcc",
                           "#7700ff","#333355","#00ffff","#1a0030","#ff00ff"),
    "Terminal Verde":_tema("#0c1a0c","#00ff41","#00cc33","#0c1f0c","#00ff41","#0c1a0c",
                           "#00ff41","#00cc33","#0c1a0c","#00ff41","#007a1f","#005c17",
                           "#007a1f","#1a3d1a","#00ff41","#091409","#00ff41",
                           "#00ff41","#00ff88","#ff4444"),
    "Clásico Claro": _tema("#e8eaf6","#1a237e","#283593","#ffffff","#333333","#c5cae9",
                           "#a5d6a7","#81d4fa","#e8eaf6","#ffd54f","#66bb6a","#29b6f6",
                           "#1565c0","#546e7a","white","#c5cae9","#1a237e",
                           "#1565c0","#2e7d32","#c62828"),
}

# ─────────────────────────────────────────────
# CAPAS OSI  (índice 0=APL … 6=FIS)
# ─────────────────────────────────────────────
CAPAS_INFO = [
    ("APL","Aplicación",   "Datos",   "HTTP/FTP/SMTP headers",       "—",          "Interfaz entre app y red"),
    ("PRE","Presentación", "Datos",   "Codificación (Base64/UTF-8)", "—",          "Cifrado, compresión, formato"),
    ("SES","Sesión",       "Datos",   "ID Sesión, Sync tokens",      "—",          "Gestión de diálogo y sesión"),
    ("TRA","Transporte",   "Segmento","Puerto src/dst, Seq/Ack, Win","Checksum TCP","TCP/UDP – fiabilidad extremo a extremo"),
    ("RED","Red",          "Paquete", "IP src/dst, TTL, Proto",      "—",          "Enrutamiento IP entre redes"),
    ("ENL","Enlace",       "Trama",   "MAC src/dst, EtherType",      "CRC-32 FCS", "Control de acceso al medio"),
    ("FIS","Física",       "Bits",    "Preámbulo, SFD",              "—",          "Señales eléctricas/ópticas"),
]
NOMBRES_SEQ = [c[0] for c in CAPAS_INFO]   # ["APL","PRE",…,"FIS"]


class SimuladorOSI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Modelos OSI – UNEMI 2026")
        self.root.geometry("1280x900")

        self.tema_actual = tk.StringVar(value="UNEMI Dark")
        self.velocidad   = tk.DoubleVar(value=0.35)
        self._after_ids  = []
        self._animando   = False
        self._seq_emisor_count = self._seq_receptor_count = 0

        self._construir_ui()
        self._aplicar_tema()

    # ──────────────────────────────────────────
    # UI
    # ──────────────────────────────────────────
    def _construir_ui(self):
        r = self.root

        self.frm_header = tk.Frame(r)
        self.frm_header.pack(fill=tk.X)
        self.lbl_titulo = tk.Label(self.frm_header,
            text="UNIVERSIDAD ESTATAL DE MILAGRO", font=("Helvetica", 18, "bold"))
        self.lbl_titulo.pack(pady=5)
         # Subtítulo
        self.lbl_subtitulo = tk.Label(
        self.frm_header,
            text="Sistema desarrollado por los integrantes del Grupo N",
            font=("Helvetica", 11, "italic"),
            fg="black"
        )
        self.lbl_subtitulo.pack(pady=2)
        self.info_frame = tk.Frame(r, bd=1, relief=tk.SOLID)
        self.info_frame.pack(fill=tk.X, padx=40, pady=3)
        self.lbl_nota = tk.Label(self.info_frame, wraplength=1000,
            font=("Arial", 9, "italic"),
            text=("NOTA TÉCNICA: El modelo OSI se lee del 7 al 1 (Emisor) porque describe el proceso "
                  "de envío desde la aplicación hasta el medio físico. En el Receptor se lee del 1 al 7 "
                  "para reconstruir los datos."))
        self.lbl_nota.pack(pady=4)

        # ── Barra de control ──
        self.panel = tk.Frame(r)
        self.panel.pack(pady=6)

        self.entrada = tk.Entry(self.panel, width=38, font=("Arial", 11))
        self.entrada.insert(0, "Datos de Evaluación UNEMI")
        self.entrada.pack(side=tk.LEFT, padx=8)

        self.btn_send  = tk.Button(self.panel, text="🚀 ENVIAR",  command=self.transmitir, width=12, font=("bold",))
        self.btn_reset = tk.Button(self.panel, text="🔄 RESET",   command=self.resetear,   width=12, font=("bold",))
        self.btn_send.pack(side=tk.LEFT, padx=4)
        self.btn_reset.pack(side=tk.LEFT, padx=4)

        tk.Label(self.panel, text="  Tema:", font=("Arial", 9)).pack(side=tk.LEFT)
        self.cmb_tema = ttk.Combobox(self.panel, textvariable=self.tema_actual,
            values=list(TEMAS.keys()), state="readonly", width=14, font=("Arial", 9))
        self.cmb_tema.pack(side=tk.LEFT, padx=4)
        self.cmb_tema.bind("<<ComboboxSelected>>", lambda e: self._aplicar_tema())

        tk.Label(self.panel, text="  Velocidad:", font=("Arial", 9)).pack(side=tk.LEFT)
        self.lbl_vel = tk.Label(self.panel, text="Normal", font=("Arial", 9, "bold"), width=7)
        self.lbl_vel.pack(side=tk.LEFT)
        self.scl_vel = tk.Scale(self.panel, from_=0.05, to=1.0, resolution=0.05,
            orient=tk.HORIZONTAL, variable=self.velocidad,
            command=self._actualizar_label_vel, length=120, showvalue=False)
        self.scl_vel.pack(side=tk.LEFT, padx=2)

        # ── Contenedor 3 columnas ──
        self.main_container = tk.Frame(r)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20)
        for col, w in enumerate([1, 0, 1]):
            self.main_container.columnconfigure(col, weight=w)

        self._construir_terminal("a", 0, "TERMINAL EMISOR (ENCAPSULAMIENTO L7→L1)")
        self._construir_canal()
        self._construir_terminal("b", 2, "TERMINAL RECEPTOR (DESENCAPSULAMIENTO L1→L7)")

        nombres_rx = list(reversed(NOMBRES_SEQ))
        self._dibujar_nodos(self.canvas_a, self.rects_a, NOMBRES_SEQ,  lambda i: f"L{7-i}")
        self._dibujar_nodos(self.canvas_b, self.rects_b, nombres_rx,   lambda i: f"L{i+1}")

    def _construir_terminal(self, lado, col, titulo):
        frm = tk.Frame(self.main_container)
        frm.grid(row=0, column=col, sticky="nsew")
        canvas = tk.Canvas(frm, width=480, height=120, highlightthickness=1, bg="white")
        canvas.pack(pady=5)
        lbl = tk.Label(frm, text=titulo, font=("bold", 9))
        lbl.pack()
        consola = tk.Text(frm, width=60, height=19, font=("Consolas", 9))
        consola.pack(pady=5)

        setattr(self, f"frame_pc{lado}", frm)
        setattr(self, f"canvas_{lado}", canvas)
        setattr(self, f"lbl_pc{lado}", lbl)
        setattr(self, f"consola_{lado}", consola)
        setattr(self, f"rects_{lado}", [])

    def _construir_canal(self):
        self.frame_canal = tk.Frame(self.main_container)
        self.frame_canal.grid(row=0, column=1, padx=10)

        self.canvas_canal = tk.Canvas(self.frame_canal, width=110, height=120, highlightthickness=0)
        self.canvas_canal.pack()
        self.flecha = self.canvas_canal.create_line(10, 60, 100, 60, arrow=tk.LAST, width=4, fill="#dee2e6")

        self.lbl_canal = tk.Label(self.frame_canal, text="CANAL\nM/M/1", font=("Arial", 8, "italic"))
        self.lbl_canal.pack()

        self.frm_stats = tk.Frame(self.frame_canal, bd=2, relief=tk.SOLID)
        self.frm_stats.pack(pady=6, fill=tk.X)

        self.lbl_seq_title    = tk.Label(self.frm_stats, text="SECUENCIA",        font=("Consolas", 7, "bold"))
        self.lbl_seq_em_label = tk.Label(self.frm_stats, text="EMISOR (L7→L1)",   font=("Consolas", 7))
        self.lbl_seq_emisor   = tk.Label(self.frm_stats, text="···",              font=("Consolas", 8, "bold"), wraplength=95, justify=tk.LEFT)
        self.lbl_seq_canal    = tk.Label(self.frm_stats, text="",                 font=("Consolas", 8, "bold"))
        self.lbl_seq_rx_label = tk.Label(self.frm_stats, text="RECEPTOR (L1→L7)", font=("Consolas", 7))
        self.lbl_seq_receptor = tk.Label(self.frm_stats, text="···",              font=("Consolas", 8, "bold"), wraplength=95, justify=tk.LEFT)
        self.lbl_seq_result   = tk.Label(self.frm_stats, text="",                 font=("Consolas", 9, "bold"))

        for w in [self.lbl_seq_title, self.lbl_seq_em_label, self.lbl_seq_emisor,
                  self.lbl_seq_canal, self.lbl_seq_rx_label, self.lbl_seq_receptor,
                  self.lbl_seq_result]:
            w.pack(padx=4, pady=(4 if w is self.lbl_seq_title else 0))
        self.lbl_seq_result.pack_configure(pady=(2, 6))

    # ──────────────────────────────────────────
    # NODOS
    # ──────────────────────────────────────────
    def _dibujar_nodos(self, canvas, rects, nombres, nivel_fn):
        for i, nombre in enumerate(nombres):
            x = 15 + i * 65
            r = canvas.create_rectangle(x, 30, x+55, 90, outline="#002147", fill="#f8f9fa")
            canvas.create_text(x+27, 52, text=nombre,      font=("Arial", 7, "bold"))
            canvas.create_text(x+27, 68, text=nivel_fn(i), font=("Arial", 6), fill="#555")
            rects.append(r)

    # ──────────────────────────────────────────
    # LOGS (unificados)
    # ──────────────────────────────────────────
    def log(self, consola, msg):
        consola.insert(tk.END, msg + "\n")
        consola.see(tk.END)

    def log_a(self, msg): self.log(self.consola_a, msg)
    def log_b(self, msg): self.log(self.consola_b, msg)

    # ──────────────────────────────────────────
    # VELOCIDAD
    # ──────────────────────────────────────────
    def _actualizar_label_vel(self, val=None):
        v = self.velocidad.get()
        etq = ("Turbo ⚡" if v <= 0.10 else "Rápido" if v <= 0.25
               else "Normal" if v <= 0.45 else "Lento" if v <= 0.70 else "Muy lento")
        self.lbl_vel.configure(text=etq)

    # ──────────────────────────────────────────
    # TEMAS
    # ──────────────────────────────────────────
    def _aplicar_tema(self):
        t = self._t = TEMAS[self.tema_actual.get()]

        # Fondos de frames
        for frm in [self.frm_header, self.panel, self.main_container,
                    self.frame_pca, self.frame_canal, self.frame_pcb]:
            frm.configure(bg=t["bg"])

        self.root.configure(bg=t["bg"])
        self.lbl_titulo.configure(bg=t["bg"], fg=t["fg_titulo"])
        self.lbl_subtitulo.configure(bg=t["bg"], fg=t["fg_subtitulo"])
        self.info_frame.configure(bg=t["nota_bg"])
        self.lbl_nota.configure(bg=t["nota_bg"], fg=t["nota_fg"])
        self.lbl_pca.configure(bg=t["bg"], fg=t["fg_subtitulo"])
        self.lbl_pcb.configure(bg=t["bg"], fg=t["fg_subtitulo"])
        self.lbl_canal.configure(bg=t["canal_bg"], fg=t["canal_fg"])
        self.canvas_canal.configure(bg=t["canal_bg"])

        self.frm_stats.configure(bg=t["stats_bg"])
        for w in [self.lbl_seq_title, self.lbl_seq_em_label, self.lbl_seq_emisor,
                  self.lbl_seq_canal, self.lbl_seq_rx_label, self.lbl_seq_receptor,
                  self.lbl_seq_result]:
            w.configure(bg=t["stats_bg"], fg=t["stats_fg"])

        self.consola_a.configure(bg=t["consola_a_bg"], fg=t["consola_a_fg"],
                                 insertbackground=t["consola_a_fg"])
        self.consola_b.configure(bg=t["consola_b_bg"], fg=t["consola_b_fg"],
                                 insertbackground=t["consola_b_fg"])
        self.btn_send.configure(bg=t["btn_send"],  fg=t["btn_fg"])
        self.btn_reset.configure(bg=t["btn_reset"], fg=t["btn_fg"])
        self.lbl_vel.configure(bg=t["bg"], fg=t["fg_subtitulo"])
        self.scl_vel.configure(bg=t["bg"], fg=t["fg_subtitulo"],
                               troughcolor=t["stats_bg"], highlightbackground=t["bg"])
        self._refrescar_nodos_idle()

    def _refrescar_nodos_idle(self):
        t = self._t
        for r in self.rects_a:
            self.canvas_a.itemconfig(r, fill=t["nodo_idle"], outline=t["bg"])
        for r in self.rects_b:
            self.canvas_b.itemconfig(r, fill=t["nodo_idle"], outline=t["bg"])
        self.canvas_canal.itemconfig(self.flecha, fill="#dee2e6")
        self.canvas_a.configure(bg=t["nota_bg"])
        self.canvas_b.configure(bg=t["nota_bg"])

    # ──────────────────────────────────────────
    # SECUENCIA
    # ──────────────────────────────────────────
    def _render_seq(self, hechas, direccion="enc"):
        nombres = NOMBRES_SEQ if direccion == "enc" else list(reversed(NOMBRES_SEQ))
        partes = [("✔" if i < hechas else "") + n for i, n in enumerate(nombres)]
        return " → ".join(partes)

    def _actualizar_secuencia(self, fase):
        t = self._t
        cfg = {
            "enc":   lambda: (
                self.lbl_seq_emisor.configure(text=self._render_seq(self._seq_emisor_count), fg=t["seq_capa"]),
                self.lbl_seq_canal.configure(text="", fg=t["stats_fg"]),
                self.lbl_seq_receptor.configure(text="···", fg=t["stats_fg"]),
                self.lbl_seq_result.configure(text=""),
            ),
            "canal": lambda: (
                self.lbl_seq_emisor.configure(text=self._render_seq(7), fg=t["seq_ok"]),
                self.lbl_seq_canal.configure(text="~~~ ✈ ~~~", fg=t["canal_active"]),
                self.lbl_seq_receptor.configure(text="···", fg=t["stats_fg"]),
                self.lbl_seq_result.configure(text=""),
            ),
            "dec":   lambda: (
                self.lbl_seq_receptor.configure(text=self._render_seq(self._seq_receptor_count, "dec"), fg=t["seq_capa"]),
                self.lbl_seq_canal.configure(text="~~~ ✔ ~~~", fg=t["seq_ok"]),
                self.lbl_seq_result.configure(text=""),
            ),
            "ok":    lambda: (
                self.lbl_seq_receptor.configure(text=self._render_seq(7, "dec"), fg=t["seq_ok"]),
                self.lbl_seq_result.configure(text="✅ ÉXITO", fg=t["seq_ok"]),
            ),
            "error": lambda: self.lbl_seq_result.configure(text="❌ ERROR", fg=t["seq_err"]),
        }
        cfg.get(fase, lambda: None)()

    # ──────────────────────────────────────────
    # M/M/1
    # ──────────────────────────────────────────
    def _calcular_mm1(self):
        lam = round(random.uniform(0.5, 2.5), 3)
        mu  = round(lam + random.uniform(0.5, 2.0), 3)
        rho = round(lam / mu, 4)
        Wq  = round(rho / (mu * (1 - rho)), 4)
        Lq  = round(lam * Wq, 4)
        return lam, mu, rho, Wq, Lq

    # ──────────────────────────────────────────
    # TRANSMISIÓN
    # ──────────────────────────────────────────
    def transmitir(self):
        msg = self.entrada.get().strip()
        if not msg:
            messagebox.showwarning("Campo vacío", "⚠️  Por favor ingresa un mensaje antes de enviar.")
            return
        if self._animando:
            return

        self.resetear()
        self._animando = True
        self.btn_send.configure(state=tk.DISABLED)

        lam, mu, rho, Wq, Lq = self._calcular_mm1()
        self.log_a(f"  M/M/1  λ={lam} pkt/s  μ={mu} pkt/s  ρ={rho*100:.1f}%  Wq={Wq:.4f}s\n")
        self.log_a("╔══════════════════════════════════════════╗")
        self.log_a("║   INICIO DE ENCAPSULAMIENTO OSI – PC-A   ║")
        self.log_a("╚══════════════════════════════════════════╝")
        self.log_a(f"  Mensaje original : '{msg}'\n  Longitud         : {len(msg)} bytes\n")

        data_ref = [msg]
        pasos = (
            [("enc",   i,   CAPAS_INFO[i],     data_ref) for i in range(7)] +
            [("canal", None, None,             data_ref)] +
            [("dec",   i,   CAPAS_INFO[6-i],   data_ref) for i in range(7)] +
            [("fin",   None, None,             data_ref)]
        )

        self._seq_emisor_count = self._seq_receptor_count = 0
        self._ejecutar_paso(pasos, 0)

    # ──────────────────────────────────────────
    # EJECUCIÓN DE PASOS
    # ──────────────────────────────────────────
    def _ejecutar_paso(self, pasos, idx):
        if idx >= len(pasos):
            return
        tipo, i, capa, data_ref = pasos[idx]
        t = self._t
        delay_ms = int(self.velocidad.get() * 1000)

        if tipo == "enc":
            self.canvas_a.itemconfig(self.rects_a[i], fill=t["nodo_active"])
            if i == 1:
                data_ref[0] = base64.b64encode(data_ref[0].encode()).decode()

            wq_local = random.expovariate(3.0)
            self.log_a(f"  ▶ Capa {7-i} – {capa[1]:12s} ({capa[0]})")
            self.log_a(f"    PDU      : {capa[2]}")
            self.log_a(f"    Header   : {capa[3]}")
            if capa[4] != "—": self.log_a(f"    Trailer  : {capa[4]}")
            self.log_a(f"    Info     : {capa[5]}")
            self.log_a(f"    Wq local : {wq_local:.4f}s")
            if i == 1:
                preview = data_ref[0][:40] + "…" if len(data_ref[0]) > 40 else data_ref[0]
                self.log_a(f"    Payload  : {preview}")
            self.log_a("")

            self._seq_emisor_count = i
            self._actualizar_secuencia("enc")

            def _done_enc(i=i):
                self.canvas_a.itemconfig(self.rects_a[i], fill=t["nodo_done_a"])
                self._seq_emisor_count = i + 1
                self._actualizar_secuencia("enc")
                self._ejecutar_paso(pasos, idx + 1)
            self._after_ids.append(self.root.after(delay_ms, _done_enc))

        elif tipo == "canal":
            self.canvas_canal.itemconfig(self.flecha, fill=t["canal_active"])
            self.log_a("━" * 46)
            self.log_a("  ✈  [CANAL] Propagación física en curso…\n     Bits transmitidos al medio (L7→L1)")
            self.log_a("━" * 46 + "\n")
            self._actualizar_secuencia("canal")

            def _done_canal():
                self.canvas_canal.itemconfig(self.flecha, fill=t["canal_done"])
                self.log_b("╔══════════════════════════════════════════╗")
                self.log_b("║  INICIO DE DESENCAPSULAMIENTO – PC-B     ║")
                self.log_b("║  Orden: L1(FIS) → L2(ENL) → … → L7(APL) ║")
                self.log_b("╚══════════════════════════════════════════╝")
                self.log_b("  [CANAL] Trama de bits recibida ✔\n")
                self._seq_receptor_count = 0
                self._ejecutar_paso(pasos, idx + 1)
            self._after_ids.append(self.root.after(max(int(delay_ms * 2.5), 600), _done_canal))

        elif tipo == "dec":
            self.canvas_b.itemconfig(self.rects_b[i], fill=t["nodo_active"])
            if i == 5:
                try:
                    data_ref[0] = base64.b64decode(data_ref[0].encode()).decode()
                except Exception:
                    pass

            wq_local = random.uniform(0.01, 0.1)
            nivel = i + 1
            self.log_b(f"  ◀ Capa {nivel} – {capa[1]:12s} ({capa[0]})")
            self.log_b(f"    PDU      : {capa[2]}")
            self.log_b(f"    {'Trailer' if capa[4] != '—' else 'Header'}  : {capa[4] if capa[4] != '—' else capa[3]}")
            self.log_b(f"    Info     : {capa[5]}")
            self.log_b(f"    Wq local : {wq_local:.4f}s")
            if i == 5: self.log_b(f"    Payload  : '{data_ref[0]}'")
            self.log_b("")

            self._seq_receptor_count = i
            self._actualizar_secuencia("dec")

            def _done_dec(i=i):
                self.canvas_b.itemconfig(self.rects_b[i], fill=t["nodo_done_b"])
                self._seq_receptor_count = i + 1
                self._actualizar_secuencia("dec")
                self._ejecutar_paso(pasos, idx + 1)
            self._after_ids.append(self.root.after(delay_ms, _done_dec))

        elif tipo == "fin":
            ok = (data_ref[0] == self.entrada.get().strip())
            self.log_b("╔══════════════════════════════════════════╗")
            self.log_b("║     DESENCAPSULAMIENTO COMPLETO – PC-B   ║")
            self.log_b("╚══════════════════════════════════════════╝")
            self.log_b(f"  Mensaje final : '{data_ref[0]}'")
            self.log_b(f"  Integridad    : {'✔ OK' if ok else '✘ ERROR'}")
            self.log_b(f"  Estado        : {'ÉXITO ✅' if ok else 'ERROR ❌'}")
            self._actualizar_secuencia("ok" if ok else "error")
            self._animando = False
            self.btn_send.configure(state=tk.NORMAL)

    # ──────────────────────────────────────────
    # RESET
    # ──────────────────────────────────────────
    def resetear(self):
        for aid in self._after_ids:
            self.root.after_cancel(aid)
        self._after_ids.clear()
        self._animando = False
        self._seq_emisor_count = self._seq_receptor_count = 0
        self.consola_a.delete(1.0, tk.END)
        self.consola_b.delete(1.0, tk.END)
        self.canvas_canal.itemconfig(self.flecha, fill="#dee2e6")
        for w in [self.lbl_seq_emisor, self.lbl_seq_receptor]:
            w.configure(text="···")
        self.lbl_seq_canal.configure(text="")
        self.lbl_seq_result.configure(text="")
        self.btn_send.configure(state=tk.NORMAL)
        self._refrescar_nodos_idle()


if __name__ == "__main__":
    root = tk.Tk()
    SimuladorOSI(root)
    root.mainloop()