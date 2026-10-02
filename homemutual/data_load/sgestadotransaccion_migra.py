# homemutual/data_load/sgestadotransaccion_migra.py
import os
import sys
import json
import django
import unicodedata
from django.db import connection
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

# Añadir el directorio base del proyecto al sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homemutual.settings')
django.setup()

from apps.maestros.models.sg_catalogo_models import SgEstadoTransaccion


# ============================================================
# MODEL MAP
# ============================================================
MODEL_MAP = {
    'estados_transaccion': {
        'model': SgEstadoTransaccion,
        'id_field': 'id_sg_estado_transaccion',
        'estatus_field': 'estatus_sg_estado_transaccion',
        'json_id_key': 'id_estado_transaccion',
        'json_desc_key': 'descripcion',
        'json_es_final_key': 'es_final',
        'json_es_exitoso_key': 'es_exitoso',
        'table_name': 'sg_estado_transaccion',
    }
}


# ============================================================
# UTILIDADES
# ============================================================
def reset_table(table_name):
    """Elimina los datos existentes en la tabla."""
    with connection.cursor() as cursor:
        try:
            cursor.execute(f"DELETE FROM {table_name};")
            print(f"  🗑️  Tabla {table_name} limpiada.")
        except Exception as e:
            print(f"  [ADVERTENCIA] No se pudo limpiar la tabla {table_name}: {e}")


def quitar_tildes(texto):
    """Elimina las tildes de un texto."""
    if not texto:
        return ''
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )


def generar_codigo(descripcion):
    """
    Genera un código a partir de la descripción.
    Ejemplo: 'Pendiente' → 'PENDIENTE'
             'Informado Al Banco' → 'INFORMADO_AL_BANCO'
             'Pendiente Confirmación en Banco' → 'PENDIENTE_CONFIRMACION_EN_BANCO'
    """
    if not descripcion:
        return ''
    sin_tildes = quitar_tildes(descripcion.strip())
    return sin_tildes.upper().replace(' ', '_')


# ============================================================
# CARGADOR PRINCIPAL
# ============================================================
def cargar_estados_transaccion(data, dry_run=False):
    """Carga los estados de transacción desde el JSON."""
    print("\n=== Cargando Estados de Transacción ===")

    if not dry_run:
        reset_table(MODEL_MAP['estados_transaccion']['table_name'])

    records = data.get('estados_transaccion', [])
    total = len(records)
    creados = 0

    for idx, record in enumerate(records, 1):
        id_value = record.get('id_estado_transaccion', '').strip()
        descripcion = record.get('descripcion', '').strip()
        es_final = record.get('es_final', False)
        es_exitoso = record.get('es_exitoso', False)

        if not id_value or not descripcion:
            print(f"  [AVISO] Registro {idx} ignorado: datos incompletos")
            continue

        # Generar código a partir de la descripción
        codigo = generar_codigo(descripcion)

        if dry_run:
            print(f"  {idx}. ID: {id_value}")
            print(f"      Código: {codigo}")
            print(f"      Descripción: {descripcion}")
            print(f"      Es Final: {es_final}")
            print(f"      Es Exitoso: {es_exitoso}")
            print(f"      Estatus: True (1)")
            print()
            creados += 1
        else:
            try:
                SgEstadoTransaccion.objects.create(
                    id_sg_estado_transaccion=id_value,
                    codigo=codigo,
                    descripcion=descripcion,
                    es_final=es_final,
                    es_exitoso=es_exitoso,
                    # estatus_sg_estado_transaccion=True,  # default=True
                )
                creados += 1
                print(f"  ✅ {codigo} - {descripcion}")
            except Exception as e:
                print(f"  [ERROR] Falló al crear estado {codigo}: {e}")

    print(f"\n✅ Estados de Transacción cargados: {creados}/{total}")


