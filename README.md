# Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ

Proyecto desarrollado para la **Fase 4 – Prácticas simuladas** del curso **Programación (213023 – Grupo 213023A_2204)** de la **Universidad Nacional Abierta y a Distancia (UNAD)**.

## Descripción General

Aplicación orientada a objetos construida en **Python 3** (sin uso de motores de bases de datos) para administrar en memoria los clientes, servicios especializados y reservas de **Software FJ**, garantizando continuidad operativa mediante manejo avanzado de excepciones, interfaz gráfica de usuario en **Tkinter** y auditoría persistente en archivo de logs.

## Arquitectura Modular del Proyecto

- `excepciones_logs.py`: Jerarquía de excepciones personalizadas (`SoftwareFJError`, `ValidacionClienteError`, `ServicioNoDisponibleError`, `ReservaInvalidaError`, `CalculoCostoError`) y gestor de registros en `sistema_software_fj.log`.
- `modelos_base.py`: Clase abstracta base `EntidadSistema` (`ABC`) y clase `Cliente` con encapsulación estricta (`@property`), validaciones y encadenamiento de excepciones (`raise ... from ...`).
- `servicios.py`: Clase abstracta `Servicio` y tres subclases especializadas (`ReservaSala`, `AlquilerEquipo`, `AsesoriaEspecializada`) aplicando polimorfismo y sobrecarga de métodos (`@singledispatchmethod`).
- `reservas.py`: Clase `Reserva` (gestión de estados `PENDIENTE`, `CONFIRMADA`, `PROCESADA`, `CANCELADA`) y controlador central `GestorSoftwareFJ` con listas en memoria y bloques `try/except/else/finally`.
- `main.py`: Simulación secuencial de 12 operaciones completas (casos válidos e inválidos) en consola que demuestran estabilidad sin interrupciones.
- `interfaz_tkinter.py`: Interfaz gráfica de usuario (GUI) desarrollada con la librería estándar `tkinter` (`ttk`) que permite gestionar clientes, servicios y reservas de forma interactiva, ejecutar las 12 simulaciones y visualizar en tiempo real el archivo `sistema_software_fj.log`.

## Ejecución

### 1. Interfaz Gráfica de Usuario (Tkinter)
```bash
python interfaz_tkinter.py
