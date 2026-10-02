# homemutual\data_load\catalogos_migra.py
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

from apps.maestros.models.sg_catalogo_models import (
    SgNacionalidad,
    SgProvincia,
    SgEstadoCivil,
    SgCondicionFiscal,
    SgOcupacion,
    SgMotivoPEP,
)

# Mapeo de nombres de tabla a sus modelos y campos de ID
MODEL_MAP = {
    'nacionalidades': {
        'model': SgNacionalidad,
        'id_field': 'id_sg_nacionalidad',
        'estatus_field': 'estatus_sg_nacionalidad',
        'json_id_key': 'idWeb',
        'json_desc_key': 'descripcion',
        'table_name': 'sg_nacionalidad'
    },
    'provincias': {
        'model': SgProvincia,
        'id_field': 'id_sg_provincia',
        'estatus_field': 'estatus_sg_provincia',
        'json_id_key': 'idProvincia',
        'json_data_keys': ['codigoIsoProvincia', 'nombreProvincia', 'idPais', 'nombrePais'],
        'table_name': 'sg_provincia'
    },
    'estados_civiles': {
        'model': SgEstadoCivil,
        'id_field': 'id_sg_estado_civil',
        'estatus_field': 'estatus_sg_estado_civil',
        'json_id_key': 'id',
        'json_desc_key': 'descripcion',
        'table_name': 'sg_estado_civil'
    },
    'condiciones_fiscales': {
        'model': SgCondicionFiscal,
        'id_field': 'id_sg_condicion_fiscal',
        'estatus_field': 'estatus_sg_condicion_fiscal',
        'json_id_key': 'idWeb',
        'json_desc_key': 'descripcion',
        'table_name': 'sg_condicion_fiscal'
    },
    'ocupaciones': {
        'model': SgOcupacion,
        'id_field': 'id_sg_ocupacion',
        'estatus_field': 'estatus_sg_ocupacion',
        'json_id_key': 'id',
        'json_desc_key': 'descripcion',
        'table_name': 'sg_ocupacion'
    },
    'motivos_pep': {
        'model': SgMotivoPEP,
        'id_field': 'id_sg_motivo_pep',
        'estatus_field': 'estatus_sg_motivo_pep',
        'json_id_key': 'idWeb',
        'json_desc_key': 'descripcion',
        'table_name': 'sg_motivo_pep'
    }
}


def reset_table(table_name):
    """Elimina los datos existentes en la tabla y resetea su ID si es autoincrementable."""
    # Los modelos usan CharField como PK, no hay autoincrement
    # Pero eliminamos los registros igual
    engine = settings.DATABASES['default']['ENGINE']
    
    with connection.cursor() as cursor:
        try:
            cursor.execute(f"DELETE FROM {table_name};")
            print(f"Tabla {table_name} limpiada.")
        except Exception as e:
            print(f"  [ADVERTENCIA] No se pudo limpiar la tabla {table_name}: {e}")


def cargar_nacionalidades(data, dry_run=False):
    """Carga las nacionalidades desde el JSON."""
    print("\n=== Cargando Nacionalidades ===")
    
    if not dry_run:
        reset_table(MODEL_MAP['nacionalidades']['table_name'])
    
    records = data.get('nacionalidades', [])
    total = len(records)
    creados = 0
    
    for idx, record in enumerate(records, 1):
        id_value = record.get('idWeb', '').strip()
        descripcion = record.get('descripcion', '').strip()
        
        if not id_value or not descripcion:
            print(f"  [AVISO] Registro {idx} ignorado: datos incompletos")
            continue
        
        if dry_run:
            print(f"  {idx}. ID: {id_value}, Descripción: {descripcion}, Estatus: True (1)")
            creados += 1
        else:
            try:
                # Usamos el valor por defecto True (1) para el estatus
                SgNacionalidad.objects.create(
                    id_sg_nacionalidad=id_value,
                    # estatus_sg_nacionalidad=True,  # No es necesario porque el default es True
                    descripcion=descripcion
                )
                creados += 1
                if creados % 50 == 0:
                    print(f"  Progreso: {creados}/{total}")
            except Exception as e:
                print(f"  [ERROR] Falló al crear nacionalidad {id_value}: {e}")
    
    print(f"✅ Nacionalidades cargadas: {creados}/{total}")


