// JavaScript personalizado para el sistema de clínica

// Configuración global
const ClinicaApp = {
    init: function() {
        this.setupEventListeners();
        this.initializeComponents();
        this.setupFormValidation();
        this.setupAjaxDefaults();
    },

    setupEventListeners: function() {
        // Toggle sidebar en móviles
        $(document).on('click', '.sidebar-toggle', function() {
            $('.sidebar').toggleClass('show');
        });

        // Cerrar sidebar al hacer click fuera
        $(document).on('click', function(e) {
            if (!$(e.target).closest('.sidebar, .sidebar-toggle').length) {
                $('.sidebar').removeClass('show');
            }
        });

        // Confirmación para acciones de eliminación
        $(document).on('click', '.btn-delete', function(e) {
            e.preventDefault();
            const message = $(this).data('message') || '¿Está seguro de que desea eliminar este elemento?';
            if (confirm(message)) {
                window.location.href = $(this).attr('href');
            }
        });

        // Auto-hide alerts
        setTimeout(function() {
            $('.alert').fadeOut('slow');
        }, 5000);
    },

    initializeComponents: function() {
        // Inicializar tooltips
        $('[data-bs-toggle="tooltip"]').tooltip();

        // Inicializar popovers
        $('[data-bs-toggle="popover"]').popover();

        // Inicializar datepickers
        $('.datepicker').datepicker({
            format: 'yyyy-mm-dd',
            autoclose: true,
            todayHighlight: true,
            language: 'es'
        });

        // Inicializar select2 para búsquedas
        $('.select2').select2({
            theme: 'bootstrap-5',
            placeholder: 'Seleccione una opción',
            allowClear: true
        });
    },

    setupFormValidation: function() {
        // Validación personalizada para formularios
        $('.needs-validation').on('submit', function(e) {
            if (!this.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            $(this).addClass('was-validated');
        });

        // Validación en tiempo real
        $('.form-control').on('blur', function() {
            if (this.checkValidity()) {
                $(this).removeClass('is-invalid').addClass('is-valid');
            } else {
                $(this).removeClass('is-valid').addClass('is-invalid');
            }
        });
    },

    setupAjaxDefaults: function() {
        // Configuración CSRF para AJAX
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", $('meta[name=csrf-token]').attr('content'));
                }
            }
        });
    },

    showLoading: function(element) {
        const $element = $(element);
        $element.prop('disabled', true);
        const originalText = $element.text();
        $element.data('original-text', originalText);
        $element.html('<i class="fas fa-spinner fa-spin"></i> Cargando...');
    },

    hideLoading: function(element) {
        const $element = $(element);
        $element.prop('disabled', false);
        $element.html($element.data('original-text'));
    },

    showAlert: function(message, type = 'info') {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        $('.alert-container').prepend(alertHtml);
        
        // Auto-hide después de 5 segundos
        setTimeout(function() {
            $('.alert').first().fadeOut('slow', function() {
                $(this).remove();
            });
        }, 5000);
    }
};

