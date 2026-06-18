// ============================================
// select2_config_cliente.js
// Configuración específica para búsqueda de clientes
// ============================================

// Configuración base de Select2 para clientes
const select2ClienteConfig = {
    theme: 'bootstrap-5',           // Tema compatible con Bootstrap 5
    allowClear: true,                // Permitir limpiar la selección con una "x"
    language: 'es',                  // Idioma español
    minimumInputLength: 2,           // Mínimo 2 caracteres para empezar a buscar
    placeholder: 'Buscar cliente por ID, nombre o CUIT...',
    
    // Configuración de búsqueda remota (AJAX)
    ajax: {
        url: '/maestros/buscar-cliente-select2/',  // Endpoint en Django
        dataType: 'json',                          // Tipo de datos esperados
        delay: 300,                                // Espera 300ms después de dejar de escribir
        
        // Datos que se envían al servidor
        data: function(params) {
            return {
                term: params.term,      // Término de búsqueda
                page: params.page || 1  // Número de página (para paginación)
            };
        },
        
        // Procesar los resultados recibidos del servidor
        processResults: function(data, params) {
            return {
                results: data.results,              // Lista de resultados
                pagination: {
                    more: data.more || false        // Si hay más páginas
                }
            };
        },
        
        cache: true  // Guardar resultados en caché para búsquedas repetidas
    },
    
    // Formato de cómo se muestra CADA resultado en el dropdown
    templateResult: function(cliente) {
        // Mientras se cargan los datos
        if (cliente.loading) {
            return cliente.text;
        }
        
        // Construir HTML personalizado para cada cliente
        var html = '<div><strong>' + cliente.id + '</strong> - ' + cliente.text;
        if (cliente.cuit) {
            html += '<br><small class="text-muted">CUIT: ' + cliente.cuit + '</small>';
        }
        html += '</div>';
        
        return $(html);
    },
    
    // Formato de cómo se muestra el cliente SELECCIONADO en el campo
    templateSelection: function(cliente) {
        if (!cliente.id) return cliente.text;
        return cliente.id + ' - ' + cliente.text;
    }
};

// ============================================
// FUNCIÓN 1: Inicializar Select2
// ============================================
// Inicializa el campo Select2 con la configuración de clientes
// 
// Uso: initClienteSelect2('.mi-selector')
// 
function initClienteSelect2(selector = '.select2-cliente') {
    $(selector).select2(select2ClienteConfig);
}

// ============================================
// FUNCIÓN 2: Sincronizar campo oculto al seleccionar
// ============================================
// Cuando se selecciona un cliente, actualiza un campo oculto con el ID
// También maneja la limpieza y validación visual
//
// Uso: syncClienteHidden('.select2-cliente', '#id_cliente', '#cliente-error')
//
function syncClienteHidden(select2Selector, hiddenInputId, errorDivId = null) {
    
    // Evento: Cuando se SELECCIONA un cliente
    $(select2Selector).on('select2:select', function(e) {
        var data = e.params.data;                    // Datos del cliente seleccionado
        
        $(hiddenInputId).val(data.id);               // Guardar ID en campo oculto
        
        if (errorDivId) {
            $(errorDivId).hide();                    // Ocultar mensaje de error
        }
        
        $(select2Selector).removeClass('is-invalid'); // Quitar clase de error visual
    });
    
    // Evento: Cuando se LIMPIA la selección (click en la "x")
    $(select2Selector).on('select2:clearing', function() {
        $(hiddenInputId).val('');                    // Limpiar campo oculto
        
        if (errorDivId) {
            $(errorDivId).text('Debe seleccionar un cliente');  // Mostrar error
            $(errorDivId).show();
        }
        
        $(select2Selector).addClass('is-invalid');    // Agregar clase de error visual
    });
}

// ============================================
// FUNCIÓN 3: Validar antes de enviar el formulario
// ============================================
// Evita que el formulario se envíe si no hay un cliente seleccionado
//
// Uso: validateClienteSelect2('.select2-cliente', '#id_cliente', '#cliente-error', 'form')
//
function validateClienteSelect2(select2Selector, hiddenInputId, errorDivId, formSelector = 'form') {
    
    $(formSelector).on('submit', function(e) {
        // Verificar si hay un ID de cliente guardado
        if (!$(hiddenInputId).val()) {
            e.preventDefault();                       // Detener envío del formulario
            
            $(errorDivId).text('Debe seleccionar un cliente de la lista');
            $(errorDivId).show();                     // Mostrar mensaje de error
            
            $(select2Selector).addClass('is-invalid'); // Marcar campo como inválido
            
            // Enfocar el campo Select2
            $(select2Selector).select2('open');
            
            return false;  // No enviar formulario
        }
        return true;       // Enviar formulario
    });
}

// ============================================
// FUNCIÓN PRINCIPAL: Configuración completa (recomendada)
// ============================================
// Inicializa todas las funcionalidades de una vez
//
// Uso: setupClienteSelect2()
// Uso con selectores personalizados: setupClienteSelect2('.mi-cliente', '#mi-id', '#mi-error', 'form')
//
function setupClienteSelect2(
    select2Selector = '.select2-cliente',   // Selector del campo visual
    hiddenInputId = '#id_id_cliente',       // ID del campo oculto
    errorDivId = '#cliente-error',          // ID del div de error
    formSelector = 'form'                   // Selector del formulario
) {
    initClienteSelect2(select2Selector);                    // Paso 1: Inicializar
    syncClienteHidden(select2Selector, hiddenInputId, errorDivId);  // Paso 2: Sincronizar
    validateClienteSelect2(select2Selector, hiddenInputId, errorDivId, formSelector); // Paso 3: Validar
}