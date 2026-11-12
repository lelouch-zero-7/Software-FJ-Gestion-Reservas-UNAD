# -*- coding: utf-8 -*-
"""
Módulo 3: Clase Abstracta Servicio, Subclases Especializadas y Polimorfismo.
Proyecto: Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ.
Curso: Programación (213023) - UNAD.
"""

from abc import abstractmethod  # Importa el decorador para definir métodos abstractos obligatorios.
from functools import singledispatchmethod  # Permite implementar sobrecarga formal de métodos en Python.

# Importa las excepciones personalizadas del Módulo 1 y la clase base del Módulo 2.
from excepciones_logs import ServicioNoDisponibleError, CalculoCostoError
from modelos_base import EntidadSistema


# ==============================================================================
# 1. CLASE ABSTRACTA SERVICIO
# ==============================================================================

class Servicio(EntidadSistema):
    """
    Clase abstracta que modela cualquier servicio ofrecido por Software FJ.
    Hereda de EntidadSistema y establece la interfaz común para el cálculo
    polimórfico de tarifas, validación de disponibilidad y sobrecarga de costos.
    """

    def __init__(self, id_servicio: str, nombre_servicio: str, tarifa_hora: float):
        try:
            # Inicializa la entidad base con su identificador único.
            super().__init__(id_servicio)
            # Valida que el nombre del servicio no esté vacío.
            if not nombre_servicio or not isinstance(nombre_servicio, str) or len(nombre_servicio.strip()) < 3:
                raise ValueError("El nombre del servicio debe tener al menos 3 caracteres.")
            # Valida que la tarifa por hora sea un número positivo mayor a cero.
            if not isinstance(tarifa_hora, (int, float)) or tarifa_hora <= 0:
                raise ValueError("La tarifa por hora debe ser un valor numérico mayor a cero.")

            # Almacena los atributos encapsulados del servicio.
            self._nombre_servicio = nombre_servicio.strip()
            self._tarifa_hora = float(tarifa_hora)
        except (ValueError, TypeError) as err_tecnico:
            # Encadena la excepción técnica hacia una excepción de dominio de servicios.
            raise ServicioNoDisponibleError(
                f"Error al configurar el servicio '{nombre_servicio}': {err_tecnico}"
            ) from err_tecnico

    @property
    def nombre_servicio(self) -> str:
        """Retorna el nombre comercial del servicio."""
        return self._nombre_servicio

    @property
    def tarifa_hora(self) -> float:
        """Retorna la tarifa base por hora del servicio."""
        return self._tarifa_hora

    @abstractmethod
    def calcular_costo_base(self, duracion_horas: int) -> float:
        """Método abstracto polimórfico para calcular el subtotal según la duración."""
        pass

    @abstractmethod
    def verificar_disponibilidad(self, cantidad_requerida: int = 1) -> bool:
        """Método abstracto que verifica si el servicio tiene cupo o stock operativo."""
        pass

    # --- Implementación de Métodos Sobrecargados para Cálculo Final ---
    @singledispatchmethod
    def calcular_total(self, datos_calculo, iva: float = 0.19, descuento: float = 0.0) -> float:
        """
        Método sobrecargado principal que calcula el costo total aplicando IVA y descuentos.
        Soporta recibir directamente la duración (int) o un diccionario de parámetros (dict).
        """
        raise CalculoCostoError(
            f"Tipo de parámetro no soportado para el cálculo de costos: {type(datos_calculo).__name__}"
        )

    @calcular_total.register(int)
    def _(self, duracion_horas: int, iva: float = 0.19, descuento: float = 0.0) -> float:
        """Sobrecarga 1: Calcula el total recibiendo directamente las horas como entero."""
        if duracion_horas <= 0:
            raise CalculoCostoError("La duración en horas debe ser mayor a cero.")
        if not (0.0 <= iva <= 1.0) or not (0.0 <= descuento < 1.0):
            raise CalculoCostoError("Los porcentajes de IVA (0-1) o descuento (0-0.99) están fuera de rango.")

        subtotal = self.calcular_costo_base(duracion_horas)
        valor_descuento = subtotal * descuento
        base_gravable = subtotal - valor_descuento
        total = base_gravable * (1 + iva)
        return round(total, 2)

    @calcular_total.register(dict)
    def _(self, parametros: dict, iva: float = 0.19, descuento: float = 0.0) -> float:
        """Sobrecarga 2: Calcula el total recibiendo un diccionario con horas, iva y descuento opcionales."""
        if "horas" not in parametros:
            raise CalculoCostoError("El diccionario de cálculo debe incluir la clave obligatoria 'horas'.")
        horas = parametros["horas"]
        iva_dic = parametros.get("iva", iva)
        desc_dic = parametros.get("descuento", descuento)
        # Delega la validación y cálculo matemático a la sobrecarga entera.
        return self.calcular_total(int(horas), float(iva_dic), float(desc_dic))

    def validar_datos(self) -> bool:
        """Verifica que el servicio esté activo y tenga tarifa válida."""
        return bool(self._nombre_servicio) and self._tarifa_hora > 0 and self._activo


# ==============================================================================
# 2. SUBCLASES ESPECIALIZADAS (HERENCIA Y POLIMORFISMO)
# ==============================================================================

