//-- neumatic\static\js\opciones_reporte.js

//---------------------------------------------------------------------------
//-- Función para llenar localidades basadas en la provincia seleccionada.
//---------------------------------------------------------------------------
const updateLocalidades = async (provinciaId) => {
	const localidadSelect = document.querySelector('[name="localidad"]');
	
	//-- Limpiar el select de localidades.
	localidadSelect.innerHTML = '<option value="">Selecciones una localidad...</option>';
	
	if (!provinciaId) {
		return;
	}
	
	try {
		//-- Llamada a la vista para obtener las localidades filtradas por provincia.
		const url = `/informes/filtrar-localidad/?id_provincia=${provinciaId}`;
		const response = await fetch(url);
		
		if (response.ok) {
			const data = await response.json();
			
			const localidades = data.localidad;
			//-- Rellenar el select con las localidades obtenidas.
			localidades.forEach(localidad => {
				const option = document.createElement("option");
				option.value = localidad.id_localidad;
				option.textContent = localidad.nombre_completo;
				localidadSelect.appendChild(option);
			});
		} else {
			console.log("Error al obtener localidades:", response.statusText);
		}
		
	} catch (error) {
		console.log("Error en la petición de localidades:", error);
	}
};

//-- Event listener para el select de provincias.
const provinciaSelect = document.querySelector('[name="provincia"]');
if (provinciaSelect) {
	provinciaSelect.addEventListener("change", function () {
		const selectedProvincia = this.value;
		updateLocalidades(selectedProvincia);
	});
}

//---------------------------------------------------------------------------
//-- Función para manejar la lógica de habilitar/deshabilitar y seleccionar
//-- automáticamente PDF.
//---------------------------------------------------------------------------
const selectAllFormats = () => {
	const formatCheckboxes = document.querySelectorAll('[name="formato_envio"]');
	
	//-- Variable especifica para marcar por defecto el formato PDF.
	const pdfCheckbox = document.querySelector('[name="formato_envio"][value="pdf"]');
	const emailField = document.getElementById("email");
	const celularField = document.getElementById("celular");
	const selectedOption = document.querySelector('input[name="tipo_salida"]:checked').value;
	
	formatCheckboxes.forEach((checkbox) => {
		
		//-- Deshabilitar o habilitar los checkboxes según la selección.
		checkbox.disabled = selectedOption === "pantalla" || selectedOption === "pdf_preliminar" || selectedOption === "excel_preliminar" || selectedOption === "csv_preliminar";
		if (checkbox.disabled) {
			checkbox.checked = false; //-- Desmarcar si están deshabilitados.
			emailField.value = "";
			celularField.value = "";
		}
	});
	
	//-- Habilitar/deshabilitar campos según la opción seleccionada.
	emailField.disabled = selectedOption !== "email";
	celularField.disabled = selectedOption !== "whatsapp";
	
	//-- Seleccionar el checkbox de PDF si se elige "email" o "whatsapp".
	if (selectedOption === "email" || selectedOption === "whatsapp") {
		pdfCheckbox.checked = true;
	}
};

//-- Inicializar el estado por defecto.
const initializeDefaults = () => {
	const formatCheckboxes = document.querySelectorAll('[name="formato_envio"]');
	const emailField = document.getElementById("email");
	const celularField = document.getElementById("celular");
	
	//-- Deshabilitar checkboxes.
	formatCheckboxes.forEach((checkbox) => {
		checkbox.disabled = true;
		checkbox.checked = false;
	});
	
	//-- Deshabilitar los campos de envio.
	emailField.disabled = true;
	celularField.disabled = true;
};

//-- evento 'change' para los cambios.
const radios = document.querySelectorAll('input[name="tipo_salida"]');
radios.forEach(radio => {
    radio.removeEventListener("change", selectAllFormats); // Evita duplicados
    radio.addEventListener("change", selectAllFormats);
});

//-- cargar la página.
const vistaPantalla = document.querySelector('input[name="tipo_salida"][value="pantalla"]');
if (vistaPantalla) {
	vistaPantalla.checked = true; //-- Seleccionar Vista Preliminar en Tabla por defecto.
}
initializeDefaults();


//-- Script adicional para el botón "Generar".
const btnGenerar = document.getElementById("generar");

