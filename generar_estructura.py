#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
from pathlib import Path
from datetime import datetime

def generar_estructura(directorio_inicio, archivo_salida="estructura_directorios.txt", 
					mostrar_archivos=True, nivel_maximo=None, excluir_dirs=None):
	"""
	Genera la estructura de directorios en un archivo de texto.
	
	Args:
		directorio_inicio: Directorio desde donde comenzar
		archivo_salida: Nombre del archivo de salida
		mostrar_archivos: Si True, incluye archivos en la estructura
		nivel_maximo: Número máximo de niveles a mostrar (None = todos)
		excluir_dirs: Lista de directorios a excluir (ej: ['.git', '__pycache__'])
	"""
	if excluir_dirs is None:
		excluir_dirs = ['.git', '__pycache__', '.venv', 'venv', 'node_modules', '.idea', '.vscode']
	
	directorio_inicio = Path(directorio_inicio).resolve()
	
	if not directorio_inicio.exists():
		print(f"Error: El directorio '{directorio_inicio}' no existe.")
		return False
	
	if not directorio_inicio.is_dir():
		print(f"Error: '{directorio_inicio}' no es un directorio.")
		return False
	
	print(f"Generando estructura desde: {directorio_inicio}")
	print(f"Archivo de salida: {archivo_salida}")
	
	try:
		with open(archivo_salida, 'w', encoding='utf-8') as f:
			# Escribir encabezado
			f.write(f"Estructura de directorios generada desde: {directorio_inicio}\n")
			f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
			f.write("=" * 60 + "\n\n")
			
			# Generar estructura recursivamente
			def recorrer_directorio(directorio, prefijo="", nivel=0):
				if nivel_maximo is not None and nivel >= nivel_maximo:
					return
				
				try:
					# Obtener todos los elementos y ordenarlos (directorios primero)
					elementos = []
					for item in directorio.iterdir():
						if item.name not in excluir_dirs:
							elementos.append(item)
					
					# Ordenar: directorios primero, luego archivos, alfabéticamente
					elementos.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
					
					for i, elemento in enumerate(elementos):
						es_ultimo = (i == len(elementos) - 1)
						
						if elemento.is_dir():
							# Icono para directorio
							f.write(f"{prefijo}{'└── ' if es_ultimo else '├── '}📁 {elemento.name}/\n")
							
							# Nuevo prefijo para el siguiente nivel
							nuevo_prefijo = prefijo + ("    " if es_ultimo else "│   ")
							recorrer_directorio(elemento, nuevo_prefijo, nivel + 1)
						
						elif mostrar_archivos:
							# Icono para archivo
							icono = "📄"  # Archivo normal
							extension = elemento.suffix.lower()
							
							# Diferentes iconos según la extensión
							iconos_especiales = {
								'.py': '🐍', '.js': '📜', '.html': '🌐', '.css': '🎨',
								'.json': '📋', '.xml': '📑', '.txt': '📝', '.md': '📖',
								'.jpg': '🖼️', '.png': '🖼️', '.gif': '🖼️', '.pdf': '📕',
								'.zip': '📦', '.exe': '⚙️', '.sql': '🗃️', '.csv': '📊'
							}
							icono = iconos_especiales.get(extension, '📄')
							
							f.write(f"{prefijo}{'└── ' if es_ultimo else '├── '}{icono} {elemento.name}\n")
				
				except PermissionError:
					f.write(f"{prefijo}⚠️  [Acceso denegado]\n")
				except Exception as e:
					f.write(f"{prefijo}⚠️  [Error: {str(e)}]\n")
			
			recorrer_directorio(directorio_inicio)
		
		print(f"✓ Estructura guardada en '{archivo_salida}'")
		return True
		
	except Exception as e:
		print(f"✗ Error al generar el archivo: {e}")
		return False

def main():
	parser = argparse.ArgumentParser(
		description='Genera un archivo de texto con la estructura de directorios.'
	)
	
	parser.add_argument(
		'directorio', 
		nargs='?', 
		default='.',
		help='Directorio inicial (por defecto: directorio actual)'
	)
	
	parser.add_argument(
		'-o', '--output',
		default='estructura_directorios.txt',
		help='Nombre del archivo de salida (por defecto: estructura_directorios.txt)'
	)
	
	parser.add_argument(
		'-nf', '--no-files',
		action='store_true',
		help='No incluir archivos, solo directorios'
	)
	
	parser.add_argument(
		'-l', '--level',
		type=int,
		help='Nivel máximo de profundidad'
	)
	
	parser.add_argument(
		'-e', '--exclude',
		nargs='+',
		help='Directorios a excluir (separados por espacios)'
	)
	
	parser.add_argument(
		'-s', '--simple',
		action='store_true',
		help='Usar símbolos simples (sin emojis)'
	)
	
	args = parser.parse_args()
	
	# Si se usa --simple, desactivamos los emojis (aunque nuestro script no los usa directamente)
	if args.simple:
		print("Modo simple activado")
	
	excluir = args.exclude if args.exclude else None
	
	# Generar estructura
	generar_estructura(
		directorio_inicio=args.directorio,
		archivo_salida=args.output,
		mostrar_archivos=not args.no_files,
		nivel_maximo=args.level,
		excluir_dirs=excluir
	)

if __name__ == "__main__":
	main()


''' Modo de uso:

#-- Estructura del directorio actual:
python generar_estructura.py

#-- Estructura de un directorio específico:
python generar_estructura.py /ruta/al/directorio

#-- Especificar archivo de salida:
python generar_estructura.py -o mi_estructura.txt

#-- Solo directorios (sin archivos):
python generar_estructura.py --no-files

#-- Limitar profundidad a 3 niveles:
python generar_estructura.py -l 3

#-- Excluir directorios específicos:
python generar_estructura.py -e .git node_modules __pycache__

#-- Ver todas las opciones:
python generar_estructura.py --help

'''