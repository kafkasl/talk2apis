

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
            },
            error: function(error) {
                console.error('error: /gen-script:', error);
                $('#output').text('Error generating code.', error);
            }
        });
    });

    $('#run-button').on('click', async function() {
        $('#output').text("Running...");

        let pyodide = await loadPyodide();
        // Load the 'requests' package
        await pyodide.loadPackage('requests');

        let pythonCode = editor.getValue();
        console.log(pythonCode);

        // Redirect print output and error output
        pyodide.runPython(`
            import io, sys
            sys.stdout = io.StringIO()
            sys.stderr = io.StringIO()
        `);

        try {
            pyodide.runPython(pythonCode);
        } catch (err) {
            $('#output').text(err.message);
            return;
        }

        let output = pyodide.runPython('sys.stdout.getvalue()');
        let error = pyodide.runPython('sys.stderr.getvalue()');

        if (output) {
            $('#output').text(output);
        } else {
            $('#output').text(error);
        }
    });
});
