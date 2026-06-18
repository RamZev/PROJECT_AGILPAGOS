//-- Este es el JavaScript personalizado principal para Neumatic --//

window.addEventListener('DOMContentLoaded', event => {
	
	// ---------------------------------------------------------------------------
	// Funcionalidad para Manejo de campos(inputs) decimales.
	// ---------------------------------------------------------------------------
	
	const decimalInputs = document.querySelectorAll('.decimal-input');
	if (decimalInputs) {
		decimalInputs.forEach(input => {
			let numericValue = '0';
			let decimalMode = false;
			//let isNegative = false;
			let isAllSelected = false;
			
			// Configuración inicial basada en el valor existente
			if (input.value && input.value !== '0') {
				let initialValue = input.value;
				//isNegative = initialValue.startsWith('-');
				if (initialValue.includes(',')) {
					// Valor en formato local, ej: "1.250,35"
					numericValue = initialValue.replace(/\./g, '').replace(',', '.');
					decimalMode = true;
				} else {
					// Valor en formato backend, ej: "1250.35"
					numericValue = initialValue;
					decimalMode = numericValue.includes('.') ? true : false;
				}
			}
			
			// Configuración inicial
			updateDisplay();
			
			input.addEventListener('keydown', function(e) {
				// Verificar selección actual
				isAllSelected = input.selectionStart === 0 && input.selectionEnd === input.value.length;
				
				// Manejar borrado completo cuando todo está seleccionado
				if (isAllSelected && (e.key === 'Delete' || e.key === 'Backspace')) {
					e.preventDefault();
					numericValue = '0';
					decimalMode = false;
					updateDisplay();
					input.select();
					return;
				}
				
				// Permitir otras teclas de control
				if ([8, 9, 13, 27, 37, 38, 39, 40].includes(e.keyCode) ||
					(e.ctrlKey && [65, 67, 86, 88].includes(e.keyCode))) {
					return;
				}
				
				// Permitir números, coma o punto
				if ((e.key >= '0' && e.key <= '9') || 
					e.key === ',' || e.key === '.' || 
					e.key === 'Backspace' || e.key === 'Delete') {
					return;
				}
				
				e.preventDefault();
			});
			
			input.addEventListener('input', function(e) {
				// Manejar borrado normal
				if (e.inputType.includes('delete') && !isAllSelected) {
					handleBackspace();
					updateDisplay();
					return;
				}
				
				// Manejar entrada de coma/punto
				if (e.data === ',' || e.data === '.') {
					if (!decimalMode) {
						decimalMode = true;
						if (numericValue.indexOf('.') === -1) {
							numericValue += '.';
						}
						updateDisplay(); // Mostrar coma inmediatamente
					}
					return;
				}
				
				// Manejar entrada numérica
				if (e.data >= '0' && e.data <= '9') {
					// Si todo está seleccionado, reemplazar el valor
					if (isAllSelected) {
						numericValue = e.data;
						decimalMode = false;
					} 
					// Modo decimal
					else if (decimalMode) {
						const decimalPart = numericValue.split('.')[1] || '';
						if (decimalPart.length < 2) {
							numericValue += e.data;
						}
					} 
					// Modo entero (comportamiento de calculadora)
					else {
						if (numericValue === '0') {
							numericValue = e.data;
						} else if (numericValue.indexOf('.') === -1) {
							numericValue += e.data;
						}
					}
					updateDisplay();
				}
			});
			
			input.addEventListener('mousedown', function() {
				isAllSelected = false;
			});
			
			input.addEventListener('focus', function() {
				// Mostrar valor sin formato de miles pero con coma decimal
				let display = numericValue.replace('.', ',');
				input.value = display;
				
				// Seleccionar todo
				input.select();
				isAllSelected = true;
			});
			
			input.addEventListener('blur', function() {
				// Si no hay valor, establecer a 0,00
				if (numericValue === '' || numericValue === '0') {
					numericValue = '0.00';
					input.value = '0,00';
					return;
				}
				
				// Completar decimales si es necesario
				const parts = numericValue.split('.');
				if (parts.length === 1) {
					// No hay decimales, agregar .00
					numericValue += '.00';
				} else if (parts[1].length === 1) {
					// Solo un decimal, agregar 0
					numericValue += '0';
				} else if (parts[1].length === 0) {
					// Solo el punto, agregar 00
					numericValue += '00';
				}
				
				decimalMode = false;
				updateDisplay();
			});
			
			function handleBackspace() {
				isAllSelected = false;
				
				const hasDecimal = numericValue.indexOf('.') !== -1;
				
				if (hasDecimal) {
					const decimalPart = numericValue.split('.')[1];
					// Si hay decimales, borrar el último
					if (decimalPart.length > 0) {
						numericValue = numericValue.slice(0, -1);
						// Si era el último decimal, quitar el punto también
						if (decimalPart.length === 1) {
							numericValue = numericValue.slice(0, -1);
							decimalMode = false;
						}
					}
					// Si no hay decimales pero hay punto, quitarlo
					else if (numericValue.endsWith('.')) {
						numericValue = numericValue.slice(0, -1);
						decimalMode = false;
					}
				} else if (numericValue.length > 1) {
					numericValue = numericValue.slice(0, -1);
				} else {
					numericValue = '0';
				}
			}
			
			function updateDisplay() {
				const parts = numericValue.split('.');
				let integerPart = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.');
				let decimalPart = parts[1] || '';
				
				// Mostrar diferente según el modo
				if (decimalMode) {
					// Modo decimal activo - mostrar coma siempre
					input.value = integerPart + ',' + decimalPart;
				} else if (decimalPart.length > 0) {
					// Tiene decimales - mostrar con coma
					input.value = integerPart + ',' + decimalPart;
				} else {
					// Valor entero - sin coma
					input.value = integerPart;
				}
			}
		});
		
		// Asegurar que el valor se envía con punto decimal
		document.querySelector('form').addEventListener('submit', function(e) {
			decimalInputs.forEach(input => {
				// Guardar el valor con formato en el dataset
				const formattedValue = input.value;
				
				// Transformar para el envío (sin guardar en dataset)
				input.value = input.value.replace(/\./g, '').replace(',', '.');
				
				// Restaurar inmediatamente el formato visual
				requestAnimationFrame(() => {
					input.value = formattedValue;
				});
			});
		});
	} 

});
