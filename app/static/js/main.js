function updateRecords() {
    $.ajax({
        url: '/notes/list/',
        method: 'GET',
        success: function(data) {
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
        },
        error: function() {
            toastr.error('Data updation failed');
        }
    });
}


$(document).ready(function () {

    // For Edit
    $(document).on('click', '.edit-note', function() {
        var noteId = $(this).attr('data-id');
    
        // Load the edit note modal HTML from the static directory
        $.get('/static/html/editNoteModal.html', function (modalHtml) {
            // Append the modal HTML to the body
            $('body').append(modalHtml);
    
            // Get the note data via AJAX
            $.ajax({
                url: '/notes/get/' + noteId,
                method: 'GET',
                success: function (data) {
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
    
                        // Send the PUT request using AJAX
                        $.ajax({
                            url: `/notes/put/${noteId}`,
                            type: 'PUT',
                            data: JSON.stringify(formData),
                            contentType: 'application/json',
                            success: function(response) {
                                // Close the modal
                                $('#editNoteModal').modal('hide');
    
                                // Show success toast
                                toastr.success('Note updated successfully');
    
                                // Update the specific note item in the list
                                updateRecords()
                            },
                            error: function(xhr, status, error) {
                                // Handle errors if any
                                console.error('Update error:', error);
                                // Show error toast
                                showToast('Something went wrong', 'red');
                            }
                        });
                    });
                },
                error: function (error) {
                    console.log('Error retrieving note:', error);
                }
            });
        });
    });


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
    
                $.ajax({
                    url: '/notes/delete/' + noteId,
                    method: 'DELETE',
                    success: function () {
                        // Close the modal
                        $('#confirmationModal').remove();
    
                        // Show success toast
                        toastr.success('Note deleted successfully');
    
                        // Refresh the records list
                        updateRecords();
                    },
                    error: function (error) {
                        console.log('Error deleting note:', error);
                        // Show error toast
                        toastr.error('Something went wrong');
                    }
                });
            });
        });
    });


    function fetch_data() {
        $.ajax({
            url: '/notes',
            method: 'GET',
            success: function (data) {

                console.log(data);
            }
        });
    }


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

        $.ajax({
            url: '/notes/post/',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(data) {
                // Show success toast
                toastr.success('Note created successfully');

                // Clear the form
                $('#createNoteForm')[0].reset();

                // Fetch and render updated records
                updateRecords();
            },
            error: function(error) {
                console.log('Error creating note:', error);
                // Show error toast
                toastr.error('Something went wrong');
            }
        });
    });


    
});