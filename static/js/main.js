// Main JavaScript for Nagaribashi Express
$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    $('.alert').each(function() {
        var alert = $(this);
        setTimeout(function() {
            alert.fadeOut();
        }, 5000);
    });

    // Confirm delete actions
    $('.btn-delete').on('click', function(e) {
        if (!confirm('আপনি কি নিশ্চিত যে আপনি এটি মুছে ফেলতে চান?')) {
            e.preventDefault();
        }
    });

    // Form validation
    $('form').on('submit', function(e) {
        var form = $(this);
        if (form[0].checkValidity() === false) {
            e.preventDefault();
            e.stopPropagation();
        }
        form.addClass('was-validated');
    });

    // Currency formatting
    $('.currency-input').on('input', function() {
        var value = $(this).val().replace(/[^\d]/g, '');
        if (value) {
            $(this).val('৳' + parseInt(value).toLocaleString());
        }
    });

    // Rating stars
    $('.rating-stars').on('click', 'i', function() {
        var rating = $(this).data('rating');
        var stars = $(this).parent().find('i');
        
        stars.removeClass('fas').addClass('far');
        stars.slice(0, rating).removeClass('far').addClass('fas');
        
        $(this).parent().find('input[type="hidden"]').val(rating);
    });

    // Order status updates
    $('.status-update').on('change', function() {
        var orderId = $(this).data('order-id');
        var newStatus = $(this).val();
        var statusElement = $(this).closest('tr').find('.order-status');
        
        $.ajax({
            url: '/orders/' + orderId + '/status/update/',
            method: 'POST',
            data: {
                'status': newStatus,
                'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                statusElement.removeClass().addClass('order-status status-' + newStatus);
                statusElement.text(response.status_display);
                showAlert('অর্ডার অবস্থা সফলভাবে আপডেট হয়েছে', 'success');
            },
            error: function() {
                showAlert('অর্ডার অবস্থা আপডেট করতে ব্যর্থ', 'danger');
            }
        });
    });

    // Search functionality
    $('#search-input').on('keyup', function() {
        var searchTerm = $(this).val().toLowerCase();
        $('.searchable-item').each(function() {
            var itemText = $(this).text().toLowerCase();
            if (itemText.indexOf(searchTerm) === -1) {
                $(this).hide();
            } else {
                $(this).show();
            }
        });
    });

    // Filter functionality
    $('.filter-btn').on('click', function() {
        var filter = $(this).data('filter');
        $('.filterable-item').each(function() {
            if (filter === 'all' || $(this).data('category') === filter) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
        
        $('.filter-btn').removeClass('active');
        $(this).addClass('active');
    });

    // Loading states
    $('.btn-loading').on('click', function() {
        var btn = $(this);
        var originalText = btn.html();
        
        btn.prop('disabled', true);
        btn.html('<span class="loading-spinner"></span> প্রক্রিয়াধীন...');
        
        setTimeout(function() {
            btn.prop('disabled', false);
            btn.html(originalText);
        }, 2000);
    });

    // Real-time notifications
    if (typeof(EventSource) !== "undefined") {
        var source = new EventSource("/notifications/stream/");
        source.onmessage = function(event) {
            var notification = JSON.parse(event.data);
            showNotification(notification.title, notification.message, notification.type);
        };
    }

    // Location tracking for delivery agents
    if (navigator.geolocation && $('.delivery-agent').length > 0) {
        navigator.geolocation.getCurrentPosition(function(position) {
            updateLocation(position.coords.latitude, position.coords.longitude);
        });
    }

    // Auto-refresh for order tracking
    if ($('.order-tracking').length > 0) {
        setInterval(function() {
            refreshOrderStatus();
        }, 30000); // Refresh every 30 seconds
    }
});

// Utility functions
function showAlert(message, type) {
    var alertHtml = '<div class="alert alert-' + type + ' alert-dismissible fade show" role="alert">' +
                    message +
                    '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>' +
                    '</div>';
    
    $('.main-content').prepend(alertHtml);
    
    setTimeout(function() {
        $('.alert').fadeOut();
    }, 5000);
}