// Módulo para gestión de pacientes
const PacientesModule = {
    init: function() {
        this.setupEventListeners();
    },

    setupEventListeners: function() {
        // Búsqueda en tiempo real
        $('#searchPacientes').on('input', this.debounce(function() {
            const searchTerm = $(this).val();
            PacientesModule.searchPacientes(searchTerm);
        }, 300));

        // Modal para nuevo paciente
        $('#btnNuevoPaciente').on('click', function() {
            $('#modalPaciente').modal('show');
            $('#formPaciente')[0].reset();
            $('#modalPacienteLabel').text('Nuevo Paciente');
        });

        // Editar paciente
        $(document).on('click', '.btn-edit-paciente', function() {
            const pacienteId = $(this).data('id');
            PacientesModule.loadPacienteData(pacienteId);
        });

        // Ver historial
        $(document).on('click', '.btn-historial', function() {
            const pacienteId = $(this).data('id');
            PacientesModule.loadHistorial(pacienteId);
        });
    },

    searchPacientes: function(searchTerm) {
        const url = new URL(window.location);
        url.searchParams.set('search', searchTerm);
        url.searchParams.set('page', '1');
        window.location.href = url.toString();
    },

    loadPacienteData: function(pacienteId) {
        ClinicaApp.showLoading('#btnGuardarPaciente');
        
        $.get(`/pacientes/${pacienteId}/editar`)
            .done(function(data) {
                // Llenar formulario con datos del paciente
                $('#pacienteId').val(data.id);
                $('#cedula').val(data.cedula);
                $('#nombres').val(data.nombres);
                $('#apellidos').val(data.apellidos);
                $('#fechaNacimiento').val(data.fecha_nacimiento);
                $('#genero').val(data.genero);
                $('#telefono').val(data.telefono);
                $('#email').val(data.email);
                $('#direccion').val(data.direccion);
                $('#contactoEmergencia').val(data.contacto_emergencia);
                $('#telefonoEmergencia').val(data.telefono_emergencia);
                $('#observaciones').val(data.observaciones);
                
                $('#modalPacienteLabel').text('Editar Paciente');
                $('#modalPaciente').modal('show');
            })
            .fail(function() {
                ClinicaApp.showAlert('Error al cargar datos del paciente', 'danger');
            })
            .always(function() {
                ClinicaApp.hideLoading('#btnGuardarPaciente');
            });
    },

    loadHistorial: function(pacienteId) {
        ClinicaApp.showLoading('#historialContent');
        
        $.get(`/pacientes/${pacienteId}/historial`)
            .done(function(data) {
                PacientesModule.renderHistorial(data);
                $('#modalHistorial').modal('show');
            })
            .fail(function() {
                ClinicaApp.showAlert('Error al cargar historial del paciente', 'danger');
            })
            .always(function() {
                ClinicaApp.hideLoading('#historialContent');
            });
    },

    renderHistorial: function(data) {
        const paciente = data.paciente;
        const estudios = data.estudios;
        
        let historialHtml = `
            <div class="patient-info mb-4">
                <h5>${paciente.nombres} ${paciente.apellidos}</h5>
                <p><strong>Cédula:</strong> ${paciente.cedula}</p>
                <p><strong>Fecha de Nacimiento:</strong> ${paciente.fecha_nacimiento}</p>
                <p><strong>Género:</strong> ${paciente.genero}</p>
            </div>
            <div class="estudios-timeline">
        `;
        
        if (estudios.length === 0) {
            historialHtml += '<p class="text-muted">No hay estudios registrados para este paciente.</p>';
        } else {
            estudios.forEach(function(estudio) {
                const estadoBadge = PacientesModule.getEstadoBadge(estudio.estado);
                historialHtml += `
                    <div class="timeline-item mb-3">
                        <div class="card">
                            <div class="card-body">
                                <div class="d-flex justify-content-between align-items-start">
                                    <div>
                                        <h6 class="card-title">${estudio.tipo}</h6>
                                        <p class="card-text text-muted">${estudio.area}</p>
                                        <small class="text-muted">Fecha: ${estudio.fecha_solicitud}</small>
                                    </div>
                                    <span class="badge ${estadoBadge}">${estudio.estado}</span>
                                </div>
                                ${estudio.observaciones ? `<p class="mt-2 mb-0"><small>${estudio.observaciones}</small></p>` : ''}
                            </div>
                        </div>
                    </div>
                `;
            });
        }
        
        historialHtml += '</div>';
        $('#historialContent').html(historialHtml);
    },

    getEstadoBadge: function(estado) {
        const badges = {
            'solicitado': 'bg-warning',
            'en_proceso': 'bg-info',
            'completado': 'bg-success',
            'cancelado': 'bg-danger'
        };
        return badges[estado] || 'bg-secondary';
    },

    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// Módulo para gestión de estudios
const EstudiosModule = {
    init: function() {
        this.setupEventListeners();
    },

    setupEventListeners: function() {
        // Filtros de estudios
        $('#areaFilter, #estadoFilter').on('change', function() {
            EstudiosModule.applyFilters();
        });

        // Cargar tipos de estudio según área seleccionada
        $('#areaEstudio').on('change', function() {
            const areaId = $(this).val();
            EstudiosModule.loadTiposEstudio(areaId);
        });

        // Modal para nueva área de estudio
        $('#btnNuevaArea').on('click', function() {
            $('#modalArea').modal('show');
        });

        // Actualizar estado de estudio
        $(document).on('click', '.btn-update-estado', function() {
            const estudioId = $(this).data('id');
            const nuevoEstado = $(this).data('estado');
            EstudiosModule.updateEstado(estudioId, nuevoEstado);
        });
    },

    applyFilters: function() {
        const url = new URL(window.location);
        const areaId = $('#areaFilter').val();
        const estado = $('#estadoFilter').val();
        
        if (areaId) {
            url.searchParams.set('area_id', areaId);
        } else {
            url.searchParams.delete('area_id');
        }
        
        if (estado) {
            url.searchParams.set('estado', estado);
        } else {
            url.searchParams.delete('estado');
        }
        
        url.searchParams.set('page', '1');
        window.location.href = url.toString();
    },

    loadTiposEstudio: function(areaId) {
        if (!areaId) {
            $('#tipoEstudio').html('<option value="">Seleccione un tipo</option>');
            return;
        }
        
        $.get(`/tipos-estudio?area_id=${areaId}`)
            .done(function(data) {
                let options = '<option value="">Seleccione un tipo</option>';
                data.forEach(function(tipo) {
                    options += `<option value="${tipo.id}">${tipo.nombre}</option>`;
                });
                $('#tipoEstudio').html(options);
            })
            .fail(function() {
                ClinicaApp.showAlert('Error al cargar tipos de estudio', 'danger');
            });
    },

    updateEstado: function(estudioId, nuevoEstado) {
        if (!confirm('¿Está seguro de cambiar el estado de este estudio?')) {
            return;
        }
        
        $.post(`/estudios/${estudioId}/actualizar`, {
            estado: nuevoEstado
        })
        .done(function() {
            ClinicaApp.showAlert('Estado actualizado correctamente', 'success');
            location.reload();
        })
        .fail(function() {
            ClinicaApp.showAlert('Error al actualizar el estado', 'danger');
        });
    }
};

// Módulo para reportes
const ReportesModule = {
    init: function() {
        this.setupEventListeners();
    },

    setupEventListeners: function() {
        // Cambio de tipo de reporte
        $('#tipoReporte').on('change', function() {
            ReportesModule.updateReportPreview();
        });

        // Cambio de filtros
        $('#fechaInicio, #fechaFin, #areaReporte').on('change', function() {
            ReportesModule.updateReportPreview();
        });

        // Generar reporte
        $('#formReporte').on('submit', function(e) {
            e.preventDefault();
            ReportesModule.generateReport();
        });
    },

    updateReportPreview: function() {
        const tipoReporte = $('#tipoReporte').val();
        const fechaInicio = $('#fechaInicio').val();
        const fechaFin = $('#fechaFin').val();
        const areaId = $('#areaReporte').val();
        
        // Simular vista previa
        let previewHtml = '<h6>Vista Previa del Reporte</h6>';
        
        if (tipoReporte) {
            previewHtml += `<p><strong>Tipo:</strong> ${tipoReporte.toUpperCase()}</p>`;
        }
        
        if (fechaInicio && fechaFin) {
            previewHtml += `<p><strong>Período:</strong> ${fechaInicio} al ${fechaFin}</p>`;
        }
        
        if (areaId) {
            const areaNombre = $('#areaReporte option:selected').text();
            previewHtml += `<p><strong>Área:</strong> ${areaNombre}</p>`;
        }
        
        previewHtml += '<p class="text-muted">El reporte incluirá todos los estudios que coincidan con los filtros seleccionados.</p>';
        
        $('#reportPreview').html(previewHtml);
    },

    generateReport: function() {
        const $btn = $('#btnGenerarReporte');
        ClinicaApp.showLoading($btn);
        
        // Simular generación de reporte
        setTimeout(function() {
            ClinicaApp.hideLoading($btn);
            ClinicaApp.showAlert('Reporte generado exitosamente', 'success');
        }, 2000);
    }
};

// Inicialización cuando el documento esté listo
$(document).ready(function() {
    ClinicaApp.init();
    
    // Inicializar módulos según la página actual
    const currentPage = $('body').data('page');
    
    switch(currentPage) {
        case 'pacientes':
            PacientesModule.init();
            break;
        case 'estudios':
            EstudiosModule.init();
            break;
        case 'reportes':
            ReportesModule.init();
            break;
    }
    
    // Animaciones de entrada
    $('.fade-in').each(function(index) {
        $(this).delay(index * 100).queue(function() {
            $(this).addClass('show').dequeue();
        });
    });
});

// Funciones globales útiles
window.ClinicaUtils = {
    formatDate: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-ES');
    },
    
    formatCurrency: function(amount) {
        return new Intl.NumberFormat('es-ES', {
            style: 'currency',
            currency: 'EUR'
        }).format(amount);
    },
    
    validateCedula: function(cedula) {
        // Validación básica de cédula (puede adaptarse según el país)
        return /^[0-9]{8,12}$/.test(cedula);
    },
    
    validateEmail: function(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }
};