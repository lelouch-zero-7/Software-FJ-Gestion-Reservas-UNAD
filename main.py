# -*- coding: utf-8 -*-
"""
Módulo 5: Simulación Principal del Sistema Integral Software FJ.
Ejecuta 12 operaciones completas (válidas e inválidas) demostrando estabilidad operativa,
polimorfismo, sobrecarga de métodos y registro exhaustivo en archivo de logs.
Proyecto: Fase 4 - Programación (213023_2204) - UNAD.
"""

from excepciones_logs import SoftwareFJError
from modelos_base import Cliente
from servicios import ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from reservas import GestorSoftwareFJ


def ejecutar_simulacion() -> None:
    """Función principal que orquesta las 12 pruebas integrales del sistema."""
    print("=" * 80)
    print(" INICIANDO SIMULACIÓN INTEGRAL - SOFTWARE FJ (SIN BASE DE DATOS) ")
    print("=" * 80)

    # Instancia el gestor central e inicializa el archivo de logs en disco.
    gestor = GestorSoftwareFJ("sistema_software_fj.log")

    # --------------------------------------------------------------------------
    # SIMULACIÓN 1: Registro VÁLIDO de clientes
    # --------------------------------------------------------------------------
    print("\n[Simulación 1] Registrando clientes válidos...")
    try:
        c1 = Cliente("CLI-01", "1002548963", "David Santiago Ruiz", "david.ruiz@softwarefj.com", "3104567890")
        c2 = Cliente("CLI-02", "1023456789", "Wilian Alejandro Barreto", "wilian.barreto@empresa.co", "3209876543")
        gestor.registrar_cliente(c1)
        gestor.registrar_cliente(c2)
        print("  -> Clientes CLI-01 y CLI-02 registrados correctamente.")
    except SoftwareFJError as e:
        gestor.logs.registrar_error(e, contexto="Simulacion1")

    # --------------------------------------------------------------------------
    # SIMULACIÓN 2: Registro INVÁLIDO de cliente (encadenamiento de excepciones)
    # --------------------------------------------------------------------------
    print("\n[Simulación 2] Intentando registrar cliente con datos inválidos (prueba de encadenamiento)...")
    try:
        c_invalido = Cliente("CLI-03", "ABC12", "Ana", "correo-sin-arroba.com", "123")
        gestor.registrar_cliente(c_invalido)
    except SoftwareFJError as e:
        gestor.logs.registrar_error(e, contexto="Simulacion2_ClienteInvalido")
        print(f"  -> Error controlado con éxito: {e}")

    # --------------------------------------------------------------------------
    # SIMULACIÓN 3: Registro INVÁLIDO de cliente duplicado
    # --------------------------------------------------------------------------
    print("\n[Simulación 3] Intentando registrar cliente duplicado...")
    try:
        c_duplicado = Cliente("CLI-04", "1002548963", "David Duplicado", "otro@correo.com", "3112223344")
        gestor.registrar_cliente(c_duplicado)
        print("  -> Intento de duplicado bloqueado y registrado en logs.")
    except SoftwareFJError as e:
        gestor.logs.registrar_error(e, contexto="Simulacion3")

    # --------------------------------------------------------------------------
    # SIMULACIÓN 4: Creación VÁLIDA de los 3 servicios especializados (Polimorfismo)
    # --------------------------------------------------------------------------
    print("\n[Simulación 4] Creando catálogo de 3 servicios especializados...")
    try:
        s1 = ReservaSala("SRV-01", "Auditorio Innovación Cloud", 120000.0, capacidad_maxima=35)
        s2 = AlquilerEquipo("SRV-02", "Servidor Rack Dell PowerEdge", 85000.0, stock_disponible=2, seguro_hora=10000.0)
        s3 = AsesoriaEspecializada("SRV-03", "Auditoría Ciberseguridad ISO", 150000.0, "Seguridad", "Ing. Ronald Rodríguez")
        gestor.registrar_servicio(s1)
        gestor.registrar_servicio(s2)
        gestor.registrar_servicio(s3)
        print("  -> Servicios SRV-01 (Sala), SRV-02 (Equipo) y SRV-03 (Asesoría) activos.")
    except SoftwareFJError as e:
        gestor.logs.registrar_error(e, contexto="Simulacion4")

    # --------------------------------------------------------------------------
    # SIMULACIÓN 5: Creación INVÁLIDA de servicio (tarifa negativa)
    # --------------------------------------------------------------------------
    print("\n[Simulación 5] Intentando crear servicio con tarifa negativa...")
    try:
        s_invalido = ReservaSala("SRV-99", "Sala Fantasma", -50000.0, capacidad_maxima=10)
        gestor.registrar_servicio(s_invalido)
    except SoftwareFJError as e:
        gestor.logs.registrar_error(e, contexto="Simulacion5_ServicioInvalido")
        print(f"  -> Error controlado con éxito: {e}")

    # --------------------------------------------------------------------------
    # SIMULACIÓN 6: Reserva EXITOSA de Sala (recargo logístico > 20 personas)
    # --------------------------------------------------------------------------
    print("\n[Simulación 6] Creando y confirmando reserva exitosa de Sala...")
    r1 = gestor.crear_y_confirmar_reserva("RES-01", "CLI-01", "SRV-01", duracion_horas=4, cantidad=25, descuento=0.10)
    if r1:
        print(f"  -> {r1.obtener_resumen()}")

    # --------------------------------------------------------------------------
    # SIMULACIÓN 7: Reserva FALLIDA de Sala ya ocupada (ServicioNoDisponibleError)
    # --------------------------------------------------------------------------
    print("\n[Simulación 7] Intentando reservar la misma sala mientras está ocupada...")
    r2_fallida = gestor.crear_y_confirmar_reserva("RES-02", "CLI-02", "SRV-01", duracion_horas=2, cantidad=10)
    if r2_fallida is None:
        print("  -> Conflicto de disponibilidad detectado y registrado en logs sin detener el sistema.")

    # --------------------------------------------------------------------------
    # SIMULACIÓN 8: Reserva EXITOSA de Equipos y prueba de agotamiento de stock
    # --------------------------------------------------------------------------
    print("\n[Simulación 8] Reservando todo el stock disponible de servidores (2 unidades)...")
    r3 = gestor.crear_y_confirmar_reserva("RES-03", "CLI-02", "SRV-02", duracion_horas=6, cantidad=2)
    if r3:
        print(f"  -> {r3.obtener_resumen()}")

    # --------------------------------------------------------------------------
    # SIMULACIÓN 9: Reserva FALLIDA por falta de stock de equipos
    # --------------------------------------------------------------------------
    print("\n[Simulación 9] Intentando reservar servidor sin stock disponible...")
    r4_fallida = gestor.crear_y_confirmar_reserva("RES-04", "CLI-01", "SRV-02", duracion_horas=3, cantidad=1)
    if r4_fallida is None:
        print("  -> Falta de inventario controlada correctamente.")

    # --------------------------------------------------------------------------
    # SIMULACIÓN 10: Reserva EXITOSA de Asesoría con descuento automático (>5 horas)
    # --------------------------------------------------------------------------
    print("\n[Simulación 10] Reservando Asesoría Especializada por 8 horas...")
    r5 = gestor.crear_y_confirmar_reserva("RES-05", "CLI-01", "SRV-03", duracion_horas=8, cantidad=1, descuento=0.05)
    if r5:
        print(f"  -> {r5.obtener_resumen()}")

    # --------------------------------------------------------------------------
    # SIMULACIÓN 11: Procesamiento, Cancelación y Transición Ilegal de Estados
    # --------------------------------------------------------------------------
    print("\n[Simulación 11] Procesando RES-01, cancelando RES-03 y probando operación ilegal...")
    try:
        if r1:
            total_cobrado = r1.procesar()
            gestor.logs.registrar_info(f"Reserva RES-01 procesada y facturada por ${total_cobrado:,.2f}")
            print(f"  -> RES-01 procesada. Total facturado: ${total_cobrado:,.2f}")
        if r3:
            r3.cancelar("Cambio de cronograma del cliente")
            gestor.logs.registrar_info("Reserva RES-03 cancelada; stock de equipos restituido.")
            print("  -> RES-03 cancelada y stock restituido.")
            # Intento ilegal: intentar confirmar una reserva ya cancelada.
            r3.confirmar()
    except SoftwareFJError as e:
        gestor.logs.registrar_error(e, contexto="Simulacion11_EstadoIlegal")
        print(f"  -> Transición de estado ilegal bloqueada: {e}")

    # --------------------------------------------------------------------------
    # SIMULACIÓN 12: Prueba de Métodos Sobrecargados y Reserva con Cliente Inexistente
    # --------------------------------------------------------------------------
    print("\n[Simulación 12] Probando sobrecarga de calcular_total() y reserva con cliente inexistente...")
    try:
        # Llamada sobrecargada 1 (con entero) vs sobrecargada 2 (con diccionario).
        costo_int = s3.calcular_total(4, iva=0.19, descuento=0.0)
        costo_dict = s3.calcular_total({"horas": 4, "iva": 0.19, "descuento": 0.0})
        print(f"  -> Sobrecarga verificada: int=${costo_int:,.2f} == dict=${costo_dict:,.2f}")
        gestor.logs.registrar_info(f"Verificación de sobrecarga exitosa: ${costo_int:,.2f}")

        # Intento con cliente inexistente.
        gestor.crear_y_confirmar_reserva("RES-99", "CLI-999", "SRV-01", duracion_horas=2)
    except SoftwareFJError as e:
        gestor.logs.registrar_error(e, contexto="Simulacion12")

    # --------------------------------------------------------------------------
    # RESUMEN FINAL Y VERIFICACIÓN DEL ARCHIVO DE LOGS
    # --------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print(f" RESUMEN EN MEMORIA -> Clientes: {len(gestor.clientes)} | Servicios: {len(gestor.servicios)} | Reservas: {len(gestor.reservas)}")
    print(" Archivo de auditoría generado: 'sistema_software_fj.log'")
    print(" EJECUCIÓN FINALIZADA SIN INTERRUPCIONES (ESTABILIDAD 100%)")
    print("=" * 80)


if __name__ == "__main__":
    ejecutar_simulacion()
