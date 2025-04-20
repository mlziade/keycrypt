document.addEventListener('DOMContentLoaded', function() {

    // --- Handle Bulk Actions ---
    var tabPanes = document.querySelectorAll('.tab-pane');
    tabPanes.forEach(function(pane) {
        var gridContainer = pane.querySelector('.puzzle-grid');
        if (gridContainer) {
            // Check if bulk actions already exist to prevent duplicates on potential reloads
            if (!pane.querySelector('.bulk-actions')) {
                var bulkActions = document.createElement('div');
                bulkActions.className = 'bulk-actions';
                bulkActions.innerHTML = `
                    <div class="bulk-action-buttons">
                        <button type="button" class="expand-all-btn">
                            <i class="bi bi-arrows-angle-expand"></i> Expand All
                        </button>
                        <button type="button" class="collapse-all-btn">
                            <i class="bi bi-arrows-angle-contract"></i> Collapse All
                        </button>
                    </div>
                `;
                
                // Insert bulk actions before the grid
                pane.insertBefore(bulkActions, gridContainer);

                // Add event listeners to bulk action buttons
                var expandAllBtn = bulkActions.querySelector('.expand-all-btn');
                var collapseAllBtn = bulkActions.querySelector('.collapse-all-btn');
                
                expandAllBtn.addEventListener('click', function() {
                    var collapseElements = pane.querySelectorAll('.collapse');
                    collapseElements.forEach(function(collapse) {
                        // Use Bootstrap API to show
                        bootstrap.Collapse.getOrCreateInstance(collapse).show();
                        // State update (aria-expanded, .collapsed) will be handled by the event listeners below
                    });
                });
                
                collapseAllBtn.addEventListener('click', function() {
                    var collapseElements = pane.querySelectorAll('.collapse');
                    collapseElements.forEach(function(collapse) {
                        // Use Bootstrap API to hide
                        bootstrap.Collapse.getOrCreateInstance(collapse).hide();
                        // State update (aria-expanded, .collapsed) will be handled by the event listeners below
                    });
                });
            }
        }
    });

    // --- Handle individual card collapse state changes using Bootstrap events ---
    // Select all collapse elements within the puzzle grids
    var allCollapseElements = document.querySelectorAll('.puzzle-grid .collapse');

    allCollapseElements.forEach(function(collapseEl) {
        var card = collapseEl.closest('.puzzle-card');
        // Find the header that controls this collapse element
        var header = card ? card.querySelector('.puzzle-card-header[data-bs-target="#' + collapseEl.id + '"]') : null;

        if (!card || !header) return; // Skip if structure is not as expected

        // Event listener for when Bootstrap starts showing the element
        collapseEl.addEventListener('show.bs.collapse', function () {
            header.setAttribute('aria-expanded', 'true');
            card.classList.remove('collapsed');
        });

        // Event listener for when Bootstrap starts hiding the element
        collapseEl.addEventListener('hide.bs.collapse', function () {
            header.setAttribute('aria-expanded', 'false');
            card.classList.add('collapsed');
        });

        // Set initial visual state based on whether the element starts shown or hidden
        if (collapseEl.classList.contains('show')) {
            header.setAttribute('aria-expanded', 'true');
            card.classList.remove('collapsed');
        } else {
            header.setAttribute('aria-expanded', 'false');
            card.classList.add('collapsed');
        }
    });
});