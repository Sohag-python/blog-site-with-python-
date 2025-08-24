// Main JavaScript for Blog Site

$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);

    // Favorite button functionality
    $('.btn-favorite').on('click', function(e) {
        e.preventDefault();
        var button = $(this);
        var url = button.attr('href');
        var icon = button.find('i');
        
        // Show loading state
        var originalIcon = icon.attr('class');
        icon.attr('class', 'fas fa-spinner fa-spin');
        button.prop('disabled', true);
        
        $.ajax({
            url: url,
            type: 'POST',
            headers: {
                'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val(),
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(data) {
                if (data.is_favorited) {
                    icon.attr('class', 'fas fa-heart');
                    button.removeClass('btn-outline-danger').addClass('btn-danger');
                } else {
                    icon.attr('class', 'far fa-heart');
                    button.removeClass('btn-danger').addClass('btn-outline-danger');
                }
                
                // Show success message
                showToast(data.message, 'success');
            },
            error: function() {
                icon.attr('class', originalIcon);
                showToast('An error occurred. Please try again.', 'error');
            },
            complete: function() {
                button.prop('disabled', false);
            }
        });
    });

    // Follow button functionality
    $('.btn-follow').on('click', function(e) {
        e.preventDefault();
        var button = $(this);
        var url = button.attr('href');
        var text = button.find('.btn-text');
        var icon = button.find('i');
        
        // Show loading state
        var originalIcon = icon.attr('class');
        var originalText = text.text();
        icon.attr('class', 'fas fa-spinner fa-spin');
        text.text('Loading...');
        button.prop('disabled', true);
        
        $.ajax({
            url: url,
            type: 'POST',
            headers: {
                'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val(),
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(data) {
                if (data.is_following) {
                    icon.attr('class', 'fas fa-user-minus');
                    text.text('Unfollow');
                    button.removeClass('btn-primary').addClass('btn-outline-secondary');
                } else {
                    icon.attr('class', 'fas fa-user-plus');
                    text.text('Follow');
                    button.removeClass('btn-outline-secondary').addClass('btn-primary');
                }
                
                // Update followers count
                $('.followers-count').text(data.followers_count);
                
                // Show success message
                showToast(data.message, 'success');
            },
            error: function() {
                icon.attr('class', originalIcon);
                text.text(originalText);
                showToast('An error occurred. Please try again.', 'error');
            },
            complete: function() {
                button.prop('disabled', false);
            }
        });
    });

    // Search form auto-submit on filter change
    $('.search-form select, .search-form input[type="date"]').on('change', function() {
        $(this).closest('form').submit();
    });

    // Smooth scrolling for anchor links
    $('a[href^="#"]').on('click', function(e) {
        e.preventDefault();
        var target = $(this.getAttribute('href'));
        if (target.length) {
            $('html, body').stop().animate({
                scrollTop: target.offset().top - 100
            }, 1000);
        }
    });

    // Image lazy loading
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }

    // Form validation enhancement
    $('form').on('submit', function() {
        var submitBtn = $(this).find('button[type="submit"]');
        var originalText = submitBtn.text();
        
        submitBtn.prop('disabled', true);
        submitBtn.html('<span class="loading"></span> ' + originalText);
        
        // Re-enable after 10 seconds as fallback
        setTimeout(function() {
            submitBtn.prop('disabled', false);
            submitBtn.text(originalText);
        }, 10000);
    });

    // Rating stars interaction
    $('.rating-stars input[type="radio"]').on('change', function() {
        var rating = $(this).val();
        var stars = $(this).closest('.rating-stars').find('i');
        
        stars.each(function(index) {
            if (index < rating) {
                $(this).removeClass('far').addClass('fas');
            } else {
                $(this).removeClass('fas').addClass('far');
            }
        });
    });

    // Copy link functionality
    $('.copy-link').on('click', function(e) {
        e.preventDefault();
        var url = window.location.href;
        
        if (navigator.clipboard) {
            navigator.clipboard.writeText(url).then(function() {
                showToast('Link copied to clipboard!', 'success');
            });
        } else {
            // Fallback for older browsers
            var textArea = document.createElement('textarea');
            textArea.value = url;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            showToast('Link copied to clipboard!', 'success');
        }
    });
});

// Toast notification function
function showToast(message, type = 'info') {
    var toastClass = 'bg-primary';
    var icon = 'fas fa-info-circle';
    
    switch(type) {
        case 'success':
            toastClass = 'bg-success';
            icon = 'fas fa-check-circle';
            break;
        case 'error':
            toastClass = 'bg-danger';
            icon = 'fas fa-exclamation-circle';
            break;
        case 'warning':
            toastClass = 'bg-warning';
            icon = 'fas fa-exclamation-triangle';
            break;
    }
    
    var toastHtml = `
        <div class="toast align-items-center text-white ${toastClass} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="${icon} me-2"></i>${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    // Create toast container if it doesn't exist
    if (!$('#toast-container').length) {
        $('body').append('<div id="toast-container" class="toast-container position-fixed top-0 end-0 p-3"></div>');
    }
    
    var $toast = $(toastHtml);
    $('#toast-container').append($toast);
    
    var toast = new bootstrap.Toast($toast[0]);
    toast.show();
    
    // Remove toast element after it's hidden
    $toast.on('hidden.bs.toast', function() {
        $(this).remove();
    });
}

// Utility functions
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substr(0, maxLength) + '...';
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Add loading class to body
    document.body.classList.add('loaded');
    
    // Initialize any additional components here
});

