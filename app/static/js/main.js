$(document).ready(function () {
    // Edit note button click handler
    $('.edit-note').on('click', function() {
        var noteId = $(this).attr('data-id');

        // Load the edit note modal HTML from the static directory
        $.get('/static/html/editNoteModal.html', function (modalHtml) {
            // Append the modal HTML to the body
            $('body').append(modalHtml);

            // Get the note data via AJAX
            $.ajax({
                url: '/notes/' + noteId,
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

                    $('#editNoteModal').find('select[name="noteCategory"]').append(categoriesHtml);

                    // Open the modal
                    $('#editNoteModal').modal('show');

                    // Remove the modal from the DOM after it is closed
                    $('#editNoteModal').on('hidden.bs.modal', function () {
                        $(this).remove();
                    });
                },
                error: function (error) {
                    console.log('Error retrieving note:', error);
                }
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

    // Update note form submission handler
    $('#updateNoteForm').on('submit', function(event) {
        console.log('Update note form submitted');
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
                fetch_data(); // Fetch the updated data
                console.log('Note updated successfully:', response);
                // Store a flag in localStorage to show the toast after page reload
                localStorage.setItem('showUpdateSuccessToast', 'true');

                // Reload the page
                // location.reload();
            },
            error: function(xhr, status, error) {
                // Handle errors if any
                console.error('Update error:', error);
                // Show error toast
                showToast('Something went wrong', 'red');
            }
        });
    });

    // Check if the success toast should be shown after page reload
    if (localStorage.getItem('showSuccessToast') === 'true') {
        // Show success toast
        showToast('Note created successfully', 'green');

        // Remove the flag from localStorage
        localStorage.removeItem('showSuccessToast');
    }

    // Check if the update success toast should be shown after page reload
    if (localStorage.getItem('showUpdateSuccessToast') === 'true') {
        // Show update success toast
        showToast('Note updated successfully', 'green');

        // Remove the flag from localStorage
        localStorage.removeItem('showUpdateSuccessToast');
    }

    $('#createNoteForm').on('submit', function(event) {
        event.preventDefault(); // Prevent the default form submission
        
        // Get the form data
        var formData = {
            user_id : 1,
            title: $('input[placeholder="Note Title"]').val(),
            category_id: $('#noteCategory').val(),
            content: $('textarea[placeholder="Note Content"]').val()
        };

        $.ajax({
            url: '/notes/post/',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function (data) {
                // Store a flag in localStorage to show the toast after page reload
                localStorage.setItem('showSuccessToast', 'true');

                // Reload the page
                location.reload();
            },
            error: function (error) {
                console.log('Error creating note:', error);
                // Show error toast
                showToast('Something went wrong', 'red');
            }
        });
    });

    // Delete note button click handler
    $('.delete-note').click(function (e) {
        e.preventDefault();
        var noteId = $(this).data('id'); // Get the note ID from the data attribute
    
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
                        // Store a flag in localStorage to show the toast after page reload
                        localStorage.setItem('showDeleteSuccessToast', 'true');
    
                        // Reload the page
                        location.reload();
                    },
                    error: function (error) {
                        console.log('Error deleting note:', error);
                        // Show error toast
                        showToast('Something went wrong', 'red');
                    }
                });
    
                // Remove the modal
                $('#confirmationModal').remove();
            });
        });
    });


    // Check if the delete success toast should be shown after page reload
    if (localStorage.getItem('showDeleteSuccessToast') === 'true') {
        // Show delete success toast
        showToast('Note deleted successfully', 'red');

        // Remove the flag from localStorage
        localStorage.removeItem('showDeleteSuccessToast');
    }

    // Function to show toast with dynamic message and color
    function showToast(message, color) {
        $('body').append(`<div id="dynamicToast" style="position: fixed; top: -50px; right: 20px; background-color: ${color}; color: white; padding: 10px; border-radius: 5px; transition: top 0.5s;">${message}</div>`);
        setTimeout(function() {
            $('#dynamicToast').css('top', '20px');
        }, 100); // Small delay to trigger the transition
        setTimeout(function() {
            $('#dynamicToast').css('top', '-50px');
            setTimeout(function() {
                $('#dynamicToast').remove();
            }, 500); // Wait for the transition to complete before removing
        }, 3000);
    }
});