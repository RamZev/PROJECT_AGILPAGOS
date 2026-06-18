# neumatic\entorno\constantes_base.py

# -- Datos estándares aplicables a los modelos base
ESTATUS_GEN = [
	(True, 'Activo'),
	(False, 'Inactivo'),
]

TIPO_PERSONA = [
	("F", 'Física'),
	("J", 'Jurídica'),
]

TIPO_CUENTA = [
	("C", 'Comun'),
	("E", 'Especial'),
	("D", 'Diferencial'),
]

BLACK_LIST = [
	(True, 'Si'),
	(False, 'No'),
]

ESTATUS_CHOICES = [ 
	('activos', 'Activos'),
	('inactivos', 'Inactivos'), 
	('todos', 'Todos'), 
]

MESES = [
		('01', 'Enero'),
		('02', 'Febrero'),
		('03', 'Marzo'),
		('04', 'Abril'),
		('05', 'Mayo'),
		('06', 'Junio'),
		('07', 'Julio'),
		('08', 'Agosto'),
		('09', 'Septiembre'),
		('10', 'Octubre'),
		('11', 'Noviembre'),
		('12', 'Diciembre'),
	]
