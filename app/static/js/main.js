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


function updateRecords() {
    ajaxCall('/notes/list/', 'GET', null, function (data) {
        var notesHtml = data.data.map(note => `
            <div class="note-item">
                <div class="note-title">${note.title}</div>
                <div class="note-actions">
                    <a href="#" class="edit-note" data-id="${note.id}" style="width: 30px; margin-left: -15px; display: inline-block; text-align: center;"><i class="fas fa-pencil-alt"></i></a>
                    <a href="#" class="delete-note" data-id="${note.id}" style="width: 30px; margin-left: -15px;display: inline-block; text-align: center;"><i class="fas fa-trash"></i></a>
                </div>
            </div>
        `).join('');
        $('.note-list').html(notesHtml);
    }, function () {
        toastr.error('Data updation failed');
    });
}



$(document).ready(function () {

    // Handle edit note click event
    $(document).on('click', '.edit-note', function () {
        var noteId = $(this).attr('data-id');

        // Get the note data via AJAX
        ajaxCall('/notes/get/' + noteId + '/', 'GET', null, function (data) {
            // Populate the form with the retrieved data
            $('input[name="title"]').val(data.data.title);
            $('#noteContent').val(data.data.content);

            // Initialize CKEditor on the textarea
            if (CKEDITOR.instances['noteContent']) {
                CKEDITOR.instances['noteContent'].destroy(true);
            }
            CKEDITOR.replace('noteContent');
            CKEDITOR.instances['noteContent'].setData(data.data.content);

            // Set the selected category
            $('#noteCategory').val(data.data.category_id);

            // Hide the save button and show the update button
            var saveButton = $('#createNoteForm button[type="submit"]');
            saveButton.hide();

            if (!$('#updateNoteButton').length ) {
                $('<button id="updateNoteButton" class="btn btn-primary">Update Note</button>')
                    .insertAfter(saveButton)
                    .on('click', function (event) {
                        event.preventDefault(); // Prevent the default form submission

                        // Get the form data
                        var formData = {
                            title: $('input[name="title"]').val(),
                            category_id: $('#noteCategory').val(),
                            content: CKEDITOR.instances['noteContent'].getData(),
                            // user_id: 2 // Assuming user_id is fixed for now
                        };

                        // Check for empty fields and show custom error for each field
                        if (!formData.title) {
                            toastr.error('Title field cannot be empty');
                            return;
                        }
                        if (!formData.category_id) {
                            toastr.error('Category field cannot be empty');
                            return;
                        }
                        if (!formData.content) {
                            toastr.error('Content field cannot be empty');
                            return;
                        }

                        // Send the PUT request using AJAX
                        ajaxCall(`/notes/put/${noteId}`, 'PUT', formData, function (response) {
                            // Show success toast
                            toastr.success('Note updated successfully');

                            // Update the specific note item in the list
                            updateRecords();

                            // Reset the form and make the save button visible again
                            $('#createNoteForm')[0].reset();
                            CKEDITOR.instances['noteContent'].setData('');
                            saveButton.show();
                            $('#updateNoteButton').remove();
                        }, function (xhr, status, error) {
                            toastr.error('Update error: ' + error);
                        });
                    });
            } else {
                $('#updateNoteButton').show();
            }
        }, function (error) {
            toastr.error('Error retrieving note: ' + error);
        });
    });

    // Ensure the save button is shown and the update button is hidden on form reset
    $('#createNoteForm').on('reset', function () {
        $('button[type="submit"]').show();
        $('#updateNoteButton').remove();
    });


    // Handle delete note click event
    $(document).on('click', '.delete-note', function (e) {
        e.preventDefault();
        var noteId = $(this).attr('data-id');

        Swal.fire({
            title: "Do you want to save the changes?",
            showCancelButton: true,
            confirmButtonText: "Delete"
        }).then((result) => {
            /* Read more about isConfirmed, isDenied below */
            if (result.isConfirmed) {

                ajaxCall(`/notes/delete/${noteId}`, 'DELETE', {}, function () {

                    // Show success toast
                    Swal.fire("Deleted!", "", "success");

                    // Refresh the records list
                    updateRecords();
                    // window.location.reload()
                }, function (error) {
                    Swal.fire("Error deleting Note!", "", "failure");
                });


            } else if (result.isDenied) {
                Swal.fire("Changes are not saved", "", "info");
            }
        });

    });

    // Handle the create note form submission
    $(document).on('submit', '#createNoteForm', function (event) {
        event.preventDefault(); // Prevent the default form submission

        // Get the form data
        var formData = {
            // user_id: 2,
            title: $('input[placeholder="Note Title"]').val(),
            category_id: $('#noteCategory').val(),
            content: $('textarea[placeholder="Note Content"]').val()
        };

        // Check if any field is empty and show custom toaster message
        if (!formData.title) {
            toastr.error('Title field cannot be empty');
            return;
        }
        if (!formData.category_id) {
            toastr.error('Category field cannot be empty');
            return;
        }
        if (!formData.content) {
            toastr.error('Content field cannot be empty');
            return;
        }

        ajaxCall('/notes/post/', 'POST', formData, function (data) {
            // Show success toast
            toastr.success('Note created successfully');

            // Clear the form
            $('#createNoteForm')[0].reset();

            // Clear the TinyMCE content
            CKEDITOR.instances['noteContent'].setData('');

            // Fetch and render updated records
            updateRecords();
            // window.location.reload()
        }, function (error) {
            toastr.error('Error creating note: ' + error);
        });
    });


    // ******************************** JS For Logout ******************************** //

    function getCsrfToken() {
        return $('meta[name="csrf-token"]').attr('content');
    }

    function eraseCookie(name) {
        document.cookie = name + '=; Max-Age=-99999999;';
    }
    
    $('#logout-btn').click(function(event) {
        event.preventDefault();
        $.ajax({
            type: 'POST',
            url: '/logout',
            success: function(response) {
                console.log("Logged out successfully");
                eraseCookie('access_token_cookie');
                eraseCookie('refresh_token_cookie');
                window.location.href = '/login';
                // Clear the form after redirecting to login
                $('#username').val('');
                $('#password').val('');
            },
            error: function(xhr, status, error) {
                console.log("Error logging out: ", error);
            }
        });
    });

    // ******************************** JS For Logout ******************************** //


});