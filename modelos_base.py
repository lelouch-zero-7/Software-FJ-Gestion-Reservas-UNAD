# -*- coding: utf-8 -*-
"""
Módulo 2: Clase Abstracta Base y Modelo de Cliente.
Proyecto: Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ.
Curso: Programación (213023) - UNAD.
"""

from abc import ABC, abstractmethod  # Importa herramientas para definir clases y métodos abstractos.
from datetime import datetime  # Importa datetime para registrar la fecha de creación de cada entidad.
import re  # Importa expresiones regulares para validar formatos de correo electrónico y documento.

# Importa las excepciones personalizadas del Módulo 1.
from excepciones_logs import ValidacionClienteError


# ==============================================================================
# 1. CLASE ABSTRACTA BASE DEL SISTEMA
# ==============================================================================

class EntidadSistema(ABC):
    """
    Clase abstracta que representa cualquier entidad general dentro de Software FJ
    (Clientes, Servicios, Reservas). Obliga a todas las subclases a implementar
    métodos estándar de identificación, validación y resumen de información.
    """

    def __init__(self, id_entidad: str):
        # Valida que el identificador de la entidad no sea nulo ni una cadena vacía.
        if not id_entidad or not isinstance(id_entidad, str) or not id_entidad.strip():
            raise ValueError("El identificador de la entidad debe ser una cadena de texto no vacía.")
        # Almacena el identificador limpio de espacios en un atributo protegido.
        self._id_entidad = id_entidad.strip()
        # Registra la marca de tiempo exacta en que se instanció el objeto.
        self._fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Define el estado activo por defecto de la entidad en memoria.
        self._activo = True

    @property
    def id_entidad(self) -> str:
        """Propiedad de solo lectura para consultar el ID único de la entidad."""
        return self._id_entidad

    @property
    def fecha_creacion(self) -> str:
        """Propiedad de solo lectura para consultar la fecha de registro."""
        return self._fecha_creacion

    @property
    def activo(self) -> bool:
        """Propiedad que indica si la entidad está habilitada operativamente."""
        return self._activo

    @activo.setter
    def activo(self, estado: bool) -> None:
        """Permite activar o desactivar la entidad verificando que sea un valor booleano."""
        if not isinstance(estado, bool):
            raise TypeError("El estado 'activo' debe ser un valor booleano (True o False).")
        self._activo = estado

    @abstractmethod
    def validar_datos(self) -> bool:
        """Método abstracto que cada subclase debe implementar para verificar su integridad."""
        pass

    @abstractmethod
    def obtener_resumen(self) -> str:
        """Método abstracto que retorna una descripción legible de la entidad."""
        pass


# ==============================================================================
# 2. CLASE CLIENTE CON ENCAPSULACIÓN Y VALIDACIONES ROBUSTAS
# ==============================================================================

class Cliente(EntidadSistema):
    """
    Representa un cliente de la empresa Software FJ.
    Hereda de EntidadSistema y aplica encapsulación estricta (atributos privados __)
    junto con validaciones de integridad y encadenamiento de excepciones.
    """

    def __init__(self, id_cliente: str, documento: str, nombre: str, correo: str, telefono: str):
        try:
            # Inicializa los atributos base heredados de EntidadSistema.
            super().__init__(id_cliente)
            # Asigna cada atributo a través de sus setters encapsulados para disparar validaciones.
            self.documento = documento
            self.nombre = nombre
            self.correo = correo
            self.telefono = telefono
            # Ejecuta la validación integral final del objeto recién construido.
            self.validar_datos()
        except (ValueError, TypeError) as err_tecnico:
            # Aplica encadenamiento de excepciones (raise ... from ...) conservando la causa original.
            raise ValidacionClienteError(
                f"Fallo al registrar el cliente '{nombre}': {err_tecnico}"
            ) from err_tecnico

    # --- Encapsulación del Documento de Identidad ---
    @property
    def documento(self) -> str:
        """Retorna el número de documento de identidad del cliente."""
        return self.__documento

    @documento.setter
    def documento(self, valor: str) -> None:
        """Valida que el documento sea numérico y tenga entre 6 y 15 dígitos."""
        if not isinstance(valor, str) or not valor.strip().isdigit():
            raise ValueError("El documento de identidad debe contener únicamente dígitos numéricos.")
        doc_limpio = valor.strip()
        if not (6 <= len(doc_limpio) <= 15):
            raise ValueError("El documento de identidad debe tener entre 6 y 15 dígitos.")
        self.__documento = doc_limpio

    # --- Encapsulación del Nombre Completo ---
    @property
    def nombre(self) -> str:
        """Retorna el nombre completo del cliente."""
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        """Valida que el nombre sea una cadena válida de al menos 3 caracteres."""
        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise ValueError("El nombre del cliente debe tener al menos 3 caracteres válidos.")
        self.__nombre = valor.strip().title()

    # --- Encapsulación del Correo Electrónico ---
    @property
    def correo(self) -> str:
        """Retorna el correo electrónico institucional o personal del cliente."""
        return self.__correo

    @correo.setter
    def correo(self, valor: str) -> None:
        """Valida el formato estándar del correo electrónico mediante expresión regular."""
        if not isinstance(valor, str):
            raise TypeError("El correo electrónico debe ser una cadena de texto.")
        correo_limpio = valor.strip().lower()
        patron_correo = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
        if not re.match(patron_correo, correo_limpio):
            raise ValueError(f"El formato del correo electrónico '{valor}' no es válido.")
        self.__correo = correo_limpio

    # --- Encapsulación del Teléfono de Contacto ---
    @property
    def telefono(self) -> str:
        """Retorna el número telefónico de contacto del cliente."""
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        """Valida que el teléfono contenga entre 7 y 15 dígitos numéricos."""
        if not isinstance(valor, str) or not valor.strip().isdigit():
            raise ValueError("El teléfono debe contener únicamente números sin espacios ni símbolos.")
        tel_limpio = valor.strip()
        if not (7 <= len(tel_limpio) <= 15):
            raise ValueError("El teléfono debe tener entre 7 y 15 dígitos.")
        self.__telefono = tel_limpio

    # --- Implementación de Métodos Abstractos ---
    def validar_datos(self) -> bool:
        """Verifica que todos los atributos privados del cliente estén correctamente poblados."""
        return all([
            bool(self.__documento),
            bool(self.__nombre),
            bool(self.__correo),
            bool(self.__telefono),
            self._activo
        ])

    def obtener_resumen(self) -> str:
        """Retorna una ficha resumida del cliente para reportes y logs."""
        estado = "Activo" if self._activo else "Inactivo"
        return (
            f"Cliente [{self.id_entidad}] | Doc: {self.__documento} | "
            f"Nombre: {self.__nombre} | Correo: {self.__correo} | "
            f"Tel: {self.__telefono} | Estado: {estado}"
        )

    def __str__(self) -> str:
        """Representación en cadena del objeto Cliente."""
        return self.obtener_resumen()
