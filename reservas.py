# -*- coding: utf-8 -*-
"""
Módulo 4: Clase Reserva y Gestor Central en Memoria (Sin Base de Datos).
Proyecto: Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ.
Curso: Programación (213023_2204) - UNAD.
"""

from datetime import datetime  # Importa datetime para auditar fechas de creación y actualización.

# Importa excepciones y gestor de logs del Módulo 1.
from excepciones_logs import (
    SoftwareFJError,
    ValidacionClienteError,
    ServicioNoDisponibleError,
    ReservaInvalidaError,
    CalculoCostoError,
    GestorLogs,
)
# Importa entidades base y servicios especializados de los Módulos 2 y 3.
from modelos_base import EntidadSistema, Cliente
from servicios import Servicio, ReservaSala, AlquilerEquipo


# ==============================================================================
# 1. CLASE RESERVA (INTEGRACIÓN CLIENTE, SERVICIO, DURACIÓN Y ESTADOS)
# ==============================================================================

class Reserva(EntidadSistema):
    """
    Modela una reserva de servicio realizada por un cliente de Software FJ.
    Controla el ciclo de vida de estados (PENDIENTE -> CONFIRMADA -> PROCESADA / CANCELADA),
    la disponibilidad de recursos y el cálculo de costos con manejo estricto de excepciones.
    """

    ESTADOS_VALIDOS = ("PENDIENTE", "CONFIRMADA", "PROCESADA", "CANCELADA")

    def __init__(
        self,
        id_reserva: str,
        cliente: Cliente,
        servicio: Servicio,
        duracion_horas: int,
        cantidad: int = 1,
        descuento: float = 0.0,
    ):
        try:
            # Inicializa la entidad base con su identificador único.
            super().__init__(id_reserva)
            # Valida que el cliente sea una instancia activa y válida.
            if not isinstance(cliente, Cliente) or not cliente.validar_datos():
                raise ValueError("Se requiere una instancia válida y activa de Cliente.")
            # Valida que el servicio sea una subclase activa de Servicio.
            if not isinstance(servicio, Servicio) or not servicio.validar_datos():
                raise ValueError("Se requiere una instancia válida y activa de Servicio.")
            # Valida que la duración sea un entero positivo mayor a cero.
            if not isinstance(duracion_horas, int) or duracion_horas <= 0:
                raise ValueError("La duración de la reserva debe ser un número entero mayor a 0 horas.")
            # Valida que la cantidad solicitada sea al menos 1.
            if not isinstance(cantidad, int) or cantidad <= 0:
                raise ValueError("La cantidad solicitada debe ser al menos 1.")

            # Verifica disponibilidad operativa del servicio antes de crear la reserva.
            servicio.verificar_disponibilidad(cantidad)

            # Asigna los atributos de la reserva.
            self.cliente = cliente
            self.servicio = servicio
            self.duracion_horas = duracion_horas
            self.cantidad = cantidad
            self.descuento = float(descuento)
            self._estado = "PENDIENTE"
            self.fecha_actualizacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Calcula el costo total utilizando el método sobrecargado de Servicio (versión dict).
            self.costo_total = self.servicio.calcular_total(
                {"horas": self.duracion_horas, "descuento": self.descuento}
            )
        except ServicioNoDisponibleError:
            # Propaga directamente el error de disponibilidad sin enmascararlo.
            raise
        except (ValueError, TypeError, CalculoCostoError) as err_tecnico:
            # Encadena cualquier error de validación o cálculo hacia ReservaInvalidaError.
            raise ReservaInvalidaError(
                f"No fue posible instanciar la reserva '{id_reserva}': {err_tecnico}"
            ) from err_tecnico

    @property
    def estado(self) -> str:
        """Retorna el estado actual de la reserva."""
        return self._estado

    def confirmar(self) -> None:
        """Confirma una reserva pendiente y bloquea o descuenta el recurso asociado."""
        if self._estado != "PENDIENTE":
            raise ReservaInvalidaError(
                f"Operación no permitida: no se puede confirmar la reserva '{self.id_entidad}' en estado '{self._estado}'."
            )
        # Vuelve a validar disponibilidad al momento exacto de confirmar.
        self.servicio.verificar_disponibilidad(self.cantidad)

        # Actualiza el estado físico del servicio en memoria (polimorfismo por tipo de recurso).
        if isinstance(self.servicio, ReservaSala):
            self.servicio.ocupada = True
        elif isinstance(self.servicio, AlquilerEquipo):
            self.servicio.stock_disponible -= self.cantidad

        self._estado = "CONFIRMADA"
        self.fecha_actualizacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def procesar(self) -> float:
        """Procesa y factura una reserva previamente confirmada, liberando el recurso al finalizar."""
        if self._estado != "CONFIRMADA":
            raise ReservaInvalidaError(
                f"Operación no permitida: la reserva '{self.id_entidad}' debe estar CONFIRMADA para procesarse (actual: '{self._estado}')."
            )
        # Libera el recurso reservado tras completar la prestación del servicio.
        if isinstance(self.servicio, ReservaSala):
            self.servicio.ocupada = False
        elif isinstance(self.servicio, AlquilerEquipo):
            self.servicio.stock_disponible += self.cantidad

        self._estado = "PROCESADA"
        self.fecha_actualizacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self.costo_total

    def cancelar(self, motivo: str = "Cancelación solicitada por el usuario") -> None:
        """Cancela una reserva pendiente o confirmada y restituye cupos/inventario si aplica."""
        if self._estado in ("PROCESADA", "CANCELADA"):
            raise ReservaInvalidaError(
                f"No es posible cancelar la reserva '{self.id_entidad}' porque ya está '{self._estado}'."
            )
        # Si estaba confirmada, revierte la ocupación de sala o inventario de equipos.
        if self._estado == "CONFIRMADA":
            if isinstance(self.servicio, ReservaSala):
                self.servicio.ocupada = False
            elif isinstance(self.servicio, AlquilerEquipo):
                self.servicio.stock_disponible += self.cantidad

        self._estado = "CANCELADA"
        self.fecha_actualizacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def validar_datos(self) -> bool:
        """Verifica la integridad estructural de la reserva."""
        return (
            self.cliente is not None
            and self.servicio is not None
            and self.duracion_horas > 0
            and self._estado in self.ESTADOS_VALIDOS
        )

    def obtener_resumen(self) -> str:
        """Retorna una descripción detallada del estado y costo de la reserva."""
        return (
            f"Reserva [{self.id_entidad}] | Estado: {self._estado} | "
            f"Cliente: {self.cliente.nombre} | Servicio: {self.servicio.nombre_servicio} | "
            f"Duración: {self.duracion_horas}h (Cant: {self.cantidad}) | Total c/IVA: ${self.costo_total:,.2f}"
        )


