import flet as ft
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

# ============================================================
# MODELO DE DATOS
# ============================================================

class Categoria:
    def __init__(self, nombre: str, tipo: str, icono: str = "💼", color: str = "blue"):
        self.nombre = nombre
        self.tipo = tipo  # 'ingreso' o 'gasto'
        self.icono = icono
        self.color = color
    
    def to_dict(self):
        return {
            "nombre": self.nombre,
            "tipo": self.tipo,
            "icono": self.icono,
            "color": self.color
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class Transaccion:
    def __init__(self, monto: float, tipo: str, categoria: str, 
                 cuenta: str, descripcion: str = "", fecha: str = None):
        self.id = datetime.now().strftime("%Y%m%d%H%M%S%f")
        self.monto = monto
        self.tipo = tipo  # 'ingreso', 'gasto', 'transferencia'
        self.categoria = categoria
        self.cuenta = cuenta
        self.descripcion = descripcion
        self.fecha = fecha or datetime.now().strftime("%Y-%m-%d %H:%M")
    
    def to_dict(self):
        return {
            "id": self.id,
            "monto": self.monto,
            "tipo": self.tipo,
            "categoria": self.categoria,
            "cuenta": self.cuenta,
            "descripcion": self.descripcion,
            "fecha": self.fecha
        }
    
    @classmethod
    def from_dict(cls, data):
        t = cls(
            monto=data["monto"],
            tipo=data["tipo"],
            categoria=data["categoria"],
            cuenta=data["cuenta"],
            descripcion=data.get("descripcion", ""),
            fecha=data.get("fecha")
        )
        t.id = data.get("id", t.id)
        return t

class Cuenta:
    def __init__(self, nombre: str, saldo_inicial: float = 0.0, 
                 tipo: str = "efectivo", color: str = "green"):
        self.nombre = nombre
        self.saldo = saldo_inicial
        self.saldo_inicial = saldo_inicial
        self.tipo = tipo  # 'efectivo', 'banco', 'ahorro', 'inversion'
        self.color = color
    
    def to_dict(self):
        return {
            "nombre": self.nombre,
            "saldo": self.saldo,
            "saldo_inicial": self.saldo_inicial,
            "tipo": self.tipo,
            "color": self.color
        }
    
    @classmethod
    def from_dict(cls, data):
        c = cls(
            nombre=data["nombre"],
            saldo_inicial=data.get("saldo_inicial", 0),
            tipo=data.get("tipo", "efectivo"),
            color=data.get("color", "green")
        )
        c.saldo = data.get("saldo", c.saldo_inicial)
        return c

# ============================================================
# GESTOR DE DATOS LOCAL
# ============================================================

class FinanceManager:
    def __init__(self):
        self.archivo = "finanzas_data.json"
        self.cuentas: List[Cuenta] = []
        self.categorias: List[Categoria] = []
        self.transacciones: List[Transaccion] = []
        self.cargar_datos()
    
    def cargar_datos(self):
        if os.path.exists(self.archivo):
            try:
                with open(self.archivo, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.cuentas = [Cuenta.from_dict(c) for c in data.get("cuentas", [])]
                    self.categorias = [Categoria.from_dict(c) for c in data.get("categorias", [])]
                    self.transacciones = [Transaccion.from_dict(t) for t in data.get("transacciones", [])]
            except:
                self.inicializar_datos_default()
        else:
            self.inicializar_datos_default()
    
    def guardar_datos(self):
        data = {
            "cuentas": [c.to_dict() for c in self.cuentas],
            "categorias": [c.to_dict() for c in self.categorias],
            "transacciones": [t.to_dict() for t in self.transacciones]
        }
        with open(self.archivo, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def inicializar_datos_default(self):
        # Categorías por defecto
        self.categorias = [
            Categoria("Sueldo", "ingreso", "💰", "green"),
            Categoria("Freelance", "ingreso", "💻", "blue"),
            Categoria("Alimentación", "gasto", "🍔", "orange"),
            Categoria("Transporte", "gasto", "🚗", "purple"),
            Categoria("Entretenimiento", "gasto", "🎮", "pink"),
            Categoria("Servicios", "gasto", "💡", "yellow"),
            Categoria("Salud", "gasto", "🏥", "red"),
            Categoria("Educación", "gasto", "📚", "cyan")
        ]
        
        # Cuenta por defecto
        self.cuentas = [
            Cuenta("Efectivo", 0, "efectivo", "green"),
            Cuenta("Banco Principal", 0, "banco", "blue")
        ]
        
        self.guardar_datos()
    
    def agregar_cuenta(self, nombre, saldo_inicial=0, tipo="efectivo", color="blue"):
        cuenta = Cuenta(nombre, saldo_inicial, tipo, color)
        self.cuentas.append(cuenta)
        self.guardar_datos()
        return cuenta
    
    def eliminar_cuenta(self, nombre):
        self.cuentas = [c for c in self.cuentas if c.nombre != nombre]
        self.guardar_datos()
    
    def agregar_categoria(self, nombre, tipo, icono="💼", color="blue"):
        cat = Categoria(nombre, tipo, icono, color)
        self.categorias.append(cat)
        self.guardar_datos()
        return cat
    
    def eliminar_categoria(self, nombre):
        self.categorias = [c for c in self.categorias if c.nombre != nombre]
        self.guardar_datos()
    
    def agregar_transaccion(self, monto, tipo, categoria, cuenta, descripcion=""):
        trans = Transaccion(monto, tipo, categoria, cuenta, descripcion)
        self.transacciones.append(trans)
        
        # Actualizar saldo de cuenta
        for c in self.cuentas:
            if c.nombre == cuenta:
                if tipo == "ingreso":
                    c.saldo += monto
                elif tipo == "gasto":
                    c.saldo -= monto
                break
        
        self.guardar_datos()
        return trans
    
    def transferir_entre_cuentas(self, cuenta_origen, cuenta_destino, monto, comision=0.41):
        """
        Transfiere entre cuentas con comisión automática (por defecto 0.41%)
        """
        total_descontar = monto * (1 + comision / 100)
        
        # Verificar fondos suficientes
        origen = next((c for c in self.cuentas if c.nombre == cuenta_origen), None)
        if not origen or origen.saldo < total_descontar:
            return False, "Fondos insuficientes"
        
        # Realizar transferencia
        origen.saldo -= total_descontar
        
        destino = next((c for c in self.cuentas if c.nombre == cuenta_destino), None)
        if destino:
            destino.saldo += monto
        
        # Registrar transacciones
        self.transacciones.append(Transaccion(
            monto=total_descontar,
            tipo="transferencia",
            categoria=f"Transferencia a {cuenta_destino}",
            cuenta=cuenta_origen,
            descripcion=f"Envío: ${monto:.2f} + Comisión: ${monto * comision / 100:.2f}"
        ))
        
        self.transacciones.append(Transaccion(
            monto=monto,
            tipo="ingreso",
            categoria=f"Transferencia desde {cuenta_origen}",
            cuenta=cuenta_destino,
            descripcion=f"Recibido de {cuenta_origen}"
        ))
        
        self.guardar_datos()
        return True, f"Transferencia exitosa. Comisión: ${monto * comision / 100:.2f}"
    
    def get_balance_total(self):
        return sum(c.saldo for c in self.cuentas)
    
    def get_transacciones_recientes(self, limite=10):
        return sorted(self.transacciones, key=lambda x: x.fecha, reverse=True)[:limite]
    
    def get_estadisticas_mes(self):
        # Estadísticas del mes actual
        mes_actual = datetime.now().strftime("%Y-%m")
        trans_mes = [t for t in self.transacciones if t.fecha.startswith(mes_actual)]
        
        ingresos = sum(t.monto for t in trans_mes if t.tipo == "ingreso")
        gastos = sum(t.monto for t in trans_mes if t.tipo == "gasto")
        
        return {
            "ingresos": ingresos,
            "gastos": gastos,
            "balance": ingresos - gastos
        }

# ============================================================
# INTERFAZ CON FLET
# ============================================================

def main(page: ft.Page):
    page.title = "💰 Finanzas Pro"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#1a1a2e"
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO
    
    # Colores personalizados
    COLORS = {
        "primary": "#16213e",
        "secondary": "#0f3460",
        "accent": "#e94560",
        "success": "#00d9ff",
        "warning": "#ffc107",
        "danger": "#ff4757",
        "text": "#eaeaea"
    }
    
    manager = FinanceManager()
    
    # ============================================================
    # COMPONENTES UI
    # ============================================================
    
    def crear_tarjeta_resumen():
        stats = manager.get_estadisticas_mes()
        balance_total = manager.get_balance_total()
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Balance Total", size=14, color="grey"),
                ft.Text(f"${balance_total:,.2f}", size=32, weight="bold", color=COLORS["success"]),
                ft.Divider(height=20, color="transparent"),
                ft.Row([
                    ft.Column([
                        ft.Text("Ingresos del mes", size=12, color="grey"),
                        ft.Text(f"+${stats['ingresos']:,.2f}", size=18, color="green")
                    ], expand=True),
                    ft.Column([
                        ft.Text("Gastos del mes", size=12, color="grey"),
                        ft.Text(f"-${stats['gastos']:,.2f}", size=18, color=COLORS["danger"])
                    ], expand=True)
                ])
            ]),
            padding=20,
            bgcolor=COLORS["primary"],
            border_radius=15,
            margin=ft.margin.only(left=15, right=15, top=15)
        )
    
    def crear_lista_cuentas():
        cuentas_controls = []
        for cuenta in manager.cuentas:
            cuentas_controls.append(
                ft.Container(
                    content=ft.ListTile(
                        leading=ft.CircleAvatar(
                            content=ft.Text(cuenta.nombre[0], color="white"),
                            bgcolor=cuenta.color
                        ),
                        title=ft.Text(cuenta.nombre, color=COLORS["text"]),
                        subtitle=ft.Text(cuenta.tipo.capitalize(), size=12, color="grey"),
                        trailing=ft.Text(
                            f"${cuenta.saldo:,.2f}", 
                            size=16, 
                            weight="bold",
                            color="green" if cuenta.saldo >= 0 else "red"
                        )
                    ),
                    bgcolor=COLORS["secondary"],
                    border_radius=10,
                    margin=ft.margin.only(bottom=5)
                )
            )
        return ft.Column(cuentas_controls, spacing=5)
    
    def crear_lista_transacciones():
        trans = manager.get_transacciones_recientes(5)
        trans_controls = []
        
        colores_tipo = {
            "ingreso": "green",
            "gasto": COLORS["danger"],
            "transferencia": "orange"
        }
        
        iconos_tipo = {
            "ingreso": "↗",
            "gasto": "↘",
            "transferencia": "↔"
        }
        
        for t in trans:
            trans_controls.append(
                ft.Container(
                    content=ft.ListTile(
                        leading=ft.Text(
                            iconos_tipo.get(t.tipo, "•"), 
                            size=24,
                            color=colores_tipo.get(t.tipo, "white")
                        ),
                        title=ft.Text(t.categoria, color=COLORS["text"]),
                        subtitle=ft.Text(
                            f"{t.cuenta} • {t.fecha[:10]}", 
                            size=11, 
                            color="grey"
                        ),
                        trailing=ft.Text(
                            f"{'+' if t.tipo == 'ingreso' else '-'}${abs(t.monto):,.2f}",
                            size=14,
                            weight="bold",
                            color=colores_tipo.get(t.tipo, "white")
                        )
                    ),
                    bgcolor=COLORS["secondary"],
                    border_radius=10,
                    margin=ft.margin.only(bottom=5)
                )
            )
        return ft.Column(trans_controls, spacing=5)
    
    # ============================================================
    # VISTAS
    # ============================================================
    
    def vista_principal():
        return ft.Column([
            crear_tarjeta_resumen(),
            
            # Sección Cuentas
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("Mis Cuentas", size=18, weight="bold", color=COLORS["text"]),
                        ft.IconButton(
                            icon=ft.icons.ADD,
                            icon_color=COLORS["accent"],
                            on_click=lambda _: mostrar_dialogo_nueva_cuenta()
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    crear_lista_cuentas()
                ]),
                padding=15
            ),
            
            # Sección Transacciones Recientes
            ft.Container(
                content=ft.Column([
                    ft.Text("Transacciones Recientes", size=18, weight="bold", color=COLORS["text"]),
                    crear_lista_transacciones()
                ]),
                padding=15
            )
        ], scroll=ft.ScrollMode.AUTO)
    
    def vista_transacciones():
        return ft.Column([
            ft.Container(
                content=ft.Text("Nueva Transacción", size=24, weight="bold"),
                padding=20,
                alignment=ft.alignment.center
            ),
            
            # Botones rápidos
            ft.Row([
                ft.ElevatedButton(
                    "Ingreso",
                    icon=ft.icons.ADD_CIRCLE,
                    bgcolor="green",
                    color="white",
                    expand=True,
                    on_click=lambda _: mostrar_dialogo_transaccion("ingreso")
                ),
                ft.ElevatedButton(
                    "Gasto",
                    icon=ft.icons.REMOVE_CIRCLE,
                    bgcolor=COLORS["danger"],
                    color="white",
                    expand=True,
                    on_click=lambda _: mostrar_dialogo_transaccion("gasto")
                )
            ], padding=20),
            
            ft.ElevatedButton(
                "Transferencia entre cuentas",
                icon=ft.icons.SWAP_HORIZ,
                bgcolor=COLORS["accent"],
                color="white",
                expand=True,
                on_click=lambda _: mostrar_dialogo_transferencia()
            ),
            
            ft.Divider(height=30),
            
            ft.Text("Historial Completo", size=18, weight="bold", padding=20),
            crear_lista_transacciones()
        ], scroll=ft.ScrollMode.AUTO)
    
    def vista_categorias():
        cats_ingreso = [c for c in manager.categorias if c.tipo == "ingreso"]
        cats_gasto = [c for c in manager.categorias if c.tipo == "gasto"]
        
        def crear_grid_categorias(categorias):
            return ft.GridView(
                [ft.Container(
                    content=ft.Column([
                        ft.Text(c.icono, size=30),
                        ft.Text(c.nombre, size=12, text_align="center")
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=COLORS["secondary"],
                    border_radius=10,
                    padding=10,
                    aspect_ratio=1
                ) for c in categorias],
                max_extent=100,
                spacing=10,
                run_spacing=10,
                padding=20
            )
        
        return ft.Column([
            ft.Container(
                content=ft.Text("Categorías", size=24, weight="bold"),
                padding=20
            ),
            
            ft.ElevatedButton(
                "Agregar Categoría",
                icon=ft.icons.ADD,
                on_click=lambda _: mostrar_dialogo_nueva_categoria()
            ),
            
            ft.Text("Ingresos", size=16, weight="bold", color="green", padding=ft.padding.only(left=20, top=20)),
            crear_grid_categorias(cats_ingreso),
            
            ft.Text("Gastos", size=16, weight="bold", color=COLORS["danger"], padding=ft.padding.only(left=20, top=20)),
            crear_grid_categorias(cats_gasto)
        ], scroll=ft.ScrollMode.AUTO)
    
    # ============================================================
    # DIÁLOGOS
    # ============================================================
    
    def mostrar_dialogo_nueva_cuenta():
        nombre = ft.TextField(label="Nombre de la cuenta")
        saldo = ft.TextField(label="Saldo inicial", value="0", keyboard_type=ft.KeyboardType.NUMBER)
        tipo = ft.Dropdown(
            label="Tipo",
            options=[
                ft.dropdown.Option("efectivo", "Efectivo"),
                ft.dropdown.Option("banco", "Cuenta Bancaria"),
                ft.dropdown.Option("ahorro", "Ahorro"),
                ft.dropdown.Option("inversion", "Inversión")
            ]
        )
        
        def guardar(e):
            if nombre.value:
                manager.agregar_cuenta(
                    nombre.value, 
                    float(saldo.value or 0), 
                    tipo.value or "efectivo"
                )
                actualizar_vista()
                page.dialog.open = False
                page.update()
        
        page.dialog = ft.AlertDialog(
            title=ft.Text("Nueva Cuenta"),
            content=ft.Column([nombre, saldo, tipo], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: cerrar_dialogo()),
                ft.ElevatedButton("Guardar", on_click=guardar, bgcolor=COLORS["accent"])
            ]
        )
        page.dialog.open = True
        page.update()
    
    def mostrar_dialogo_transaccion(tipo):
        monto = ft.TextField(label="Monto", keyboard_type=ft.KeyboardType.NUMBER, prefix_text="$")
        descripcion = ft.TextField(label="Descripción (opcional)")
        
        cuenta_dd = ft.Dropdown(
            label="Cuenta",
            options=[ft.dropdown.Option(c.nombre) for c in manager.cuentas]
        )
        
        cat_dd = ft.Dropdown(
            label="Categoría",
            options=[ft.dropdown.Option(c.nombre) for c in manager.categorias if c.tipo == tipo]
        )
        
        def guardar(e):
            if monto.value and cuenta_dd.value and cat_dd.value:
                manager.agregar_transaccion(
                    float(monto.value),
                    tipo,
                    cat_dd.value,
                    cuenta_dd.value,
                    descripcion.value
                )
                actualizar_vista()
                page.dialog.open = False
                page.update()
                page.snack_bar = ft.SnackBar(ft.Text(f"{'Ingreso' if tipo == 'ingreso' else 'Gasto'} registrado"))
                page.snack_bar.open = True
                page.update()
        
        page.dialog = ft.AlertDialog(
            title=ft.Text(f"Nuevo {'Ingreso' if tipo == 'ingreso' else 'Gasto'}"),
            content=ft.Column([monto, cuenta_dd, cat_dd, descripcion], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: cerrar_dialogo()),
                ft.ElevatedButton("Guardar", on_click=guardar, bgcolor="green" if tipo == "ingreso" else COLORS["danger"])
            ]
        )
        page.dialog.open = True
        page.update()
    
    def mostrar_dialogo_transferencia():
        origen = ft.Dropdown(
            label="Desde",
            options=[ft.dropdown.Option(c.nombre) for c in manager.cuentas]
        )
        destino = ft.Dropdown(
            label="Hacia",
            options=[ft.dropdown.Option(c.nombre) for c in manager.cuentas]
        )
        monto = ft.TextField(label="Monto a transferir", keyboard_type=ft.KeyboardType.NUMBER, prefix_text="$")
        comision = ft.TextField(label="Comisión %", value="0.41", keyboard_type=ft.KeyboardType.NUMBER)
        
        info_text = ft.Text(size=12, color="grey")
        
        def calcular_comision(e):
            try:
                m = float(monto.value or 0)
                c = float(comision.value or 0)
                total = m * (1 + c/100)
                com = m * c/100
                info_text.value = f"Se descontarán: ${total:.2f} (Comisión: ${com:.2f})"
                page.update()
            except:
                pass
        
        monto.on_change = calcular_comision
        comision.on_change = calcular_comision
        
        def transferir(e):
            if origen.value and destino.value and monto.value and origen.value != destino.value:
                exito, mensaje = manager.transferir_entre_cuentas(
                    origen.value,
                    destino.value,
                    float(monto.value),
                    float(comision.value or 0.41)
                )
                
                actualizar_vista()
                page.dialog.open = False
                page.update()
                
                page.snack_bar = ft.SnackBar(
                    ft.Text(mensaje),
                    bgcolor="green" if exito else "red"
                )
                page.snack_bar.open = True
                page.update()
        
        page.dialog = ft.AlertDialog(
            title=ft.Text("Transferencia entre Cuentas"),
            content=ft.Column([
                origen, destino, monto, comision, info_text
            ], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: cerrar_dialogo()),
                ft.ElevatedButton("Transferir", on_click=transferir, bgcolor=COLORS["accent"])
            ]
        )
        page.dialog.open = True
        page.update()
    
    def mostrar_dialogo_nueva_categoria():
        nombre = ft.TextField(label="Nombre")
        tipo = ft.Dropdown(
            label="Tipo",
            options=[
                ft.dropdown.Option("ingreso", "Ingreso"),
                ft.dropdown.Option("gasto", "Gasto")
            ]
        )
        icono = ft.TextField(label="Emoji (ej: 🍔)", value="💼")
        
        def guardar(e):
            if nombre.value and tipo.value:
                manager.agregar_categoria(nombre.value, tipo.value, icono.value)
                actualizar_vista()
                page.dialog.open = False
                page.update()
        
        page.dialog = ft.AlertDialog(
            title=ft.Text("Nueva Categoría"),
            content=ft.Column([nombre, tipo, icono], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: cerrar_dialogo()),
                ft.ElevatedButton("Guardar", on_click=guardar)
            ]
        )
        page.dialog.open = True
        page.update()
    
    def cerrar_dialogo():
        page.dialog.open = False
        page.update()
    
    # ============================================================
    # NAVEGACIÓN
    # ============================================================
    
    content_area = ft.Container(expand=True)
    
    def cambiar_vista(index):
        vistas = [vista_principal, vista_transacciones, vista_categorias]
        content_area.content = vistas[index]()
        page.update()
    
    def actualizar_vista():
        # Encuentra el índice actual y refresca
        cambiar_vista(0)
    
    # Barra de navegación inferior
    nav_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationDestination(icon=ft.icons.DASHBOARD, label="Resumen"),
            ft.NavigationDestination(icon=ft.icons.SWAP_HORIZ, label="Transacciones"),
            ft.NavigationDestination(icon=ft.icons.CATEGORY, label="Categorías")
        ],
        on_change=lambda e: cambiar_vista(e.control.selected_index),
        bgcolor=COLORS["primary"],
        indicator_color=COLORS["accent"]
    )
    
    # Layout principal
    page.add(
        ft.Column([
            ft.Container(
                content=ft.Text("💰 Finanzas Pro", size=20, weight="bold"),
                padding=15,
                bgcolor=COLORS["primary"]
            ),
            content_area,
            nav_bar
        ], expand=True)
    )
    
    # Cargar vista inicial
    cambiar_vista(0)

# Iniciar app
ft.app(target=main)