def cargar_provincias(data, dry_run=False):
    """Carga las provincias desde el JSON."""
    print("\n=== Cargando Provincias ===")
    
    if not dry_run:
        reset_table(MODEL_MAP['provincias']['table_name'])
    
    records = data.get('provincias', [])
    total = len(records)
    creados = 0
    
    for idx, record in enumerate(records, 1):
        id_value = record.get('idProvincia', '').strip()
        codigo_iso = record.get('codigoIsoProvincia', '').strip()
        nombre = record.get('nombreProvincia', '').strip()
        id_pais = record.get('idPais', '').strip()
        nombre_pais = record.get('nombrePais', '').strip()
        
        if not id_value or not nombre:
            print(f"  [AVISO] Registro {idx} ignorado: datos incompletos")
            continue
        
        if dry_run:
            print(f"  {idx}. ID: {id_value}, Nombre: {nombre}, Código ISO: {codigo_iso}, Estatus: True (1)")
            creados += 1
        else:
            try:
                SgProvincia.objects.create(
                    id_sg_provincia=id_value,
                    # estatus_sg_provincia=True,  # No es necesario porque el default es True
                    codigo_iso=codigo_iso or None,
                    nombre_provincia=nombre,
                    id_pais=id_pais or '',
                    nombre_pais=nombre_pais or None
                )
                creados += 1
                if creados % 50 == 0:
                    print(f"  Progreso: {creados}/{total}")
            except Exception as e:
                print(f"  [ERROR] Falló al crear provincia {id_value}: {e}")
    
    print(f"✅ Provincias cargadas: {creados}/{total}")


def cargar_estados_civiles(data, dry_run=False):
    """Carga los estados civiles desde el JSON."""
    print("\n=== Cargando Estados Civiles ===")
    
    if not dry_run:
        reset_table(MODEL_MAP['estados_civiles']['table_name'])
    
    records = data.get('estados_civiles', [])
    total = len(records)
    creados = 0
    
    for idx, record in enumerate(records, 1):
        id_value = record.get('id', '').strip()
        descripcion = record.get('descripcion', '').strip()
        
        if not id_value or not descripcion:
            print(f"  [AVISO] Registro {idx} ignorado: datos incompletos")
            continue
        
        if dry_run:
            print(f"  {idx}. ID: {id_value}, Descripción: {descripcion}, Estatus: True (1)")
            creados += 1
        else:
            try:
                SgEstadoCivil.objects.create(
                    id_sg_estado_civil=id_value,
                    # estatus_sg_estado_civil=True,  # No es necesario porque el default es True
                    descripcion=descripcion
                )
                creados += 1
            except Exception as e:
                print(f"  [ERROR] Falló al crear estado civil {id_value}: {e}")
    
    print(f"✅ Estados Civiles cargados: {creados}/{total}")


def cargar_condiciones_fiscales(data, dry_run=False):
    """Carga las condiciones fiscales desde el JSON."""
    print("\n=== Cargando Condiciones Fiscales ===")
    
    if not dry_run:
        reset_table(MODEL_MAP['condiciones_fiscales']['table_name'])
    
    records = data.get('condiciones_fiscales', [])
    total = len(records)
    creados = 0
    
    for idx, record in enumerate(records, 1):
        id_value = record.get('idWeb', '').strip()
        descripcion = record.get('descripcion', '').strip()
        
        if not id_value or not descripcion:
            print(f"  [AVISO] Registro {idx} ignorado: datos incompletos")
            continue
        
        if dry_run:
            print(f"  {idx}. ID: {id_value}, Descripción: {descripcion}, Estatus: True (1)")
            creados += 1
        else:
            try:
                SgCondicionFiscal.objects.create(
                    id_sg_condicion_fiscal=id_value,
                    # estatus_sg_condicion_fiscal=True,  # No es necesario porque el default es True
                    descripcion=descripcion
                )
                creados += 1
            except Exception as e:
                print(f"  [ERROR] Falló al crear condición fiscal {id_value}: {e}")
    
    print(f"✅ Condiciones Fiscales cargadas: {creados}/{total}")


