// Fonction pour afficher les messages flash
function showMessage(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
            <span aria-hidden="true">&times;</span>
        </button>
    `;
    
    document.querySelector('.messages-container').appendChild(alertDiv);
    
    // Auto-hide après 5 secondes
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Validation des formulaires
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            if (!isValid) {
                event.preventDefault();
                showMessage('Veuillez remplir tous les champs requis', 'danger');
            }
        });
    });
});

// Prévisualisation des fichiers
function previewFile(input) {
    const preview = document.querySelector('.file-preview');
    const file = input.files[0];
    
    if (file) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            if (file.type.startsWith('image/')) {
                preview.innerHTML = `<img src="${e.target.result}" class="img-fluid" alt="Aperçu">`;
            } else {
                preview.innerHTML = `<div class="file-info">
                    <i class="fas fa-file"></i>
                    <p>${file.name}</p>
                    <small>${(file.size / 1024).toFixed(2)} KB</small>
                </div>`;
            }
        }
        
        reader.readAsDataURL(file);
    }
}

// Confirmation de suppression
function confirmDelete(event, message = 'Êtes-vous sûr de vouloir supprimer cet élément ?') {
    if (!confirm(message)) {
        event.preventDefault();
    }
}
