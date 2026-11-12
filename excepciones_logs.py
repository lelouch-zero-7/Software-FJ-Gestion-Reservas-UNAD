# -*- coding: utf-8 -*-
"""
Módulo 1: Excepciones Personalizadas y Sistema de Logging.
Proyecto: Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ.
Curso: Programación (213023_2204) - UNAD.
"""

import logging  # Importa la librería estándar de Python para registro de eventos y errores en archivos.
from datetime import datetime  # Importa datetime para sellar con fecha y hora exacta cada operación.


# ==============================================================================
# 1. JERARQUÍA DE EXCEPCIONES PERSONALIZADAS DEL SISTEMA
# ==============================================================================

class SoftwareFJError(Exception):
    """
    Excepción base personalizada para todo el sistema de Software FJ.
    Hereda de la clase nativa Exception de Python para permitir capturar
    cualquier error propio del dominio de la aplicación de forma unificada.
    """

    def __init__(self, mensaje: str, codigo_error: str = "ERR-GENERAL"):
        # Llama al constructor de la clase padre Exception con el mensaje descriptivo.
        super().__init__(mensaje)
        # Almacena el mensaje legible del error para consultas o auditoría.
        self.mensaje = mensaje
        # Asigna un código identificador único al error para facilitar su rastreo en logs.
        self.codigo_error = codigo_error
        # Registra el instante exacto en que se originó la excepción.
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __str__(self) -> str:
        # Retorna una representación formateada con código, hora y detalle del fallo.
        return f"[{self.codigo_error}] ({self.timestamp}) -> {self.mensaje}"


class ValidacionClienteError(SoftwareFJError):
    """
    Excepción lanzada cuando los datos personales de un cliente no cumplen
    las reglas de integridad (documento inválido, correo mal formado, nombre vacío, etc.).
    """

    def __init__(self, mensaje: str):
        # Inicializa la excepción base con un código específico de validación de cliente.
        super().__init__(mensaje, codigo_error="ERR-CLIENTE-001")


class ServicioNoDisponibleError(SoftwareFJError):
    """
    Excepción lanzada cuando se intenta crear, consultar o reservar un servicio
    que se encuentra inactivo, sin cupos/inventario o con parámetros inválidos.
    """

    def __init__(self, mensaje: str):
        # Inicializa la excepción base con un código específico de disponibilidad de servicio.
        super().__init__(mensaje, codigo_error="ERR-SERVICIO-002")


class ReservaInvalidaError(SoftwareFJError):
    """
    Excepción lanzada ante operaciones no permitidas en reservas: duración negativa,
    cliente no registrado, cambios de estado ilegales (ej. confirmar una reserva cancelada).
    """

    def __init__(self, mensaje: str):
        # Inicializa la excepción base con un código específico de gestión de reservas.
        super().__init__(mensaje, codigo_error="ERR-RESERVA-003")


class CalculoCostoError(SoftwareFJError):
    """
    Excepción lanzada cuando ocurren inconsistencias matemáticas o parámetros
    fuera de rango durante el cálculo de tarifas, impuestos o descuentos.
    """

    def __init__(self, mensaje: str):
        # Inicializa la excepción base con un código específico de errores financieros/cálculo.
        super().__init__(mensaje, codigo_error="ERR-CALCULO-004")


# ==============================================================================
# 2. GESTOR DE LOGS EN ARCHIVO (SIN BASE DE DATOS)
# ==============================================================================

class GestorLogs:
    """
    Clase encargada de administrar el registro persistente de eventos informativos,
    advertencias y errores críticos en un archivo plano (.log), garantizando
    que no se dupliquen manejadores de escritura durante la ejecución.
    """

    def __init__(self, nombre_archivo: str = "sistema_software_fj.log"):
        # Guarda la ruta o nombre del archivo donde se almacenarán los registros.
        self.nombre_archivo = nombre_archivo
        # Obtiene una instancia nombrada del logger para el sistema Software FJ.
        self.logger = logging.getLogger("SoftwareFJ_Logger")
        # Establece el nivel mínimo de captura en INFO (captura INFO, WARNING, ERROR y CRITICAL).
        self.logger.setLevel(logging.INFO)

        # Verifica si el logger aún no tiene manejadores (handlers) configurados para evitar logs duplicados.
        if not self.logger.handlers:
            # Crea un manejador de archivo con codificación UTF-8 para soportar tildes y caracteres en español.
            file_handler = logging.FileHandler(self.nombre_archivo, mode="a", encoding="utf-8")
            # Define el formato estructurado: Fecha/Hora | Nivel | Mensaje del evento.
            formatter = logging.Formatter(
                fmt="%(asctime)s | %(levelname)-8s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            # Asocia el formato al manejador de archivo.
            file_handler.setFormatter(formatter)
            # Agrega el manejador configurado al logger principal.
            self.logger.addHandler(file_handler)

    def registrar_info(self, mensaje: str) -> None:
        """Registra una operación exitosa o evento normal del sistema."""
        # Escribe una línea de nivel INFO en el archivo de logs.
        self.logger.info(mensaje)

    def registrar_advertencia(self, mensaje: str) -> None:
        """Registra una alerta operativa que no detiene el flujo pero requiere atención."""
        # Escribe una línea de nivel WARNING en el archivo de logs.
        self.logger.warning(mensaje)

    def registrar_error(self, excepcion: Exception, contexto: str = "") -> None:
        """
        Registra detalladamente cualquier excepción capturada, incluyendo su causa
        encadenada (__cause__) si existe, manteniendo el programa estable.
        """
        # Construye el prefijo de contexto si fue proporcionado.
        prefijo = f"[{contexto}] " if contexto else ""
        # Verifica si la excepción fue producto de un encadenamiento (raise ... from ...).
        if excepcion.__cause__ is not None:
            # Documenta tanto la excepción de negocio como la excepción técnica original.
            detalle = (
                f"{prefijo}{type(excepcion).__name__}: {excepcion} | "
                f"Causa original ({type(excepcion.__cause__).__name__}): {excepcion.__cause__}"
            )
        else:
            # Documenta únicamente la excepción principal cuando no hay encadenamiento.
            detalle = f"{prefijo}{type(excepcion).__name__}: {excepcion}"

        # Escribe el error completo en el archivo de logs con nivel ERROR.
        self.logger.error(detalle)