function showNotification(title, message, type) {
    var notificationHtml = '<div class="toast" role="alert">' +
                          '<div class="toast-header">' +
                          '<strong class="me-auto">' + title + '</strong>' +
                          '<button type="button" class="btn-close" data-bs-dismiss="toast"></button>' +
                          '</div>' +
                          '<div class="toast-body">' + message + '</div>' +
                          '</div>';
    
    $('.toast-container').append(notificationHtml);
    
    var toast = new bootstrap.Toast($('.toast').last()[0]);
    toast.show();
}

function updateLocation(latitude, longitude) {
    $.ajax({
        url: '/delivery/location/update/',
        method: 'POST',
        data: {
            'latitude': latitude,
            'longitude': longitude,
            'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]').val()
        },
        success: function(response) {
            console.log('Location updated successfully');
        },
        error: function() {
            console.log('Failed to update location');
        }
    });
}

function refreshOrderStatus() {
    $('.order-tracking').each(function() {
        var orderId = $(this).data('order-id');
        $.ajax({
            url: '/orders/' + orderId + '/status/',
            method: 'GET',
            success: function(response) {
                $(this).find('.order-status').text(response.status_display);
                $(this).find('.order-status').removeClass().addClass('order-status status-' + response.status);
            }.bind(this)
        });
    });
}

// Bengali number conversion
function convertToBengaliNumbers(number) {
    var bengaliNumbers = ['০', '১', '২', '৩', '৪', '৫', '৬', '৭', '৮', '৯'];
    return number.toString().replace(/\d/g, function(digit) {
        return bengaliNumbers[digit];
    });
}

// Currency formatting
function formatCurrency(amount) {
    return '৳' + parseInt(amount).toLocaleString('bn-BD');
}

// Date formatting
function formatDate(dateString) {
    var date = new Date(dateString);
    var options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return date.toLocaleDateString('bn-BD', options);
}

// Phone number validation
function validatePhoneNumber(phone) {
    var phoneRegex = /^(\+88)?01[3-9]\d{8}$/;
    return phoneRegex.test(phone);
}

// Email validation
function validateEmail(email) {
    var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Form submission with loading state
function submitFormWithLoading(formSelector, successCallback) {
    var form = $(formSelector);
    var submitBtn = form.find('button[type="submit"]');
    var originalText = submitBtn.html();
    
    submitBtn.prop('disabled', true);
    submitBtn.html('<span class="loading-spinner"></span> প্রক্রিয়াধীন...');
    
    form.submit();
    
    setTimeout(function() {
        submitBtn.prop('disabled', false);
        submitBtn.html(originalText);
    }, 3000);
}

// Cart notification functionality
function addToCartNotification(productName, quantity) {
    // Show green notification when item is added to cart
    showCartNotification(quantity + 'টি ' + productName + ' কার্টে যোগ করা হয়েছে!', 'success');
    
    // Update cart badge
    updateCartBadge();
}

function showCartNotification(message, type) {
    type = type || 'success';
    var notification = document.createElement('div');
    notification.className = 'alert alert-' + type + ' alert-dismissible fade show';
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    notification.innerHTML = '<i class="fas fa-shopping-cart me-2"></i>' + message + '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>';
    
    document.body.appendChild(notification);
    
    // Auto remove after 3 seconds
    setTimeout(function() {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}

function updateCartBadge() {
    var cart = JSON.parse(localStorage.getItem('cart')) || [];
    var totalItems = cart.reduce(function(sum, item) {
        return sum + item.quantity;
    }, 0);
    var cartBadge = document.getElementById('cart-badge');
    
    if (cartBadge) {
        if (totalItems > 0) {
            cartBadge.textContent = totalItems;
            cartBadge.style.display = 'inline';
            // Add pulse animation for new items
            cartBadge.style.animation = 'pulse 0.5s ease-in-out';
            setTimeout(function() {
                cartBadge.style.animation = '';
            }, 500);
        } else {
            cartBadge.style.display = 'none';
        }
    }
}

// Add CSS for pulse animation
var style = document.createElement('style');
style.textContent = '@keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.2); } 100% { transform: scale(1); } }';
document.head.appendChild(style);