btnGenerar.addEventListener("click", async function (e) {
	e.preventDefault();  //-- Prevenir el envío normal del formulario.
	
	try {
		const form = document.getElementById("formulario");
		const formData = new FormData(form);
		const params = new URLSearchParams(formData).toString();
		
		//-- Obtener la URL base sin parámetros existentes.
		const baseUrl = form.action.split('?')[0];  //-- Tomar solo la parte antes del ?.
		const url = baseUrl + "?" + params;
		
		//-- Se hace la petición AJAX, enviando el header que indica petición AJAX.
		const response = await fetch(url, {
			headers: { "X-Requested-With": "XMLHttpRequest" }
		});
		if (!response.ok) {
			throw new Error("Error en la respuesta del servidor: " + response.statusText);
		}
		const data = await response.json();
		if (data.success) {
			window.open(data.url, "_blank");
		} else {
			//-- Remover el modal existente.
			const oldModal = document.getElementById("errorModal");
			if (oldModal) {
				oldModal.remove();
			}
			//-- Insertar el nuevo HTML del modal al final del body.
			document.body.insertAdjacentHTML('beforeend', data.html);
			//-- Crear una nueva instancia del modal y mostrarlo.
			const newErrorModal = new bootstrap.Modal(document.getElementById('errorModal'));
			newErrorModal.show();
		}
	} catch (error) {
		console.error("Error en la petición:", error);
		//-- Opcional: Mostrar mensaje al usuario.
		alert("Ocurrió un error al procesar la solicitud");
	}
});

//---------------------------------------------------------------------------
//-- Funcionalidad para mostrar modal con los errores de validación
//-- del formulario.
//---------------------------------------------------------------------------
const errorModal = new bootstrap.Modal(document.getElementById('errorModal'));
const modalElement = document.getElementById('errorModal');
const hasErrors = modalElement.dataset.hasErrors === "true";

//-- Mostrar el modal si hay errores.
if (hasErrors) {
	errorModal.show();
}

//-- Validación en tiempo real: remover clases al escribir.
//-- Seleccionar inputs y selects.
var inputs = document.querySelectorAll('input, select');
inputs.forEach(function (input) {
	//-- Para los campos de tipo input (text, number, etc.).
	input.addEventListener('input', function () {
		if (input.classList.contains('is-invalid')) {
			//-- Eliminar la clase de borde rojo (border-danger).
			input.classList.remove('is-invalid', 'border-danger');
			//-- Agregar la clase de borde azul (border-primary).
			input.classList.add('border-primary');
		}
	});
	//-- Para los combobox (select).
	input.addEventListener('change', function () {
		if (input.classList.contains('is-invalid')) {
			//-- Eliminar la clase de borde rojo (border-danger).
			input.classList.remove('is-invalid', 'border-danger');
			//-- Agregar la clase de borde azul (border-primary).
			input.classList.add('border-primary');
		}
	});
	
});

//-- Al cerrar el modal, enfocar el primer campo con error.
modalElement.addEventListener('hidden.bs.modal', function () {
	//-- Buscar el primer campo con la clase 'is-invalid' después de que el modal esté completamente oculto.
	const firstInvalidField = document.querySelector('.is-invalid');
	if (firstInvalidField) {
		firstInvalidField.focus(); //-- Establecer el foco en el primer campo con error.
	}
});

//---------------------------------------------------------------------------
//-- Funcionalidad para buscar un Cliente por su Id.
//---------------------------------------------------------------------------
const idClienteInput = document.getElementById("id_id_cliente");

if (idClienteInput){
	const nombreClienteInput = document.getElementById("id_nombre_cliente");
	
	idClienteInput.addEventListener("change", function() {
		const idCliente = idClienteInput.value.trim();
		
		if (idCliente) {
			fetch(`/informes/buscar/cliente/id/?id_cliente=${idCliente}`)
				.then(response => {
					if (!response.ok) {
						throw new Error("Cliente no encontrado");
					}
					return response.json();
				})
				.then(data => {
					nombreClienteInput.value = data.nombre_cliente || "Cliente sin nombre";
				})
				.catch(error => {
					// console.error("Error al obtener el cliente:", error);
					nombreClienteInput.value = "Cliente no encontrado";
				});
		} else {
			nombreClienteInput.value = "";
		}
	});
}

