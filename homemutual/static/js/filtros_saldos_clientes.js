// ---------------------------------------------------------------------------
// Funcionalidad Hab/Deshab combo Vendedor.
// ---------------------------------------------------------------------------
const clienteVendedorCombo = document.getElementById("id_cliente_vendedor");
const vendedorCombo = document.getElementById("id_vendedor");

const cambiarEstado = () => {
	if (clienteVendedorCombo.value === "clientes"){
		vendedorCombo.disabled = true;
		vendedorCombo.value = "";
	}else{
		vendedorCombo.disabled = false;
	}
};

cambiarEstado();

clienteVendedorCombo.addEventListener("change", cambiarEstado);
// ---------------------------------------------------------------------------