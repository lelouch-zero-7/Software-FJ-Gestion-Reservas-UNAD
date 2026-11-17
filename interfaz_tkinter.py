# -*- coding: utf-8 -*-
"""
Módulo 6: Interfaz Gráfica de Usuario (GUI) en Tkinter para Software FJ.
Integra de forma visual la gestión de clientes, servicios especializados, reservas,
ejecución de las 12 simulaciones y visualización de auditoría en tiempo real.
Proyecto: Fase 4 - Programación (213023) - UNAD.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import io
import contextlib

# Importa las clases de dominio y lógica de negocio de los módulos previos
from excepciones_logs import SoftwareFJError
from modelos_base import Cliente
from servicios import ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from reservas import GestorSoftwareFJ
from main import ejecutar_simulacion


class AplicacionSoftwareFJ(tk.Tk):
    """Ventana principal de la aplicación gráfica en Tkinter para Software FJ."""

    def __init__(self):
        super().__init__()
        self.title("Software FJ - Gestión Integral de Clientes, Servicios y Reservas (UNAD)")
        self.geometry("1040x700")
        self.minsize(960, 640)
        self.configure(bg="#F4F6F9")

        # Instancia el gestor central en memoria y carga datos iniciales de demostración
        self.gestor = GestorSoftwareFJ("sistema_software_fj.log")
        self._cargar_catalogo_inicial()

        self._configurar_estilos()
        self._construir_interfaz()
        self._actualizar_tablas_y_combos()
        self._cargar_logs_en_visor()

    def _configurar_estilos(self) -> None:
        """Define estilos visuales sobrios y modernos usando ttk."""
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure("TFrame", background="#F4F6F9")
        estilo.configure("TLabel", background="#F4F6F9", foreground="#1F2937", font=("Segoe UI", 10))
        estilo.configure("Header.TLabel", background="#0F294A", foreground="#FFFFFF", font=("Segoe UI", 13, "bold"))
        estilo.configure("Subheader.TLabel", background="#0F294A", foreground="#CBD5E1", font=("Segoe UI", 9))
        estilo.configure("TButton", font=("Segoe UI", 9, "bold"), padding=6)
        estilo.configure("Primary.TButton", background="#1D4ED8", foreground="#FFFFFF")
        estilo.map("Primary.TButton", background=[("active", "#1E40AF")])
        estilo.configure("Success.TButton", background="#047857", foreground="#FFFFFF")
        estilo.map("Success.TButton", background=[("active", "#065F46")])
        estilo.configure("Danger.TButton", background="#B91C1C", foreground="#FFFFFF")
        estilo.map("Danger.TButton", background=[("active", "#991B1B")])
        estilo.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#E2E8F0", foreground="#0F172A")
        estilo.configure("Treeview", font=("Segoe UI", 9), rowheight=25)

    def _cargar_catalogo_inicial(self) -> None:
        """Precarga clientes y los 3 servicios polimórficos para pruebas inmediatas."""
        try:
            self.gestor.registrar_cliente(
                Cliente("CLI-01", "1002548963", "David Santiago Ruiz", "david.ruiz@softwarefj.com", "3104567890")
            )
            self.gestor.registrar_cliente(
                Cliente("CLI-02", "1023456789", "Wilian Alejandro Barreto", "wilian.barreto@empresa.co", "3209876543")
            )
            self.gestor.registrar_servicio(
                ReservaSala("SRV-01", "Auditorio Innovación Cloud", 120000.0, capacidad_maxima=35)
            )
            self.gestor.registrar_servicio(
                AlquilerEquipo("SRV-02", "Servidor Rack Dell PowerEdge", 85000.0, stock_disponible=3, seguro_hora=10000.0)
            )
            self.gestor.registrar_servicio(
                AsesoriaEspecializada("SRV-03", "Auditoría Ciberseguridad ISO", 150000.0, "Seguridad", "Ing. Ronald Rodríguez")
            )
        except SoftwareFJError as err:
            self.gestor.logs.registrar_error(err, contexto="PrecargaTkinter")

    def _construir_interfaz(self) -> None:
        """Construye el encabezado, las pestañas funcionales y la barra de estado."""
        # Banner superior institucional
        banner = tk.Frame(self, bg="#0F294A", height=64, padx=18, pady=10)
        banner.pack(fill="x")
        ttk.Label(
            banner,
            text="SOFTWARE FJ — Sistema Integral de Gestión de Clientes, Servicios y Reservas",
            style="Header.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            banner,
            text="Programación Orientada a Objetos, Manejo Avanzado de Excepciones y Persistencia en Logs | UNAD (213023)",
            style="Subheader.TLabel",
        ).pack(anchor="w")

        # Cuaderno de pestañas (Notebook)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=14, pady=10)

        self.tab_clientes = ttk.Frame(self.notebook)
        self.tab_servicios = ttk.Frame(self.notebook)
        self.tab_reservas = ttk.Frame(self.notebook)
        self.tab_simulacion = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_clientes, text=" 1. Clientes ")
        self.notebook.add(self.tab_servicios, text=" 2. Servicios Polimórficos ")
        self.notebook.add(self.tab_reservas, text=" 3. Gestión de Reservas ")
        self.notebook.add(self.tab_simulacion, text=" 4. Simulación (12 Casos) y Logs ")

        self._construir_tab_clientes()
        self._construir_tab_servicios()
        self._construir_tab_reservas()
        self._construir_tab_simulacion()

        # Barra inferior de estado
        self.var_estado = tk.StringVar(value="Sistema operativo en memoria listo. Archivo de auditoría: sistema_software_fj.log")
        barra_estado = tk.Label(
            self, textvariable=self.var_estado, bg="#E2E8F0", fg="#1E293B", anchor="w", padx=12, pady=5, font=("Segoe UI", 9)
        )
        barra_estado.pack(fill="x", side="bottom")

    # --------------------------------------------------------------------------
    # PESTAÑA 1: CLIENTES (ENCAPSULACIÓN Y VALIDACIONES)
    # --------------------------------------------------------------------------
    def _construir_tab_clientes(self) -> None:
        marco_form = ttk.LabelFrame(self.tab_clientes, text=" Registrar Nuevo Cliente ", padding=12)
        marco_form.pack(fill="x", padx=12, pady=10)

        self.ent_cli_id = tk.StringVar(value="CLI-03")
        self.ent_cli_doc = tk.StringVar()
        self.ent_cli_nom = tk.StringVar()
        self.ent_cli_cor = tk.StringVar()
        self.ent_cli_tel = tk.StringVar()

        campos = [
            ("ID Cliente:", self.ent_cli_id, 0, 0),
            ("Documento (6-15 dígitos):", self.ent_cli_doc, 0, 2),
            ("Nombre Completo:", self.ent_cli_nom, 1, 0),
            ("Correo Electrónico:", self.ent_cli_cor, 1, 2),
            ("Teléfono (7-15 dígitos):", self.ent_cli_tel, 2, 0),
        ]
        for texto, var, fila, col in campos:
            ttk.Label(marco_form, text=texto).grid(row=fila, column=col, sticky="w", padx=6, pady=5)
            ttk.Entry(marco_form, textvariable=var, width=28).grid(row=fila, column=col + 1, sticky="w", padx=6, pady=5)

        ttk.Button(
            marco_form, text="Registrar Cliente", style="Primary.TButton", command=self._accion_registrar_cliente
        ).grid(row=2, column=3, sticky="e", padx=6, pady=5)

        marco_tabla = ttk.LabelFrame(self.tab_clientes, text=" Clientes Registrados en Memoria ", padding=10)
        marco_tabla.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        cols = ("id", "documento", "nombre", "correo", "telefono", "estado")
        self.tree_clientes = ttk.Treeview(marco_tabla, columns=cols, show="headings")
        encabezados = {
            "id": "ID",
            "documento": "Documento",
            "nombre": "Nombre Completo",
            "correo": "Correo Electrónico",
            "telefono": "Teléfono",
            "estado": "Estado",
        }
        for c in cols:
            self.tree_clientes.heading(c, text=encabezados[c])
            self.tree_clientes.column(c, width=140 if c != "nombre" else 210)
        self.tree_clientes.pack(fill="both", expand=True)

    def _accion_registrar_cliente(self) -> None:
        try:
            nuevo = Cliente(
                id_cliente=self.ent_cli_id.get(),
                documento=self.ent_cli_doc.get(),
                nombre=self.ent_cli_nom.get(),
                correo=self.ent_cli_cor.get(),
                telefono=self.ent_cli_tel.get(),
            )
            if self.gestor.registrar_cliente(nuevo):
                messagebox.showinfo("Cliente Registrado", f"Cliente '{nuevo.nombre}' agregado correctamente.")
                self.ent_cli_id.set(f"CLI-0{len(self.gestor.clientes) + 1}")
                self.ent_cli_doc.set("")
                self.ent_cli_nom.set("")
                self.ent_cli_cor.set("")
                self.ent_cli_tel.set("")
                self._actualizar_tablas_y_combos()
            else:
                messagebox.showwarning("Registro Duplicado", "Ya existe un cliente con ese ID o documento. Revisa los logs.")
        except SoftwareFJError as err:
            self.gestor.logs.registrar_error(err, contexto="GUI_RegistroCliente")
            messagebox.showerror("Error de Validación (Cliente)", str(err))
        finally:
            self._cargar_logs_en_visor()

    # --------------------------------------------------------------------------
    # PESTAÑA 2: SERVICIOS ESPECIALIZADOS (POLIMORFISMO)
    # --------------------------------------------------------------------------
    def _construir_tab_servicios(self) -> None:
        marco_form = ttk.LabelFrame(self.tab_servicios, text=" Crear Servicio Especializado ", padding=12)
        marco_form.pack(fill="x", padx=12, pady=10)

        self.var_srv_tipo = tk.StringVar(value="ReservaSala")
        self.var_srv_id = tk.StringVar(value="SRV-04")
        self.var_srv_nom = tk.StringVar()
        self.var_srv_tarifa = tk.StringVar(value="90000")
        self.var_srv_extra = tk.StringVar(value="25")

        ttk.Label(marco_form, text="Tipo de Servicio:").grid(row=0, column=0, sticky="w", padx=6, pady=5)
        cb_tipo = ttk.Combobox(
            marco_form,
            textvariable=self.var_srv_tipo,
            values=["ReservaSala", "AlquilerEquipo", "AsesoriaEspecializada"],
            state="readonly",
            width=25,
        )
        cb_tipo.grid(row=0, column=1, sticky="w", padx=6, pady=5)

        ttk.Label(marco_form, text="ID Servicio:").grid(row=0, column=2, sticky="w", padx=6, pady=5)
        ttk.Entry(marco_form, textvariable=self.var_srv_id, width=25).grid(row=0, column=3, sticky="w", padx=6, pady=5)

        ttk.Label(marco_form, text="Nombre Comercial:").grid(row=1, column=0, sticky="w", padx=6, pady=5)
        ttk.Entry(marco_form, textvariable=self.var_srv_nom, width=28).grid(row=1, column=1, sticky="w", padx=6, pady=5)

        ttk.Label(marco_form, text="Tarifa Base / Hora ($):").grid(row=1, column=2, sticky="w", padx=6, pady=5)
        ttk.Entry(marco_form, textvariable=self.var_srv_tarifa, width=25).grid(row=1, column=3, sticky="w", padx=6, pady=5)

        ttk.Label(marco_form, text="Capacidad / Stock / Consultor:").grid(row=2, column=0, sticky="w", padx=6, pady=5)
        ttk.Entry(marco_form, textvariable=self.var_srv_extra, width=28).grid(row=2, column=1, sticky="w", padx=6, pady=5)

        ttk.Button(
            marco_form, text="Agregar al Catálogo", style="Primary.TButton", command=self._accion_crear_servicio
        ).grid(row=2, column=3, sticky="e", padx=6, pady=5)

        marco_tabla = ttk.LabelFrame(self.tab_servicios, text=" Catálogo Activo de Servicios ", padding=10)
        marco_tabla.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        cols = ("id", "tipo", "nombre", "tarifa", "detalle")
        self.tree_servicios = ttk.Treeview(marco_tabla, columns=cols, show="headings")
        self.tree_servicios.heading("id", text="ID")
        self.tree_servicios.heading("tipo", text="Clase Polimórfica")
        self.tree_servicios.heading("nombre", text="Servicio")
        self.tree_servicios.heading("tarifa", text="Tarifa/Hora")
        self.tree_servicios.heading("detalle", text="Detalle Operativo")
        self.tree_servicios.column("id", width=80)
        self.tree_servicios.column("tipo", width=160)
        self.tree_servicios.column("nombre", width=230)
        self.tree_servicios.column("tarifa", width=120)
        self.tree_servicios.column("detalle", width=350)
        self.tree_servicios.pack(fill="both", expand=True)

    def _accion_crear_servicio(self) -> None:
        try:
            tipo = self.var_srv_tipo.get()
            id_srv = self.var_srv_id.get()
            nom = self.var_srv_nom.get()
            tarifa = float(self.var_srv_tarifa.get())
            extra = self.var_srv_extra.get().strip()

            if tipo == "ReservaSala":
                srv = ReservaSala(id_srv, nom, tarifa, capacidad_maxima=int(extra))
            elif tipo == "AlquilerEquipo":
                srv = AlquilerEquipo(id_srv, nom, tarifa, stock_disponible=int(extra))
            else:
                srv = AsesoriaEspecializada(id_srv, nom, tarifa, especialidad="Consultoría TI", consultor_asignado=extra or "Equipo FJ")

            if self.gestor.registrar_servicio(srv):
                messagebox.showinfo("Servicio Creado", f"Servicio '{srv.nombre_servicio}' habilitado correctamente.")
                self.var_srv_id.set(f"SRV-0{len(self.gestor.servicios) + 1}")
                self.var_srv_nom.set("")
                self._actualizar_tablas_y_combos()
            else:
                messagebox.showwarning("ID Duplicado", "Ya existe un servicio con ese identificador.")
        except ValueError as err_val:
            messagebox.showerror("Error de Formato Numérico", f"Verifica los valores numéricos ingresados: {err_val}")
        except SoftwareFJError as err:
            self.gestor.logs.registrar_error(err, contexto="GUI_CrearServicio")
            messagebox.showerror("Error de Servicio", str(err))
        finally:
            self._cargar_logs_en_visor()

    # --------------------------------------------------------------------------
    # PESTAÑA 3: RESERVAS Y CICLO DE ESTADOS
    # --------------------------------------------------------------------------
    def _construir_tab_reservas(self) -> None:
        marco_form = ttk.LabelFrame(self.tab_reservas, text=" Nueva Reserva de Servicio ", padding=12)
        marco_form.pack(fill="x", padx=12, pady=10)

        self.var_res_id = tk.StringVar(value="RES-01")
        self.var_res_cli = tk.StringVar()
        self.var_res_srv = tk.StringVar()
        self.var_res_horas = tk.StringVar(value="4")
        self.var_res_cant = tk.StringVar(value="1")
        self.var_res_desc = tk.StringVar(value="0.0")

        ttk.Label(marco_form, text="Código Reserva:").grid(row=0, column=0, sticky="w", padx=6, pady=5)
        ttk.Entry(marco_form, textvariable=self.var_res_id, width=22).grid(row=0, column=1, sticky="w", padx=6, pady=5)

        ttk.Label(marco_form, text="Cliente:").grid(row=0, column=2, sticky="w", padx=6, pady=5)
        self.cb_res_cliente = ttk.Combobox(marco_form, textvariable=self.var_res_cli, state="readonly", width=30)
        self.cb_res_cliente.grid(row=0, column=3, sticky="w", padx=6, pady=5)

        ttk.Label(marco_form, text="Servicio:").grid(row=1, column=0, sticky="w", padx=6, pady=5)
        self.cb_res_servicio = ttk.Combobox(marco_form, textvariable=self.var_res_srv, state="readonly", width=30)
        self.cb_res_servicio.grid(row=1, column=1, sticky="w", padx=6, pady=5)

        ttk.Label(marco_form, text="Duración (horas):").grid(row=1, column=2, sticky="w", padx=6, pady=5)
        ttk.Entry(marco_form, textvariable=self.var_res_horas, width=15).grid(row=1, column=3, sticky="w", padx=6, pady=5)

        ttk.Label(marco_form, text="Cantidad / Aforo:").grid(row=2, column=0, sticky="w", padx=6, pady=5)
        ttk.Entry(marco_form, textvariable=self.var_res_cant, width=15).grid(row=2, column=1, sticky="w", padx=6, pady=5)

        ttk.Label(marco_form, text="Descuento (0.0 - 0.9):").grid(row=2, column=2, sticky="w", padx=6, pady=5)
        ttk.Entry(marco_form, textvariable=self.var_res_desc, width=15).grid(row=2, column=3, sticky="w", padx=6, pady=5)

        ttk.Button(
            marco_form, text="Crear y Confirmar Reserva", style="Success.TButton", command=self._accion_crear_reserva
        ).grid(row=3, column=3, sticky="e", padx=6, pady=6)

        marco_tabla = ttk.LabelFrame(self.tab_reservas, text=" Reservas Registradas ", padding=10)
        marco_tabla.pack(fill="both", expand=True, padx=12, pady=(0, 6))

        cols = ("id", "estado", "cliente", "servicio", "horas", "cantidad", "total")
        self.tree_reservas = ttk.Treeview(marco_tabla, columns=cols, show="headings")
        titulos = {
            "id": "Código",
            "estado": "Estado",
            "cliente": "Cliente",
            "servicio": "Servicio",
            "horas": "Horas",
            "cantidad": "Cant/Aforo",
            "total": "Total c/IVA",
        }
        for c in cols:
            self.tree_reservas.heading(c, text=titulos[c])
            self.tree_reservas.column(c, width=110 if c not in ("cliente", "servicio") else 200)
        self.tree_reservas.pack(fill="both", expand=True)

        marco_acciones = ttk.Frame(self.tab_reservas)
        marco_acciones.pack(fill="x", padx=12, pady=(0, 10))
        ttk.Button(
            marco_acciones, text="Procesar / Facturar Seleccionada", style="Primary.TButton", command=self._accion_procesar_reserva
        ).pack(side="left", padx=(0, 8))
        ttk.Button(
            marco_acciones, text="Cancelar Seleccionada", style="Danger.TButton", command=self._accion_cancelar_reserva
        ).pack(side="left")

    def _accion_crear_reserva(self) -> None:
        try:
            id_res = self.var_res_id.get().strip()
            id_cli = self.var_res_cli.get().split(" - ")[0].strip()
            id_srv = self.var_res_srv.get().split(" - ")[0].strip()
            horas = int(self.var_res_horas.get())
            cant = int(self.var_res_cant.get())
            desc = float(self.var_res_desc.get())

            reserva = self.gestor.crear_y_confirmar_reserva(
                id_reserva=id_res,
                id_cliente=id_cli,
                id_servicio=id_srv,
                duracion_horas=horas,
                cantidad=cant,
                descuento=desc,
                confirmar_inmediato=True,
            )
            if reserva:
                messagebox.showinfo(
                    "Reserva Confirmada",
                    f"Reserva creada con éxito.\nTotal con IVA: ${reserva.costo_total:,.2f}",
                )
                self.var_res_id.set(f"RES-0{len(self.gestor.reservas) + 1}")
                self._actualizar_tablas_y_combos()
            else:
                messagebox.showerror(
                    "Reserva Rechazada",
                    "No se pudo completar la reserva (disponibilidad, stock o datos inválidos).\nConsulta el detalle en la pestaña de Logs.",
                )
        except ValueError as err_val:
            messagebox.showerror("Error de Entrada", f"Verifica que horas, cantidad y descuento sean numéricos: {err_val}")
        finally:
            self._cargar_logs_en_visor()

    def _obtener_reserva_seleccionada(self):
        seleccion = self.tree_reservas.selection()
        if not seleccion:
            messagebox.showwarning("Selección Requerida", "Selecciona primero una reserva en la tabla.")
            return None
        id_res = self.tree_reservas.item(seleccion[0])["values"][0]
        return next((r for r in self.gestor.reservas if r.id_entidad == id_res), None)

    def _accion_procesar_reserva(self) -> None:
        reserva = self._obtener_reserva_seleccionada()
        if not reserva:
            return
        try:
            total = reserva.procesar()
            self.gestor.logs.registrar_info(f"Reserva {reserva.id_entidad} procesada desde GUI por ${total:,.2f}")
            messagebox.showinfo("Reserva Procesada", f"Reserva '{reserva.id_entidad}' facturada por ${total:,.2f} y recurso liberado.")
            self._actualizar_tablas_y_combos()
        except SoftwareFJError as err:
            self.gestor.logs.registrar_error(err, contexto="GUI_ProcesarReserva")
            messagebox.showerror("Operación Inválida", str(err))
        finally:
            self._cargar_logs_en_visor()

    def _accion_cancelar_reserva(self) -> None:
        reserva = self._obtener_reserva_seleccionada()
        if not reserva:
            return
        try:
            reserva.cancelar("Cancelada desde interfaz Tkinter")
            self.gestor.logs.registrar_info(f"Reserva {reserva.id_entidad} cancelada desde GUI; recurso restituido.")
            messagebox.showinfo("Reserva Cancelada", f"La reserva '{reserva.id_entidad}' fue cancelada y su disponibilidad restituida.")
            self._actualizar_tablas_y_combos()
        except SoftwareFJError as err:
            self.gestor.logs.registrar_error(err, contexto="GUI_CancelarReserva")
            messagebox.showerror("Operación Inválida", str(err))
        finally:
            self._cargar_logs_en_visor()

    # --------------------------------------------------------------------------
    # PESTAÑA 4: SIMULACIÓN INTEGRAL (12 CASOS) Y VISOR DE LOGS
    # --------------------------------------------------------------------------
    def _construir_tab_simulacion(self) -> None:
        marco_sup = ttk.Frame(self.tab_simulacion, padding=10)
        marco_sup.pack(fill="x")

        ttk.Button(
            marco_sup,
            text="▶ Ejecutar 12 Simulaciones Completas (main.py)",
            style="Primary.TButton",
            command=self._accion_ejecutar_12_simulaciones,
        ).pack(side="left", padx=(0, 10))

        ttk.Button(
            marco_sup,
            text="↻ Actualizar Archivo de Logs",
            command=self._cargar_logs_en_visor,
        ).pack(side="left")

        panel_dividido = ttk.PanedWindow(self.tab_simulacion, orient="vertical")
        panel_dividido.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        marco_consola = ttk.LabelFrame(panel_dividido, text=" Salida de Ejecución de las 12 Simulaciones ", padding=8)
        self.txt_consola = scrolledtext.ScrolledText(marco_consola, height=11, font=("Consolas", 9), bg="#0F172A", fg="#E2E8F0")
        self.txt_consola.pack(fill="both", expand=True)

        marco_logs = ttk.LabelFrame(panel_dividido, text=" Auditoría Persistente (sistema_software_fj.log) ", padding=8)
        self.txt_logs = scrolledtext.ScrolledText(marco_logs, height=11, font=("Consolas", 9), bg="#1E293B", fg="#A7F3D0")
        self.txt_logs.pack(fill="both", expand=True)

        panel_dividido.add(marco_consola, weight=1)
        panel_dividido.add(marco_logs, weight=1)

    def _accion_ejecutar_12_simulaciones(self) -> None:
        buffer_salida = io.StringIO()
        with contextlib.redirect_stdout(buffer_salida):
            ejecutar_simulacion()
        self.txt_consola.delete("1.0", tk.END)
        self.txt_consola.insert(tk.END, buffer_salida.getvalue())
        self._cargar_logs_en_visor()
        self.var_estado.set("Simulación integral de 12 operaciones ejecutada con éxito (estabilidad 100%).")

    def _cargar_logs_en_visor(self) -> None:
        try:
            with open("sistema_software_fj.log", "r", encoding="utf-8") as archivo:
                contenido = archivo.read()
        except FileNotFoundError:
            contenido = "Aún no se ha generado el archivo sistema_software_fj.log."
        self.txt_logs.delete("1.0", tk.END)
        self.txt_logs.insert(tk.END, contenido)
        self.txt_logs.see(tk.END)

    def _actualizar_tablas_y_combos(self) -> None:
        # Refresca tabla de clientes
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)
        for c in self.gestor.clientes:
            self.tree_clientes.insert(
                "", tk.END, values=(c.id_entidad, c.documento, c.nombre, c.correo, c.telefono, "Activo" if c.activo else "Inactivo")
            )

        # Refresca tabla de servicios
        for item in self.tree_servicios.get_children():
            self.tree_servicios.delete(item)
        for s in self.gestor.servicios:
            self.tree_servicios.insert(
                "", tk.END, values=(s.id_entidad, type(s).__name__, s.nombre_servicio, f"${s.tarifa_hora:,.2f}", s.obtener_resumen())
            )

        # Refresca tabla de reservas
        for item in self.tree_reservas.get_children():
            self.tree_reservas.delete(item)
        for r in self.gestor.reservas:
            self.tree_reservas.insert(
                "",
                tk.END,
                values=(
                    r.id_entidad,
                    r.estado,
                    r.cliente.nombre,
                    r.servicio.nombre_servicio,
                    f"{r.duracion_horas} h",
                    r.cantidad,
                    f"${r.costo_total:,.2f}",
                ),
            )

        # Actualiza listas desplegables en pestaña Reservas
        self.cb_res_cliente["values"] = [f"{c.id_entidad} - {c.nombre}" for c in self.gestor.clientes]
        if self.cb_res_cliente["values"] and not self.var_res_cli.get():
            self.var_res_cli.set(self.cb_res_cliente["values"][0])

        self.cb_res_servicio["values"] = [f"{s.id_entidad} - {s.nombre_servicio}" for s in self.gestor.servicios]
        if self.cb_res_servicio["values"] and not self.var_res_srv.get():
            self.var_res_srv.set(self.cb_res_servicio["values"][0])


if __name__ == "__main__":
    app = AplicacionSoftwareFJ()
    app.mainloop()
