// idea: don't include 'more' box in template markup, add it here on
// load (also can add loading of previous images)

// Save values
cur_skipped = skipped;
cur_loaded  = loaded;

new_skip = cur_skipped + loaded;

function image_loader() {
    // When the page loaded we got HTML displaying:
    //      images[skipped:skipped+loaded]

    // Now we will load:
    //      images[skipped+loaded:skipped+2*loaded]
    $.get('/n/' + loaded + '/s/' + new_skip + '?fmt=frag', 
        function(data) {
            $('#more-images').before(data);
            new_skip = new_skip + loaded;
        }
    );
}

// On load, make the more link visible, connect it to loading func:
$('body').ready(function() {
    $('#more-images').css('display', '');
    $('#more-images-link').attr('onclick', 'image_loader();');
});
