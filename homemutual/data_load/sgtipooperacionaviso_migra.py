# homemutual/data_load/sgtipooperacionaviso_migra.py
import os
import sys
import json
import django
from django.db import connection
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

# Añadir el directorio base del proyecto al sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homemutual.settings')
django.setup()

from apps.maestros.models.sg_catalogo_models import SgTipoOperacionAviso


# ============================================================
# MODEL MAP
# ============================================================
MODEL_MAP = {
    'tipos_operacion_aviso': {
        'model': SgTipoOperacionAviso,
        'id_field': 'id_sg_tipo_operacion_aviso',
        'estatus_field': 'estatus_sg_tipo_operacion_aviso',
        'json_id_key': 'id_tipo_operacion_aviso',
        'json_desc_key': 'descripcion',
        'table_name': 'sg_tipo_operacion_aviso',
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


# ============================================================
# CARGADOR PRINCIPAL
# ============================================================
def cargar_tipos_operacion_aviso(data, dry_run=False):
    """Carga los tipos de operación de aviso desde el JSON."""
    print("\n=== Cargando Tipos de Operación Aviso ===")

    if not dry_run:
        reset_table(MODEL_MAP['tipos_operacion_aviso']['table_name'])

    records = data.get('tipos_operacion_aviso', [])
    total = len(records)
    creados = 0

    for idx, record in enumerate(records, 1):
        id_value = record.get('id_tipo_operacion_aviso', '').strip()
        descripcion = record.get('descripcion', '').strip()

        if not id_value or not descripcion:
            print(f"  [AVISO] Registro {idx} ignorado: datos incompletos")
            continue

        if dry_run:
            print(f"  {idx}. ID: {id_value}")
            print(f"      Descripción: {descripcion}")
            print(f"      Estatus: True (1)")
            print()
            creados += 1
        else:
            try:
                SgTipoOperacionAviso.objects.create(
                    id_sg_tipo_operacion_aviso=id_value,
                    descripcion=descripcion,
                    # estatus_sg_tipo_operacion_aviso=True,  # default=True
                )
                creados += 1
                print(f"  ✅ {descripcion}")
            except Exception as e:
                print(f"  [ERROR] Falló al crear tipo de operación aviso {id_value}: {e}")

    print(f"\n✅ Tipos de Operación Aviso cargados: {creados}/{total}")


# ============================================================
# ORQUESTADOR
# ============================================================
def cargar_datos(archivo_json=None, dry_run=False, solo=None):
    """
    Función principal que carga todos los datos del JSON a los modelos.

    Args:
        archivo_json: Ruta al archivo JSON (default: data_load/sgtipooperacionaviso.json)
        dry_run: Si es True, solo muestra lo que se va a cargar sin hacer cambios
        solo: Lista de tablas a cargar (ej: ['tipos_operacion_aviso'])
              Si es None, carga todas
    """
    if archivo_json is None:
        archivo_json = os.path.join(BASE_DIR, 'data_load', 'sgtipooperacionaviso.json')

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
    for key in ['tipos_operacion_aviso']:
        count = len(data.get(key, []))
        print(f"  {key}: {count} registros")
        total_registros += count
    print("-" * 40)
    print(f"  TOTAL: {total_registros} registros\n")

    if dry_run:
        print("⚠️  MODO DRY RUN - No se realizarán cambios en la base de datos\n")

    # Determinar qué cargar
    tablas_a_cargar = ['tipos_operacion_aviso']
    if solo:
        if isinstance(solo, str):
            solo = [solo]
        tablas_a_cargar = [t for t in tablas_a_cargar if t in solo]

    # Mapeo de cargadores
    cargadores = {
        'tipos_operacion_aviso': cargar_tipos_operacion_aviso,
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
        (SgTipoOperacionAviso, 'Tipos de Operación Aviso', 'estatus_sg_tipo_operacion_aviso'),
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
    for obj in SgTipoOperacionAviso.objects.all():
        estatus = "Activo" if obj.estatus_sg_tipo_operacion_aviso else "Inactivo"
        print(f"  {obj.descripcion}")
        print(f"    ID: {obj.pk}")
        print(f"    Estatus: {estatus}")
        print()


# ============================================================
# CLI
# ============================================================
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Migrar tipos de operación aviso desde JSON a Django',
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
                        help='Ruta al archivo JSON (default: data_load/sgtipooperacionaviso.json)')
    parser.add_argument('--solo', type=str,
                        help='Cargar solo una tabla específica (ej: tipos_operacion_aviso)')
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