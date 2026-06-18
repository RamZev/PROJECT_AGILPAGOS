function mostrarBotones(fila) {
    if (fila.nodeType === Node.ELEMENT_NODE) {
      fila.querySelectorAll(".boton-oculto").forEach(function(boton) {
        boton.style.visibility = "visible";
      });
    }
  }
  
  function ocultarBotones(fila) {
    if (fila.nodeType === Node.ELEMENT_NODE) {
      fila.querySelectorAll(".boton-oculto").forEach(function(boton) {
        boton.style.visibility = "hidden";
      });
    }
  }

  window.onload = function() {
    // Seleccionar todas las filas del cuerpo de la tabla
    const filas = document.querySelectorAll("tbody tr");
    
    // Ocultar los botones inicialmente
    filas.forEach(ocultarBotones);
  
    // Añadir event listeners para mostrar y ocultar los botones al pasar el ratón
    filas.forEach(function(fila) {
      fila.addEventListener("mouseenter", function() {
        mostrarBotones(fila);
      });
  
      fila.addEventListener("mouseleave", function() {
        ocultarBotones(fila);
      });
    });

  };