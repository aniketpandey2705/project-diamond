// ===== PRAHARI ENTERPRISE DASHBOARD - JAVASCRIPT =====

// Search Functionality
const searchInput = document.getElementById('searchInput');
const grievancesGrid = document.getElementById('grievancesGrid');

if (searchInput && grievancesGrid) {
    searchInput.addEventListener('input', function(e) {
        const searchTerm = e.target.value.toLowerCase();
        const cards = grievancesGrid.querySelectorAll('.grievance-card');
        
        cards.forEach(card => {
            const ticketId = card.dataset.id.toLowerCase();
            const status = card.dataset.status.toLowerCase();
            const aiReport = card.querySelector('.ai-content').textContent.toLowerCase();
            
            const matches = ticketId.includes(searchTerm) || 
                          status.includes(searchTerm) || 
                          aiReport.includes(searchTerm);
            
            if (matches) {
                card.style.display = 'block';
                card.style.animation = 'fadeIn 0.3s ease';
            } else {
                card.style.display = 'none';
            }
        });
    });
}

// Filter Functionality
const filterButtons = document.querySelectorAll('.filter-btn');

filterButtons.forEach(button => {
    button.addEventListener('click', function() {
        // Remove active class from all buttons
        filterButtons.forEach(btn => btn.classList.remove('active'));
        
        // Add active class to clicked button
        this.classList.add('active');
        
        const filterValue = this.dataset.filter;
        const cards = document.querySelectorAll('.grievance-card');
        
        cards.forEach(card => {
            if (filterValue === 'all') {
                card.style.display = 'block';
                card.style.animation = 'fadeIn 0.3s ease';
            } else {
                if (card.dataset.status === filterValue) {
                    card.style.display = 'block';
                    card.style.animation = 'fadeIn 0.3s ease';
                } else {
                    card.style.display = 'none';
                }
            }
        });
    });
});

// Copy Hash to Clipboard
function copyHash(id, hash) {
    // Create temporary textarea
    const textarea = document.createElement('textarea');
    textarea.value = hash;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    
    // Select and copy
    textarea.select();
    document.execCommand('copy');
    
    // Remove textarea
    document.body.removeChild(textarea);
    
    // Visual feedback
    const button = event.target.closest('.copy-btn');
    const originalHTML = button.innerHTML;
    
    button.innerHTML = '<i class="fas fa-check"></i>';
    button.style.background = '#10b981';
    
    setTimeout(() => {
        button.innerHTML = originalHTML;
        button.style.background = '';
    }, 2000);
    
    // Show toast notification
    showToast('Hash copied to clipboard!');
}

// Toast Notification
function showToast(message) {
    // Remove existing toast if any
    const existingToast = document.querySelector('.toast-notification');
    if (existingToast) {
        existingToast.remove();
    }
    
    // Create toast
    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.innerHTML = `
        <i class="fas fa-check-circle"></i>
        <span>${message}</span>
    `;
    
    // Add styles
    toast.style.cssText = `
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-weight: 600;
        z-index: 9999;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(toast);
    
    // Remove after 3 seconds
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Auto-refresh stats every 30 seconds (optional)
function refreshStats() {
    // This would typically make an AJAX call to get updated stats
    // For now, we'll just add a visual indicator
    const blocksBadge = document.querySelector('.blockchain-badge');
    if (blocksBadge) {
        blocksBadge.style.animation = 'pulse 0.5s ease';
        setTimeout(() => {
            blocksBadge.style.animation = '';
        }, 500);
    }
}

// Refresh every 30 seconds
setInterval(refreshStats, 30000);

// Smooth scroll for any anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add loading state to update buttons
document.querySelectorAll('.action-form').forEach(form => {
    form.addEventListener('submit', function(e) {
        const button = this.querySelector('.update-btn');
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Updating...';
        button.disabled = true;
    });
});

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('🛡️ Prahari Dashboard Initialized');
    
    // Add entrance animation to cards
    const cards = document.querySelectorAll('.grievance-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        searchInput?.focus();
    }
    
    // Escape to clear search
    if (e.key === 'Escape' && searchInput) {
        searchInput.value = '';
        searchInput.dispatchEvent(new Event('input'));
    }
});

// Add visual feedback for form submissions
document.querySelectorAll('.status-select').forEach(select => {
    select.addEventListener('change', function() {
        this.style.borderColor = '#10b981';
        setTimeout(() => {
            this.style.borderColor = '';
        }, 1000);
    });
});

// Verify individual grievance on blockchain
async function verifyGrievance(grievanceId) {
    try {
        const response = await fetch(`/verify_grievance/${grievanceId}`);
        const result = await response.json();
        
        if (result.found) {
            showToast(`✓ Verified on Block #${result.block_index} at ${result.timestamp}`);
        } else {
            showToast('⚠ Not found in blockchain', 'warning');
        }
    } catch (error) {
        showToast('❌ Verification failed', 'error');
    }
}

// Enhanced toast with types
function showToast(message, type = 'success') {
    const existingToast = document.querySelector('.toast-notification');
    if (existingToast) {
        existingToast.remove();
    }
    
    const colors = {
        success: 'linear-gradient(135deg, #10b981, #059669)',
        warning: 'linear-gradient(135deg, #f59e0b, #d97706)',
        error: 'linear-gradient(135deg, #ef4444, #dc2626)'
    };
    
    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'warning' ? 'exclamation-circle' : 'times-circle'}"></i>
        <span>${message}</span>
    `;
    
    toast.style.cssText = `
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        background: ${colors[type]};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-weight: 600;
        z-index: 9999;
        animation: slideIn 0.3s ease;
        max-width: 400px;
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

console.log('✅ Prahari Enterprise Dashboard Loaded Successfully');
