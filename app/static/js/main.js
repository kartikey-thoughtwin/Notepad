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
    ajaxCall('/notes/list/', 'GET', null, function(data) {
        var notesHtml = data.data.map(note => `
            <div class="note-item">
                <div class="note-title">${note.title}</div>
                <div class="note-content">${note.content}</div>
                <div class="note-actions">
                    <a href="#" class="edit-note" data-id="${note.id}"><i class="fas fa-pencil-alt"></i></a>
                    <a href="#" class="delete-note" data-id="${note.id}"><i class="fas fa-trash"></i></a>
                </div>
            </div>
        `).join('');
        $('.note-list').html(notesHtml);
    }, function() {
        toastr.error('Data updation failed');
    });
}

$(document).ready(function () {

    // Handle edit note click event
    $(document).on('click', '.edit-note', function() {
        var noteId = $(this).attr('data-id');
    
        // Load the edit note modal HTML from the static directory
        $.get('/static/html/editNoteModal.html', function (modalHtml) {
            // Append the modal HTML to the body
            $('body').append(modalHtml);
    
            // Get the note data via AJAX
            ajaxCall('/notes/get/' + noteId, 'GET', null, function (data) {
                // Populate the modal with the retrieved data
                $('#editNoteModal').find('input[name="title"]').val(data.data.title);
                $('#editNoteModal').find('textarea[name="content"]').val(data.data.content);
                $('#updateNoteForm').attr('data-note-id', noteId);
    
                // Populate the categories dropdown
                var categoriesHtml = categories.map(category => `
                    <option value="${category.id}" ${data.data.category_id == category.id ? 'selected' : ''}>${category.name}</option>
                `).join('');
    
                $('#editNoteModal').find('select[name="noteCategory"]').html(categoriesHtml);
    
                // Open the modal
                $('#editNoteModal').modal('show');
    
                // Remove the modal from the DOM after it is closed
                $('#editNoteModal').on('hidden.bs.modal', function () {
                    $(this).remove();
                });
    
                // Handle the update note form submission
                $('#updateNoteForm').off('submit').on('submit', function(event) {
                    event.preventDefault(); // Prevent the default form submission
    
                    // Get the note ID from the form's data attribute
                    var noteId = $(this).data('note-id');
    
                    // Get the form data    
                    var formData = {
                        title: $('#editNoteModal input[name="title"]').val(),
                        category_id: $('#editNoteModal select[name="noteCategory"]').val(),
                        content: $('#editNoteModal textarea[name="content"]').val(),
                        user_id: 1 // Assuming user_id is fixed for now
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
                    ajaxCall(`/notes/put/${noteId}`, 'PUT', formData, function(response) {
                        // Close the modal
                        $('#editNoteModal').modal('hide');
    
                        // Show success toast
                        toastr.success('Note updated successfully');
    
                        // Update the specific note item in the list
                        updateRecords();
                    }, function(xhr, status, error) {
                        toastr.error('Update error: ' + error);
                    });
                });
            }, function (error) {
                toastr.error('Error retrieving note: ' + error);
            });
        });
    });

    // Handle delete note click event
    $(document).on('click', '.delete-note', function (e) {
        e.preventDefault();
        var noteId = $(this).attr('data-id');
    
        // Load the confirmation modal HTML
        $.get('/static/html/confirmationModal.html', function (data) {
            $('body').append(data);
    
            // Set the note ID to the confirm button
            $('#confirmDelete').data('id', noteId);
    
            // Close modal on clicking No or cross button
            $('#cancelDelete, #closeModal').click(function () {
                $('#confirmationModal').remove();
            });
    
            // Confirm delete
            $('#confirmDelete').click(function () {
                var noteId = $(this).data('id'); // Get the note ID from the data attribute
    
                ajaxCall(`/notes/delete/${noteId}`, 'DELETE', {}, function() {
                    // Close the modal
                    $('#confirmationModal').remove();
    
                    // Show success toast
                    toastr.success('Note deleted successfully');
    
                    // Refresh the records list
                    updateRecords();
                }, function(error) {
                    toastr.error('Error deleting note: ' + error);
                });
            });
        });
    });

    // Handle the create note form submission
    $(document).on('submit', '#createNoteForm', function(event) {
        event.preventDefault(); // Prevent the default form submission

        // Get the form data
        var formData = {
            user_id: 1,
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

        ajaxCall('/notes/post/', 'POST', formData, function(data) {
            // Show success toast
            toastr.success('Note created successfully');

            // Clear the form
            $('#createNoteForm')[0].reset();

            // Fetch and render updated records
            updateRecords();
        }, function(error) {
            toastr.error('Error creating note: ' + error);
        });
    });

});