def cargar_ocupaciones(data, dry_run=False):
    """Carga las ocupaciones desde el JSON."""
    print("\n=== Cargando Ocupaciones ===")
    
    if not dry_run:
        reset_table(MODEL_MAP['ocupaciones']['table_name'])
    
    records = data.get('ocupaciones', [])
    total = len(records)
    creados = 0
    
    for idx, record in enumerate(records, 1):
        id_value = record.get('id', '').strip()
        descripcion = record.get('descripcion', '').strip()
        
        if not id_value or not descripcion:
            print(f"  [AVISO] Registro {idx} ignorado: datos incompletos")
            continue
        
        if dry_run:
            print(f"  {idx}. ID: {id_value}, Descripción: {descripcion}, Estatus: True (1)")
            creados += 1
        else:
            try:
                SgOcupacion.objects.create(
                    id_sg_ocupacion=id_value,
                    # estatus_sg_ocupacion=True,  # No es necesario porque el default es True
                    descripcion=descripcion
                )
                creados += 1
            except Exception as e:
                print(f"  [ERROR] Falló al crear ocupación {id_value}: {e}")
    
    print(f"✅ Ocupaciones cargadas: {creados}/{total}")


def cargar_motivos_pep(data, dry_run=False):
    """Carga los motivos PEP desde el JSON."""
    print("\n=== Cargando Motivos PEP ===")
    
    if not dry_run:
        reset_table(MODEL_MAP['motivos_pep']['table_name'])
    
    records = data.get('motivos_pep', [])
    total = len(records)
    creados = 0
    
    for idx, record in enumerate(records, 1):
        id_value = record.get('idWeb', '').strip()
        descripcion = record.get('descripcion', '').strip()
        
        if not id_value or not descripcion:
            print(f"  [AVISO] Registro {idx} ignorado: datos incompletos")
            continue
        
        if dry_run:
            print(f"  {idx}. ID: {id_value}, Descripción: {descripcion}, Estatus: True (1)")
            creados += 1
        else:
            try:
                SgMotivoPEP.objects.create(
                    id_sg_motivo_pep=id_value,
                    # estatus_sg_motivo_pep=True,  # No es necesario porque el default es True
                    descripcion=descripcion
                )
                creados += 1
            except Exception as e:
                print(f"  [ERROR] Falló al crear motivo PEP {id_value}: {e}")
    
    print(f"✅ Motivos PEP cargados: {creados}/{total}")


