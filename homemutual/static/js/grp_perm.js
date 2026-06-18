// Filtrar asignados.
function filtrarAsignados(asignados, disponibles) {
	for (let i = 0; i < asignados.options.length; i++) {
		for (let j = 0; j < disponibles.options.length; j++) {
			if (asignados.options[i].value === disponibles.options[j].value) {
				disponibles.remove(j);
				j--; // Ajustamos el índice después de eliminar un elemento
			}
		}
	}
};

// Funciones para mover elementos entre selectores.
function moverElementosSeleccionados(origen, destino) {
	for (let i = 0; i < origen.options.length; i++) {
		if (origen.options[i].selected) {
			origen.options[i].selected = false;
			destino.appendChild(origen.options[i]);
			i--;
		};
	}
}

// function moverElementosTodos(origen, destino) {
// 	for (let i = 0; i < origen.options.length; i++) {
// 		destino.appendChild(origen.options[i]);
// 		i--;
// 	};
// };

function moverElementosTodos(origen, destino) {
    for (let i = 0; i < origen.options.length; i++) {
        if (origen.options[i].style.display !== 'none') {
            destino.appendChild(origen.options[i]);
            i--; // Decrementar i porque una opción ha sido removida
        }
    }
}
