# homemutual/data_load/sgconstanteagilpagos_migra.py
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

from apps.maestros.models.sg_catalogo_models import SgConstanteAgilpagos


# ============================================================
# MODEL MAP
# ============================================================
MODEL_MAP = {
    'constantes_agilpagos': {
        'model': SgConstanteAgilpagos,
        'id_field': 'clave',
        'estatus_field': 'estatus_sg_constante_agilpagos',
        'json_id_key': 'clave',
        'json_valor_key': 'valor',
        'json_desc_key': 'descripcion',
        'table_name': 'sg_constante_agilpagos',
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
def cargar_constantes_agilpagos(data, dry_run=False):
    """Carga las constantes de Agilpagos desde el JSON."""
    print("\n=== Cargando Constantes Agilpagos ===")

    if not dry_run:
        reset_table(MODEL_MAP['constantes_agilpagos']['table_name'])

    records = data.get('constantes_agilpagos', [])
    total = len(records)
    creados = 0

    for idx, record in enumerate(records, 1):
        clave = record.get('clave', '').strip()
        valor = record.get('valor', '').strip()
        descripcion = record.get('descripcion', '').strip()

        if not clave or not valor or not descripcion:
            print(f"  [AVISO] Registro {idx} ignorado: datos incompletos")
            continue

        if dry_run:
            print(f"  {idx}. Clave: {clave}")
            print(f"      Valor: {valor}")
            print(f"      Descripción: {descripcion[:80]}...")
            print(f"      Estatus: True (1)")
            print()
            creados += 1
        else:
            try:
                SgConstanteAgilpagos.objects.create(
                    clave=clave,
                    valor=valor,
                    descripcion=descripcion,
                    # estatus_sg_constante_agilpagos=True,  # default=True
                )
                creados += 1
                print(f"  ✅ {clave}")
            except Exception as e:
                print(f"  [ERROR] Falló al crear constante {clave}: {e}")

    print(f"\n✅ Constantes Agilpagos cargadas: {creados}/{total}")


# ============================================================
# ORQUESTADOR
# ============================================================
def cargar_datos(archivo_json=None, dry_run=False, solo=None):
    """
    Función principal que carga todos los datos del JSON a los modelos.

    Args:
        archivo_json: Ruta al archivo JSON (default: data_load/sgconstanteagilpagos.json)
        dry_run: Si es True, solo muestra lo que se va a cargar sin hacer cambios
        solo: Lista de tablas a cargar (ej: ['constantes_agilpagos'])
              Si es None, carga todas
    """
    if archivo_json is None:
        archivo_json = os.path.join(BASE_DIR, 'data_load', 'sgconstanteagilpagos.json')

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
    for key in ['constantes_agilpagos']:
        count = len(data.get(key, []))
        print(f"  {key}: {count} registros")
        total_registros += count
    print("-" * 40)
    print(f"  TOTAL: {total_registros} registros\n")

    if dry_run:
        print("⚠️  MODO DRY RUN - No se realizarán cambios en la base de datos\n")

    # Determinar qué cargar
    tablas_a_cargar = ['constantes_agilpagos']
    if solo:
        if isinstance(solo, str):
            solo = [solo]
        tablas_a_cargar = [t for t in tablas_a_cargar if t in solo]

    # Mapeo de cargadores
    cargadores = {
        'constantes_agilpagos': cargar_constantes_agilpagos,
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
        (SgConstanteAgilpagos, 'Constantes Agilpagos', 'estatus_sg_constante_agilpagos'),
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
    for obj in SgConstanteAgilpagos.objects.all():
        estatus = "Activo" if obj.estatus_sg_constante_agilpagos else "Inactivo"
        print(f"  {obj.clave}")
        print(f"    Valor: {obj.valor}")
        print(f"    Descripción: {obj.descripcion}")
        print(f"    Estatus: {estatus}")
        print()


# ============================================================
# CLI
# ============================================================
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Migrar constantes de Agilpagos desde JSON a Django',
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
                        help='Ruta al archivo JSON (default: data_load/sgconstanteagilpagos.json)')
    parser.add_argument('--solo', type=str,
                        help='Cargar solo una tabla específica (ej: constantes_agilpagos)')
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