def cargar_datos(archivo_json=None, dry_run=False, solo=None):
    """
    Función principal que carga todos los datos del JSON a los modelos.
    
    Args:
        archivo_json: Ruta al archivo JSON (por defecto: catalogos.json en el mismo directorio)
        dry_run: Si es True, solo muestra lo que se va a cargar sin hacer cambios
        solo: Lista de tablas a cargar (ej: ['nacionalidades', 'provincias'])
              Si es None, carga todas
    """
    if archivo_json is None:
        archivo_json = os.path.join(BASE_DIR, 'data_load', 'catalogos.json')
    
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
    
    print(f"\n📊 Datos encontrados:")
    print("-" * 40)
    total_registros = 0
    for key in ['nacionalidades', 'provincias', 'estados_civiles', 
                'condiciones_fiscales', 'ocupaciones', 'motivos_pep']:
        count = len(data.get(key, []))
        print(f"  {key}: {count} registros")
        total_registros += count
    print("-" * 40)
    print(f"  TOTAL: {total_registros} registros\n")
    
    if dry_run:
        print("⚠️  MODO DRY RUN - No se realizarán cambios en la base de datos\n")
    
    # Determinar qué cargar
    tablas_a_cargar = ['nacionalidades', 'provincias', 'estados_civiles', 
                       'condiciones_fiscales', 'ocupaciones', 'motivos_pep']
    
    if solo:
        if isinstance(solo, str):
            solo = [solo]
        tablas_a_cargar = [t for t in tablas_a_cargar if t in solo]
    
    # Función de mapeo para cargar cada tabla
    cargadores = {
        'nacionalidades': cargar_nacionalidades,
        'provincias': cargar_provincias,
        'estados_civiles': cargar_estados_civiles,
        'condiciones_fiscales': cargar_condiciones_fiscales,
        'ocupaciones': cargar_ocupaciones,
        'motivos_pep': cargar_motivos_pep,
    }
    
    print("🚀 Iniciando migración...\n")
    
    for tabla in tablas_a_cargar:
        if tabla in cargadores:
            cargadores[tabla](data, dry_run=dry_run)
    
    print("\n" + "="*50)
    print("✅ MIGRACIÓN COMPLETADA")
    print("="*50)


def verificar_datos():
    """Verifica cuántos registros hay en cada tabla."""
    print("\n" + "="*50)
    print("🔍 VERIFICACIÓN DE DATOS CARGADOS")
    print("="*50 + "\n")
    
    modelos = [
        (SgNacionalidad, 'Nacionalidades', 'estatus_sg_nacionalidad'),
        (SgProvincia, 'Provincias', 'estatus_sg_provincia'),
        (SgEstadoCivil, 'Estados Civiles', 'estatus_sg_estado_civil'),
        (SgCondicionFiscal, 'Condiciones Fiscales', 'estatus_sg_condicion_fiscal'),
        (SgOcupacion, 'Ocupaciones', 'estatus_sg_ocupacion'),
        (SgMotivoPEP, 'Motivos PEP', 'estatus_sg_motivo_pep'),
    ]
    
    print("📋 Conteo de registros:")
    print("-" * 40)
    total = 0
    for model, nombre, estatus_field in modelos:
        count = model.objects.count()
        # Contar los activos (estatus = True/1)
        activos = model.objects.filter(**{estatus_field: True}).count()
        inactivos = count - activos
        print(f"  {nombre}: {count} registros (Activos: {activos}, Inactivos: {inactivos})")
        total += count
    print("-" * 40)
    print(f"  TOTAL: {total} registros\n")
    
    # Mostrar algunos ejemplos
    print("📝 Ejemplos de registros:")
    print("-" * 40)
    for model, nombre, _ in modelos[:3]:  # Mostrar solo los primeros 3 modelos como ejemplo
        ejemplo = model.objects.first()
        if ejemplo:
            print(f"  {nombre}:")
            print(f"    ID: {ejemplo.pk}")
            print(f"    Descripción: {str(ejemplo)}")
            print(f"    Estatus: {'Activo' if getattr(ejemplo, 'estatus_sg_' + nombre.lower().replace(' ', '_')[:-1], True) else 'Inactivo'}")
            print()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Migrar catálogos desde JSON a Django',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  %(prog)s                          # Migración completa
  %(prog)s --dry-run                # Simulación sin guardar cambios
  %(prog)s --solo nacionalidades    # Cargar solo nacionalidades
  %(prog)s --solo provincias        # Cargar solo provincias
  %(prog)s --verificar              # Verificar datos cargados
  %(prog)s --archivo mi_archivo.json # Usar archivo específico
        """
    )
    
    parser.add_argument('--dry-run', action='store_true', 
                        help='Simula la migración sin hacer cambios en la BD')
    parser.add_argument('--archivo', type=str, 
                        help='Ruta al archivo JSON (default: data_load/catalogos.json)')
    parser.add_argument('--solo', type=str, 
                        help='Cargar solo una tabla específica (ej: nacionalidades)')
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