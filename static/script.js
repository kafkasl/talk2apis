// Initialize Ace Editor
var editor = ace.edit("editor");
editor.setTheme("ace/theme/monokai");
editor.session.setMode("ace/mode/javascript");

// Set default value
editor.setValue("// Write your code here...");


// Handle form submission
$('#myForm').on('submit', function(e) {
    e.preventDefault();

    var service = $('#service').val();
    var token = $('#token').val();
    var prompt = $('#prompt').val();

    $.ajax({
        url: '/gen-script',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ service: service, token: token, prompt: prompt }),
        success: function(response) {
            editor.setValue(response.code);
        },
        error: function(error) {
            console.error(error);
        }
    });
});

// Run code when the run button is clicked
$('#run-button').on('click', function() {
    var code = editor.getValue();
    eval(code);
});