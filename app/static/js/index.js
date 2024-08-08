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
        password_hash: password // Ensure this matches the key expected by your API
    };
    console.log(data);
    
    ajaxCall('http://localhost:5000/register', 'POST', data,
        function(response) {
            if (response.message === 'Created') {
                alert('User registered successfully!');
            } else {
                alert('Error: ' + response.message);
            }
        },
        function(error) {
            console.error('Error:', error);
            alert('Error: ' + error.responseJSON.error);
        }
    );
});