class ReservaSala(Servicio):
    """
    Servicio especializado 1: Alquiler de salas de juntas, auditorios o laboratorios.
    Aplica recargo logístico si la capacidad supera los 20 asistentes.
    """

    def __init__(self, id_servicio: str, nombre_servicio: str, tarifa_hora: float, capacidad_maxima: int):
        super().__init__(id_servicio, nombre_servicio, tarifa_hora)
        if not isinstance(capacidad_maxima, int) or capacidad_maxima <= 0:
            raise ServicioNoDisponibleError("La capacidad máxima de la sala debe ser un entero positivo.")
        self.capacidad_maxima = capacidad_maxima
        self.ocupada = False

    def verificar_disponibilidad(self, cantidad_requerida: int = 1) -> bool:
        """Verifica que la sala no esté ocupada y soporte el aforo solicitado."""
        if not self._activo or self.ocupada:
            raise ServicioNoDisponibleError(f"La sala '{self._nombre_servicio}' no se encuentra disponible.")
        if cantidad_requerida > self.capacidad_maxima:
            raise ServicioNoDisponibleError(
                f"Aforo excedido: '{self._nombre_servicio}' soporta máximo {self.capacidad_maxima} personas."
            )
        return True

    def calcular_costo_base(self, duracion_horas: int) -> float:
        """Polimorfismo: Incluye un 10% adicional de logística si la sala es de gran formato (>20 personas)."""
        costo = self._tarifa_hora * duracion_horas
        if self.capacidad_maxima > 20:
            costo *= 1.10
        return round(costo, 2)

    def obtener_resumen(self) -> str:
        estado = "Ocupada" if self.ocupada else "Disponible"
        return (
            f"Servicio Sala [{self.id_entidad}] | {self._nombre_servicio} | "
            f"Capacidad: {self.capacidad_maxima} pers. | Tarifa: ${self._tarifa_hora:,.2f}/h | {estado}"
        )


class AlquilerEquipo(Servicio):
    """
    Servicio especializado 2: Alquiler de hardware, servidores, proyectores o estaciones de trabajo.
    Gestiona inventario disponible y aplica póliza de seguro tecnológico por hora.
    """

    def __init__(self, id_servicio: str, nombre_servicio: str, tarifa_hora: float, stock_disponible: int, seguro_hora: float = 5000.0):
        super().__init__(id_servicio, nombre_servicio, tarifa_hora)
        if not isinstance(stock_disponible, int) or stock_disponible < 0:
            raise ServicioNoDisponibleError("El stock de equipos no puede ser negativo.")
        if seguro_hora < 0:
            raise ServicioNoDisponibleError("El valor del seguro por hora no puede ser negativo.")
        self.stock_disponible = stock_disponible
        self.seguro_hora = float(seguro_hora)

    def verificar_disponibilidad(self, cantidad_requerida: int = 1) -> bool:
        """Verifica que existan unidades suficientes en inventario."""
        if not self._activo or self.stock_disponible < cantidad_requerida or self.stock_disponible == 0:
            raise ServicioNoDisponibleError(
                f"Stock insuficiente para '{self._nombre_servicio}'. Disponibles: {self.stock_disponible}."
            )
        return True

    def calcular_costo_base(self, duracion_horas: int) -> float:
        """Polimorfismo: Suma la tarifa base por hora más la póliza de seguro del equipo."""
        return round((self._tarifa_hora + self.seguro_hora) * duracion_horas, 2)

    def obtener_resumen(self) -> str:
        return (
            f"Servicio Equipo [{self.id_entidad}] | {self._nombre_servicio} | "
            f"Stock: {self.stock_disponible} unid. | Tarifa: ${self._tarifa_hora:,.2f}/h + Seguro: ${self.seguro_hora:,.2f}/h"
        )


class AsesoriaEspecializada(Servicio):
    """
    Servicio especializado 3: Consultoría en arquitectura de software, ciberseguridad o nube.
    Aplica descuento automático por bloques de más de 5 horas continuas.
    """

    def __init__(self, id_servicio: str, nombre_servicio: str, tarifa_hora: float, especialidad: str, consultor_asignado: str):
        super().__init__(id_servicio, nombre_servicio, tarifa_hora)
        if not especialidad or not consultor_asignado:
            raise ServicioNoDisponibleError("La asesoría requiere especialidad y consultor asignado.")
        self.especialidad = especialidad.strip()
        self.consultor_asignado = consultor_asignado.strip()

    def verificar_disponibilidad(self, cantidad_requerida: int = 1) -> bool:
        """Verifica que la línea de asesoría se encuentre activa."""
        if not self._activo:
            raise ServicioNoDisponibleError(f"La asesoría '{self._nombre_servicio}' está temporalmente suspendida.")
        return True

    def calcular_costo_base(self, duracion_horas: int) -> float:
        """Polimorfismo: Aplica un 15% de bonificación en tarifa base si se contratan más de 5 horas."""
        costo = self._tarifa_hora * duracion_horas
        if duracion_horas > 5:
            costo *= 0.85
        return round(costo, 2)

    def obtener_resumen(self) -> str:
        return (
            f"Servicio Asesoría [{self.id_entidad}] | {self._nombre_servicio} ({self.especialidad}) | "
            f"Consultor: {self.consultor_asignado} | Tarifa: ${self._tarifa_hora:,.2f}/h"
        )