//---------------------------------------------------------------------------
//-- Funcionalidad que muestra el Modal para buscar un Cliente por filtrado.
//---------------------------------------------------------------------------
const buscarAgendaForm = document.getElementById('buscarAgendaForm');

if (buscarAgendaForm) {
	const tablaResultadosAgenda = document.getElementById('tablaResultadosAgenda').querySelector('tbody');

	buscarAgendaForm.addEventListener('submit', function (event) {
		event.preventDefault();
		
		const busquedaGeneral = document.getElementById('busquedaGeneral').value;
		
		//-- Validar que la búsqueda tenga al menos 4 caracteres.
		if (busquedaGeneral.length < 4) {
			alert('Por favor, ingrese al menos 4 caracteres para realizar la búsqueda.');
			return;
		}
		
		const url = `/informes/buscar/cliente/?busqueda_general=${busquedaGeneral}`;
		
		fetch(url, {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json',
			},
		})
		.then(response => response.json())
		.then(data => {
			tablaResultadosAgenda.innerHTML = ''; //-- Limpiar tabla de resultados.
			
			data.forEach(agenda => {
				
				const fila = `
					<tr>
						<td>${agenda.id_cliente}</td>
						<td>${agenda.cuit}</td>
						<td>${agenda.nombre_cliente}</td>
						<td>${agenda.movil_cliente || 'N/A'}</td>  <!-- Muestra Móvil -->
						<td>${agenda.email_cliente || 'N/A'}</td>  <!-- Muestra Email -->
						<td>${agenda.domicilio_cliente}</td>
						<td>${agenda.codigo_postal}</td>
						<td>
							<input type="radio" name="seleccionar-agenda" 
								class="seleccionar-agenda" 
								data-id="${agenda.id_cliente}" 
								data-cuit="${agenda.cuit}" 
								data-nombre="${agenda.nombre_cliente}" 
								data-direccion="${agenda.domicilio_cliente}" 
								data-movil="${agenda.movil_cliente}"  
								data-email="${agenda.email_cliente}"
								data-cp="${agenda.codigo_postal}">
						</td>
					</tr>
				`;
				
				tablaResultadosAgenda.insertAdjacentHTML('beforeend', fila);
			});
			
		})
		.catch(error => {
			console.error('Error al buscar en agenda:', error);
		});
	});
	
	//-- Botón seleccionar de Lista de Clientes.
	document.getElementById('seleccionarAgenda').addEventListener('click', function () {
		const seleccion = document.querySelector('input[name="seleccionar-agenda"]:checked');
		
		if (seleccion) {
			const id_cliente = seleccion.getAttribute('data-id');
			const nombre = seleccion.getAttribute('data-nombre');
			// const cuit = seleccion.getAttribute('data-cuit');
			// const direccion = seleccion.getAttribute('data-direccion');
			// const movil = seleccion.getAttribute('data-movil');
			// const email = seleccion.getAttribute('data-email');
			// const cp = seleccion.getAttribute('data-cp');
			
			document.getElementById('id_id_cliente').value = id_cliente || '';
			document.getElementById('id_nombre_cliente').value = nombre || '';
			// document.getElementById('id_domicilio_factura').value = direccion || '';
			// document.getElementById('id_cuit').value = cuit || '';
			// document.getElementById('id_movil_factura').value = movil || '';
			// document.getElementById('id_email_factura').value = email || '';
			// document.getElementById('id_id_vendedor').value = id_vendedor || '';
			// document.getElementById('id_vendedor_factura').value = nombre_vendedor || '';
			
			//-- Cerrar el modal.
			const modal = bootstrap.Modal.getInstance(document.getElementById('agendaModal'));
			modal.hide();
		}
	});

	//-- Limpiar filtros y resultados cuando se cierra la ventana modal.
	agendaModal.addEventListener('hidden.bs.modal', function () {
		buscarAgendaForm.reset(); //-- Restablecer el formulario.
		tablaResultadosAgenda.innerHTML = ''; //-- Limpiar la tabla de resultados.
	});
}
// -------------------------------------------------------------------------------