# ==============================================================================
# 2. GESTOR CENTRAL DEL SISTEMA (LISTAS EN MEMORIA Y BLOQUES TRY/EXCEPT/ELSE/FINALLY)
# ==============================================================================

class GestorSoftwareFJ:
    """
    Controlador principal de Software FJ.
    Administra colecciones en memoria (listas de clientes, servicios y reservas)
    sin motores de base de datos, garantizando continuidad operativa ante errores.
    """

    def __init__(self, archivo_log: str = "sistema_software_fj.log"):
        # Listas internas en memoria para persistencia durante la sesión.
        self.clientes: list[Cliente] = []
        self.servicios: list[Servicio] = []
        self.reservas: list[Reserva] = []
        # Instancia del gestor de logs para auditoría de eventos y excepciones.
        self.logs = GestorLogs(archivo_log)
        self.logs.registrar_info("Sistema Software FJ inicializado correctamente en memoria.")

    def registrar_cliente(self, cliente: Cliente) -> bool:
        """Registra un cliente validando duplicados por ID o documento."""
        try:
            if not isinstance(cliente, Cliente):
                raise ValidacionClienteError("El objeto proporcionado no corresponde a un Cliente válido.")
            for existente in self.clientes:
                if existente.id_entidad == cliente.id_entidad or existente.documento == cliente.documento:
                    raise ValidacionClienteError(
                        f"Cliente duplicado: ya existe un registro con ID '{cliente.id_entidad}' o documento '{cliente.documento}'."
                    )
            self.clientes.append(cliente)
        except SoftwareFJError as err:
            self.logs.registrar_error(err, contexto="RegistroCliente")
            return False
        else:
            # Bloque else: se ejecuta únicamente si no ocurrió ninguna excepción.
            self.logs.registrar_info(f"Cliente registrado con éxito -> {cliente.obtener_resumen()}")
            return True
        finally:
            # Bloque finally: garantiza trazabilidad de cierre de la transacción en memoria.
            pass

    def registrar_servicio(self, servicio: Servicio) -> bool:
        """Agrega un servicio especializado al catálogo en memoria."""
        try:
            if not isinstance(servicio, Servicio):
                raise ServicioNoDisponibleError("El objeto proporcionado no es una subclase válida de Servicio.")
            if any(s.id_entidad == servicio.id_entidad for s in self.servicios):
                raise ServicioNoDisponibleError(f"Ya existe un servicio registrado con ID '{servicio.id_entidad}'.")
            self.servicios.append(servicio)
        except SoftwareFJError as err:
            self.logs.registrar_error(err, contexto="RegistroServicio")
            return False
        else:
            self.logs.registrar_info(f"Servicio habilitado en catálogo -> {servicio.obtener_resumen()}")
            return True
        finally:
            pass

    def crear_y_confirmar_reserva(
        self,
        id_reserva: str,
        id_cliente: str,
        id_servicio: str,
        duracion_horas: int,
        cantidad: int = 1,
        descuento: float = 0.0,
        confirmar_inmediato: bool = True,
    ) -> Reserva | None:
        """
        Busca cliente y servicio en las listas internas, crea la reserva y opcionalmente
        la confirma, demostrando el flujo completo try / except / else / finally.
        """
        reserva_creada = None
        try:
            # Busca el cliente en la lista interna en memoria.
            cliente = next((c for c in self.clientes if c.id_entidad == id_cliente), None)
            if cliente is None:
                raise ReservaInvalidaError(f"No existe ningún cliente registrado con ID '{id_cliente}'.")

            # Busca el servicio en la lista interna en memoria.
            servicio = next((s for s in self.servicios if s.id_entidad == id_servicio), None)
            if servicio is None:
                raise ServicioNoDisponibleError(f"No existe ningún servicio registrado con ID '{id_servicio}'.")

            # Verifica que el código de reserva no esté repetido.
            if any(r.id_entidad == id_reserva for r in self.reservas):
                raise ReservaInvalidaError(f"El código de reserva '{id_reserva}' ya se encuentra en uso.")

            # Instancia la reserva y la confirma si se indicó.
            reserva_creada = Reserva(
                id_reserva=id_reserva,
                cliente=cliente,
                servicio=servicio,
                duracion_horas=duracion_horas,
                cantidad=cantidad,
                descuento=descuento,
            )
            if confirmar_inmediato:
                reserva_creada.confirmar()

            self.reservas.append(reserva_creada)
        except SoftwareFJError as err:
            self.logs.registrar_error(err, contexto="GestionReserva")
            return None
        else:
            self.logs.registrar_info(f"Reserva gestionada exitosamente -> {reserva_creada.obtener_resumen()}")
            return reserva_creada
        finally:
            # Auditoría de cierre de operación garantizada ante éxito o fallo.
            self.logs.registrar_info(f"Auditoría finalizada para intento de reserva [{id_reserva}].")
