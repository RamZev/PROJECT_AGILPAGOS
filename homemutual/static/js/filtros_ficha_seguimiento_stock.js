//-- neumatic\static\js\filtros_ficha_seguimiento_stock.js

//---------------------------------------------------------------------------
//-- Funcionalidad Hab/Deshab campos código/CAI.
//---------------------------------------------------------------------------

//-- Habilitar/Deshabilitar campos Código y CAI según se complete uno u otro.
const codigo = document.getElementById("id_codigo");
const cai = document.getElementById("id_cai");

//-- Función para restablecer el estado de los campos (Botón Reset).
function resetearEstadoCampos() {
	codigo.disabled = false;
	cai.disabled = false;
	updateFieldsState(codigo, cai);
	updateFieldsState(cai, codigo);
}

function updateFieldsState(currentField, otherField) {
	if (currentField.value.trim() !== '') {
		otherField.disabled = true;
	} else {
		otherField.disabled = false;
	}
}

//-- Event listeners para los campos.
codigo.addEventListener('input', () => {
	updateFieldsState(codigo, cai);
});

cai.addEventListener('input', () => {
	updateFieldsState(cai, codigo);
});

//-- Event listener para el reset del formulario.
formulario.addEventListener('reset', function() {
	setTimeout(resetearEstadoCampos, 10);
});

//-- Inicialización al cargar la página.
window.addEventListener('load', () => {
	codigo.disabled = false;
	cai.disabled = false;
	
	//-- Verificar estado inicial por si hay valores precargados.
	updateFieldsState(codigo, cai);
	updateFieldsState(cai, codigo);
});

//---------------------------------------------------------------------------
//-- Funcionalidad para buscar un Producto por su Id (Código) o CAI.
//---------------------------------------------------------------------------
const medida = document.getElementById("id_medida");
const producto = document.getElementById("id_producto");
const marca = document.getElementById("id_marca");

//-- Función para limpiar los campos.
function limpiarCamposProducto() {
	medida.value = "";
	producto.value = "";
	marca.value = "";
}

//-- Función para buscar producto por id (código).
function buscarProductoPorCodigo(idProducto) {
	fetch(`/informes/buscar/producto/id/?id_producto=${idProducto}`)
		.then(response => {
			if (!response.ok) {
				throw new Error("Error en la respuesta del servidor");
			}
			return response.json();
		})
		.then(data => {
			if (data.encontrado){
				//-- Producto encontrado.
				medida.value = data.medida || "S/M";
				producto.value = data.nombre_producto || "Producto sin nombre";
				marca.value = data.marca_producto || "Producto sin marca";
			} else {
				//-- Producto no encontrado.
				limpiarCamposProducto();
				producto.value = "No encontrado";
			}
		})
		.catch((error) => {
			//-- En caso de error en la petición.
			console.error("Error al buscar el producto por código:", error);
			limpiarCamposProducto();
			producto.value = "Error en la búsqueda por código";
		});
}

//-- Función para buscar producto por CAI.
function buscarProductoPorCAI(caiValue) {
	fetch(`/informes/buscar/producto/cai/?cai=${caiValue}`)
		.then(response => {
			if (!response.ok) {
				throw new Error("Error en la respuesta del servidor");
			}
			return response.json();
		})
		.then(data => {
			if (data.encontrado) {
				medida.value = data.medida || "S/M";
				producto.value = data.nombre_producto || "Producto sin nombre";
				marca.value = data.marca_producto || "Producto sin marca";
			} else {
				limpiarCamposProducto();
				producto.value = "No encontrado";
			}
		})
		.catch(error => {
			console.error("Error al buscar producto por CAI:", error);
			limpiarCamposProducto();
			producto.value = "Error en la búsqueda por CAI";
		});
}

//-- Event listener para el campo código.
codigo.addEventListener("change", function() {
	const idProducto = this.value.trim();
	if (idProducto) {
		buscarProductoPorCodigo(idProducto);
	} else {
		limpiarCamposProducto();
	}
});

//-- Event listener para el campo CAI.
cai.addEventListener("change", function() {
	const caiValue = this.value.trim();
	if (caiValue) {
		buscarProductoPorCAI(caiValue);
	} else {
		limpiarCamposProducto();
	}
});

//-- Verificar estado inicial al cargar la página.
window.addEventListener('load', () => {
	const idProducto = codigo.value.trim();
	const caiValue = cai.value.trim();
	
	if (idProducto) {
		buscarProductoPorCodigo(idProducto);
	} else if (caiValue) {
		buscarProductoPorCAI(caiValue);
	}
});
// ---------------------------------------------------------------------------
