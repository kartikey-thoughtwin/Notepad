function ajaxCall(url, method, data, successCallback, errorCallback) {
    $.ajax({
        url: url,
        method: method,
        data: data ? JSON.stringify(data) : null,
        contentType: 'application/json',
        success: successCallback,
        error: errorCallback
    });
}

document.getElementById('login-submit').addEventListener('click', function() {
    console.log("here");
    
    const name = document.getElementById('login-name').value;
    const username = document.getElementById('login-username').value;
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    const data = {
        name: name,
        username: username,
        email: email,
        password_hash: password 
    };
    console.log(data);
    
    ajaxCall('http://localhost:5000/register', 'POST', data,
        function(response) {
            if (response.message === 'Created') {
                // alert('User registered successfully!'); 
                $('#alert-message').text('Successfully registered!');
                $('#alert-message').removeClass('error');
                $('#alert-message').addClass('success');
                setTimeout(function() {
                    $('form').removeClass('wrong-entry');
                    window.location.href = '/home';
                }, 3000);
            
            } else {
                alert('Error: ' + response.message);
            }
        },
        function(error) {
            console.error('Error:', error);
            $('#alert-message').text(error.responseJSON.error);
            $('#alert-message').removeClass('success');
            $('#alert-message').addClass('error');
            $('form').addClass('wrong-entry');
            setTimeout(function() {
                $('form').removeClass('wrong-entry');
            }, 3000);
    }
    );
});

$(document).ready(function() {
    $('#login-password').focusin(function() {
        $('form').addClass('up');
    });
    $('#login-password').focusout(function() {
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

    // Validation
    $('.btn').click(function() {
        $('form').addClass('wrong-entry');
        setTimeout(function() {
            $('form').removeClass('wrong-entry');
        }, 3000);
    });
});
