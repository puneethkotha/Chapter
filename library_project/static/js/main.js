/**
 * Library Management System
 * Main JavaScript File
 * 
 * This file contains custom JavaScript functionality for the library management system.
 */

document.addEventListener('DOMContentLoaded', function() {
    /**
     * Initialize tooltips
     */
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    /**
     * Initialize popovers
     */
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    /**
     * Auto-hide alerts after 5 seconds
     */
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        });
    }, 5000);

    /**
     * Mobile sidebar toggle
     */
    const menuToggle = document.querySelector('.menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', function() {
            if (sidebar.style.display === 'block') {
                sidebar.style.display = 'none';
            } else {
                sidebar.style.display = 'block';
            }
        });
    }

    /**
     * Book Search Form Enhancements
     */
    const bookSearchForm = document.getElementById('book-search-form');
    if (bookSearchForm) {
        const searchInput = bookSearchForm.querySelector('input[name="q"]');
        const clearSearchBtn = document.createElement('button');
        clearSearchBtn.type = 'button';
        clearSearchBtn.className = 'btn btn-link position-absolute end-0 top-0 text-decoration-none';
        clearSearchBtn.innerHTML = '<i class="fas fa-times"></i>';
        clearSearchBtn.style.display = 'none';
        clearSearchBtn.style.height = '100%';
        
        searchInput.parentNode.style.position = 'relative';
        searchInput.parentNode.appendChild(clearSearchBtn);
        
        searchInput.addEventListener('input', function() {
            clearSearchBtn.style.display = this.value ? 'block' : 'none';
        });
        
        clearSearchBtn.addEventListener('click', function() {
            searchInput.value = '';
            clearSearchBtn.style.display = 'none';
            searchInput.focus();
        });
    }

    /**
     * Rental Return Date Calculator
     */
    const borrowDateInput = document.getElementById('id_borrow_date');
    const expReturnDateInput = document.getElementById('id_exp_return_dt');
    
    if (borrowDateInput && expReturnDateInput) {
        borrowDateInput.addEventListener('change', function() {
            const borrowDate = new Date(this.value);
            if (!isNaN(borrowDate.getTime())) {
                // Set expected return date to 14 days after borrow date
                const returnDate = new Date(borrowDate);
                returnDate.setDate(returnDate.getDate() + 14);
                
                // Format the date for the input
                const year = returnDate.getFullYear();
                const month = String(returnDate.getMonth() + 1).padStart(2, '0');
                const day = String(returnDate.getDate()).padStart(2, '0');
                const formattedDate = `${year}-${month}-${day}`;
                
                expReturnDateInput.value = formattedDate;
            }
        });
    }

    /**
     * Room Reservation Conflict Checker
     */
    const reservationForm = document.getElementById('reservation-form');
    if (reservationForm) {
        const startDateInput = document.getElementById('id_start_dt');
        const endDateInput = document.getElementById('id_end_dt');
        const roomIdInput = document.getElementById('id_study_room');
        const submitButton = reservationForm.querySelector('button[type="submit"]');
        
        function checkReservationConflicts() {
            const startDateTime = new Date(startDateInput.value);
            const endDateTime = new Date(endDateInput.value);
            const roomId = roomIdInput.value;
            
            if (isNaN(startDateTime.getTime()) || isNaN(endDateTime.getTime()) || !roomId) {
                return;
            }
            
            // Format dates for API call
            const startStr = startDateTime.toISOString().split('.')[0];
            const endStr = endDateTime.toISOString().split('.')[0];
            
            // This would be a fetch to your API endpoint to check conflicts
            // For demonstration, we're just adding a visual indicator
            const hasConflict = false; // This would be determined by API response
            
            if (hasConflict) {
                submitButton.classList.add('btn-danger');
                submitButton.innerHTML = '<i class="fas fa-exclamation-triangle me-1"></i> Conflict Found';
                submitButton.disabled = true;
            } else {
                submitButton.classList.remove('btn-danger');
                submitButton.innerHTML = '<i class="fas fa-calendar-check me-1"></i> Confirm Reservation';
                submitButton.disabled = false;
            }
        }
        
        if (startDateInput && endDateInput && roomIdInput) {
            startDateInput.addEventListener('change', checkReservationConflicts);
            endDateInput.addEventListener('change', checkReservationConflicts);
            roomIdInput.addEventListener('change', checkReservationConflicts);
        }
    }

    /**
     * Data table initializer
     */
    const dataTables = document.querySelectorAll('.data-table');
    dataTables.forEach(function(table) {
        // If using a DataTables library, initialize it here
        // For now, we'll just add a simple search functionality
        const tableContainer = table.closest('.table-container');
        if (tableContainer) {
            const searchInput = document.createElement('input');
            searchInput.type = 'text';
            searchInput.className = 'form-control mb-3';
            searchInput.placeholder = 'Search this table...';
            
            tableContainer.insertBefore(searchInput, table);
            
            searchInput.addEventListener('input', function() {
                const searchTerm = this.value.toLowerCase();
                const rows = table.querySelectorAll('tbody tr');
                
                rows.forEach(function(row) {
                    const text = row.textContent.toLowerCase();
                    if (text.includes(searchTerm)) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
            });
        }
    });

    /**
     * Custom file input enhancer
     */
    const fileInputs = document.querySelectorAll('.custom-file-input');
    fileInputs.forEach(function(input) {
        const label = input.nextElementSibling;
        
        input.addEventListener('change', function(e) {
            let fileName = '';
            if (this.files && this.files.length > 1) {
                fileName = (this.getAttribute('data-multiple-caption') || '').replace('{count}', this.files.length);
            } else {
                fileName = e.target.value.split('\\').pop();
            }
            
            if (fileName) {
                label.innerHTML = fileName;
            }
        });
    });

    /**
     * Print functionality
     */
    const printButtons = document.querySelectorAll('.btn-print');
    printButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            window.print();
        });
    });

    /**
     * Form validation enhancement
     */
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });

    /**
     * Dynamic breadcrumb generator
     */
    function updateBreadcrumbs() {
        const breadcrumbContainer = document.querySelector('.breadcrumb');
        if (!breadcrumbContainer) return;
        
        const path = window.location.pathname;
        const parts = path.split('/').filter(Boolean);
        
        // Clear existing breadcrumbs except Home
        const existingItems = breadcrumbContainer.querySelectorAll('.breadcrumb-item');
        for (let i = existingItems.length - 1; i > 0; i--) {
            breadcrumbContainer.removeChild(existingItems[i]);
        }
        
        // Build path parts for each level
        let currentPath = '';
        parts.forEach((part, index) => {
            currentPath += '/' + part;
            
            const item = document.createElement('li');
            item.className = 'breadcrumb-item';
            
            if (index === parts.length - 1) {
                item.classList.add('active');
                item.setAttribute('aria-current', 'page');
                item.textContent = part.charAt(0).toUpperCase() + part.slice(1).replace(/-/g, ' ');
            } else {
                const link = document.createElement('a');
                link.href = currentPath;
                link.textContent = part.charAt(0).toUpperCase() + part.slice(1).replace(/-/g, ' ');
                item.appendChild(link);
            }
            
            breadcrumbContainer.appendChild(item);
        });
    }
    
    // Call the function on page load
    updateBreadcrumbs();

    /**
     * Dark mode toggle
     */
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    if (darkModeToggle) {
        // Check for saved preference
        const isDarkMode = localStorage.getItem('darkMode') === 'true';
        
        // Set initial state
        if (isDarkMode) {
            document.body.classList.add('dark-mode');
            darkModeToggle.checked = true;
        }
        
        // Handle toggle changes
        darkModeToggle.addEventListener('change', function() {
            if (this.checked) {
                document.body.classList.add('dark-mode');
                localStorage.setItem('darkMode', 'true');
            } else {
                document.body.classList.remove('dark-mode');
                localStorage.setItem('darkMode', 'false');
            }
        });
    }
});
