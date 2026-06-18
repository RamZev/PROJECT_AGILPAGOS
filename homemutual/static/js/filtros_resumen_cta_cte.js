// ---------------------------------------------------------------------------
// Funcionalidad Hab/Deshab combo Vendedor.
// ---------------------------------------------------------------------------
const resumenCheck = document.getElementById("id_resumen_pendiente");
const condicionCombo = document.getElementById("id_condicion_venta");
const fechaDesde = document.getElementById("id_fecha_desde");
const fechaHasta = document.getElementById("id_fecha_hasta");
const clienteCombo = document.getElementById("id_cliente");

const estadoResumenCheck = () => {
	console.log("Click en el Check");
    const disabled = resumenCheck.checked;
    [condicionCombo, fechaDesde, fechaHasta].forEach(campo => {
        campo.disabled = disabled;
    });
};

estadoResumenCheck();

resumenCheck.addEventListener("change", estadoResumenCheck);
// ---------------------------------------------------------------------------