# ============================================================
# ORQUESTADOR
# ============================================================
def cargar_datos(archivo_json=None, dry_run=False, solo=None):
    """
    Función principal que carga todos los datos del JSON a los modelos.

    Args:
        archivo_json: Ruta al archivo JSON (default: data_load/sgestadotransaccion.json)
        dry_run: Si es True, solo muestra lo que se va a cargar sin hacer cambios
        solo: Lista de tablas a cargar (ej: ['estados_transaccion'])
              Si es None, carga todas
    """
    if archivo_json is None:
        archivo_json = os.path.join(BASE_DIR, 'data_load', 'sgestadotransaccion.json')

    print(f"📂 Leyendo archivo: {archivo_json}")

    if not os.path.exists(archivo_json):
        print(f"❌ Error: El archivo {archivo_json} no existe.")
        return

    try:
        with open(archivo_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error al leer el JSON: {e}")
        return

    # Reporte de datos encontrados
    print(f"\n📊 Datos encontrados:")
    print("-" * 40)
    total_registros = 0
    for key in ['estados_transaccion']:
        count = len(data.get(key, []))
        print(f"  {key}: {count} registros")
        total_registros += count
    print("-" * 40)
    print(f"  TOTAL: {total_registros} registros\n")

    if dry_run:
        print("⚠️  MODO DRY RUN - No se realizarán cambios en la base de datos\n")

    # Determinar qué cargar
    tablas_a_cargar = ['estados_transaccion']
    if solo:
        if isinstance(solo, str):
            solo = [solo]
        tablas_a_cargar = [t for t in tablas_a_cargar if t in solo]

    # Mapeo de cargadores
    cargadores = {
        'estados_transaccion': cargar_estados_transaccion,
    }

    print("🚀 Iniciando migración...\n")

    for tabla in tablas_a_cargar:
        if tabla in cargadores:
            cargadores[tabla](data, dry_run=dry_run)

    print("\n" + "=" * 50)
    print("✅ MIGRACIÓN COMPLETADA")
    print("=" * 50)


# ============================================================
# VERIFICACIÓN
# ============================================================
def verificar_datos():
    """Verifica cuántos registros hay en la tabla."""
    print("\n" + "=" * 50)
    print("🔍 VERIFICACIÓN DE DATOS CARGADOS")
    print("=" * 50 + "\n")

    modelos = [
        (SgEstadoTransaccion, 'Estados de Transacción', 'estatus_sg_estado_transaccion'),
    ]

    print("📋 Conteo de registros:")
    print("-" * 40)
    total = 0
    for model, nombre, estatus_field in modelos:
        count = model.objects.count()
        activos = model.objects.filter(**{estatus_field: True}).count()
        inactivos = count - activos
        print(f"  {nombre}: {count} registros (Activos: {activos}, Inactivos: {inactivos})")
        total += count
    print("-" * 40)
    print(f"  TOTAL: {total} registros\n")

    # Mostrar todos los registros
    print("📝 Registros cargados:")
    print("-" * 40)
    for obj in SgEstadoTransaccion.objects.all():
        estatus = "Activo" if obj.estatus_sg_estado_transaccion else "Inactivo"
        print(f"  {obj.codigo} - {obj.descripcion}")
        print(f"    ID: {obj.pk}")
        print(f"    Es Final: {obj.es_final}")
        print(f"    Es Exitoso: {obj.es_exitoso}")
        print(f"    Estatus: {estatus}")
        print()


# ============================================================
# CLI
# ============================================================
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Migrar estados de transacción desde JSON a Django',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  %(prog)s                              # Migración completa
  %(prog)s --dry-run                    # Simulación sin guardar cambios
  %(prog)s --verificar                  # Verificar datos cargados
  %(prog)s --archivo mi_archivo.json    # Usar archivo específico
        """
    )

    parser.add_argument('--dry-run', action='store_true',
                        help='Simula la migración sin hacer cambios en la BD')
    parser.add_argument('--archivo', type=str,
                        help='Ruta al archivo JSON (default: data_load/sgestadotransaccion.json)')
    parser.add_argument('--solo', type=str,
                        help='Cargar solo una tabla específica (ej: estados_transaccion)')
    parser.add_argument('--verificar', action='store_true',
                        help='Verifica los datos cargados en la base de datos')

    args = parser.parse_args()

    if args.verificar:
        verificar_datos()
    else:
        cargar_datos(
            archivo_json=args.archivo,
            dry_run=args.dry_run,
            solo=args.solo
        )
        if not args.dry_run:
            verificar_datos()