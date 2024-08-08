// ******************************** Helper functions ******************************** // 

function setCookie(name, value, days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "") + expires + "; path=/";
}


function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1,c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
    }
    return null;
}



function refreshToken() {
    return $.ajax({
        type: 'POST',
        url: '/refresh',
        contentType: 'application/json',
        success: function(response) {
            console.log("Token refreshed");
        },
        error: function(xhr, status, error) {
            console.log("Error refreshing token: ", error);
            // Redirect to login if refresh token fails
            window.location.href = '/login';
        }
    });
}



// ******************************** Helper functions ******************************** // 



$(document).ready(function() {

    // ******************************** JS FOR UI ******************************** // 

    $('#password').focusin(function() {
        $('form').addClass('up');
    });
    $('#password').focusout(function() {
        $('form').removeClass('up');
    });

    // Panda Eye move
    $(document).on('mousemove', function(event) {
        var dw = $(document).width() / 15;
        var dh = $(document).height() / 15;
        var x = event.pageX / dw;
        var y = event.pageY / dh;
        $('.eye-ball').css({
            width: x,
            height: y
        });
    });

    // ******************************** JS For UI ******************************** //

    // ******************************** JS For Login ******************************** // 
    $(document).ready(function() {
        $('#username').val('');
        $('#password').val('');
    });

    $('.btn').click(function(event) {
        event.preventDefault();
        var username = $('#username').val();
        var password = $('#password').val();

        if (!username || !password) {
            console.log("One or both fields are empty");
            $('.alert').text('Both username and password are required!!').show();
            $('form').addClass('wrong-entry');
            setTimeout(function() {
                $('form').removeClass('wrong-entry');
                $('.alert').hide();
            }, 3000);
            return;
        }

        var data = {
            'username': username,
            'password': password
        };

        $.ajax({
            type: 'POST',
            url: '/login',
            data: JSON.stringify(data),
            contentType: 'application/json',
            success: function(response) {
                if (response.message === 'Login Success') {
                    console.log("Login Successful");
                    window.location.href = '/home';
                } else {
                    console.log("Failure");
                    $('.alert').text('Invalid Credentials!!').show();
                    $('form').addClass('wrong-entry');
                    setTimeout(function() {
                        $('form').removeClass('wrong-entry');
                        $('.alert').hide();
                    }, 3000);
                }
            },
            error: function(xhr, status, error) {
                $('.alert').text('An error occurred. Please try again.').show();
                $('form').addClass('wrong-entry');
                setTimeout(function() {
                    $('form').removeClass('wrong-entry');
                    $('.alert').hide();
                }, 3000);
            },
            xhrFields: {
                withCredentials: true
            }
        });
    });

    // ******************************** JS For Login ******************************** //

    
});
