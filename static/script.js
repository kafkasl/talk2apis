

$(document).ready(function() {
    // Initialize ACE Editor
    var editor = ace.edit("editor"); // Make sure your HTML has a div with id="editor" for this
    // editor.setTheme("ace/theme/tomorrow_night");
    // editor.session.setMode("ace/mode/python");
    // editor.setValue("// Write Python code here...", -1); // Default text
    editor.setTheme("ace/theme/monokai");
    editor.getSession().setMode("ace/mode/python");
    editor.setOptions({
        maxLines: Infinity,

    });

    // Resize editor when content is updated
    editor.getSession().on('change', function() {
        editor.resize();
    });
    // Handle form submission to fetch Python code
    $('#myForm').on('submit', function(e) {
        e.preventDefault();

        $('#output').text("Generating script...");

        // Disable the submit button until the request is complete
        var submitButton = document.getElementById('submit-button');
        submitButton.disabled = true;

        var service = $('#service').val();
        var token = $('#token').val();
        var prompt = $('#prompt').val();

        // Send data to the server
        $.ajax({
            url: '/gen-script',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ service: service, token: token, prompt: prompt }),
            success: function(response) {
                // Set the returned code in the ACE Editor
                editor.setValue(response.code, -1); // Update ACE Editor content

                // Handle the endpoints array
                var endpointsElement = $('#endpoints');
                endpointsElement.empty(); // Clear the previous endpoints
                response.endpoints.forEach(function(endpoint) {
                    // Convert the endpoint object to a nicely formatted JSON string
                    var endpointStr = JSON.stringify(endpoint, null, 2);
                    // Append the endpoint string to the endpoints element
                    endpointsElement.append('<pre>' + endpointStr + '</pre>');
                });

                // Enable the submit button
                $('#output').text("");
                submitButton.disabled = false;
            },
            error: function(error) {
                console.error('error: /gen-script:', error);
                $('#output').text('Error generating code.', error);
                submitButton.disabled = false;
            }
        });
    });

    $('#run-button').on('click', async function() {
        $('#output').text("Running...");

        // Disable the run button until the request is complete
        var runButton = document.getElementById('run-button');
        runButton.disabled = true;

        let pythonCode = editor.getValue();
        console.log(pythonCode);

        try {
            let response = await fetch('/run_code', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ code: pythonCode })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            let result = await response.json();

            if (result.output) {
                $('#output').text(result.output);
            } else {
                $('#output').text(result.error);
            }
        } catch (err) {
            $('#output').text(err.message);
        }
        finally {
            runButton.disabled = false;
        }
    });
});
