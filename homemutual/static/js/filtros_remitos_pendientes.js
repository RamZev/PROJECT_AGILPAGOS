// ---------------------------------------------------------------------------
// Funcionalidad para buscar producto por Código o CAI.
// ---------------------------------------------------------------------------
const filtrar_por = document.getElementById("id_filtrar_por");

// Para no anular la funcionalidad en el Form.
const divConDato = document.querySelector('div[data-user-vendedor]');
const userVendedor = divConDato.dataset.userVendedor;

const vendedorCombo = document.getElementById("id_vendedor");
const sucursalCombo = document.getElementById("id_sucursal");
const idCliDesde = document.getElementById("id_id_cli_desde");
const idCliHasta = document.getElementById("id_id_cli_hasta");


function blanquear(){
	vendedorCombo.selectedIndex = 0;
	sucursalCombo.selectedIndex = 0;
	idCliDesde.value = "";
	idCliHasta.value = "";
}

const cambiarEstado = () => {
	blanquear();
	if (filtrar_por.value === 'vendedor'){
		vendedorCombo.disabled = false;
		sucursalCombo.disabled = true;
		idCliDesde.disabled = true;
		idCliHasta.disabled = true;
	}else if (filtrar_por.value === 'clientes'){
		vendedorCombo.disabled = true;
		sucursalCombo.disabled = true;
		idCliDesde.disabled = false;
		idCliHasta.disabled = false;
	}else if (filtrar_por.value === 'sucursal_fac' || filtrar_por.value === 'sucursal_cli'){
		vendedorCombo.disabled = true;
		sucursalCombo.disabled = false;
		idCliDesde.disabled = true;
		idCliHasta.disabled = true;
	}
};

if (!userVendedor){
	cambiarEstado();
	filtrar_por.addEventListener("change", cambiarEstado);
}
// ---------------------------------------------------------------------------