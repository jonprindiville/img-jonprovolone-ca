/**********************************************************************
 * Load more images into the current HTML document (depends on jQuery)*
 *********************************************************************/

// skipped and loaded are expected to have been inserted into the HTML
// doc that this script is loaded from
new_skip = skipped + loaded;

/* Fetches HTML fragment with new images to replace the previous
 * #more-images element. The number of images sought is the number that
 * were on the HTML document that loads this script -- the value of
 * variable 'loaded' (see above note) */
function image_loader() {
    // When the page loaded we got HTML displaying:
    //      images[skipped:skipped+loaded]

    // Now we will load:
    //      images[skipped+loaded:skipped+2*loaded]
    $.get('/n/' + loaded + '/s/' + new_skip + '?fmt=frag', 
        function(data) {
            // Using replaceWith here because the returned fragment will
            // have its own #more-images (with text and class dependant
            // on whether or not there are more images after the current
            // retrieval.)
            $('#more-images').replaceWith(data);
            attach_handler();
            new_skip = new_skip + loaded;

            // Update the navigation at the top of the page -- if somebody
            // hits that link the next page that is loaded should skip over
            // images that we loaded here with our javascript.
            $('#next-link').attr('href', '/n/' + loaded + '/s/' + new_skip );
        }
    );
}

/* Once there are no more images to load we use the following for the
 * #more-images click handler. Toss some snark at the user before dropping
 * #more-images. */
current_warning = 0
warning_fadeout = ['no more', 'that\'s all', '*sigh*', 'take a hint']
function eventually_disappear() {
    if (current_warning < warning_fadeout.length) {
        $('#more-images p.msg').text(warning_fadeout[current_warning++]);
    } else {
        $('#more-images').fadeOut(1000);
    }
}

/* Called on the document becoming ready and after loading new images */
function attach_handler() {
    more = $('#more-images');

    if (more.hasClass('none')) { // we've got no class? :(
        // (something weird happened with our request, we'll just let this
        // be for now -- error hadling shmerror shmandling)
    } else {
        
        // We remove the style attribute to clobber the display:none that is
        // present in the HTML. This way, it will be rendered according 
        // the rules in our CSS.
        more.removeAttr('style');
        
        // We've used the classes [more, no-more] to indicate if there are more
        // images to retrieve after the ones we just got
        if (more.hasClass('more')) {
            more.click(image_loader);
        } if (more.hasClass('no-more')) {
            // If the user continues to click, give a few "warnings" before
            // disappearing the 'more' element
            more.click(eventually_disappear);

            // If we've got no more images we can lose the 'next' nav item
            // (and maybe the whole nav element)
            $('#next-link').fadeOut(1000, function() {
                $('#next-link').remove();
                if ($('header .nav').children().length == 0) {
                    $('header .nav').remove();
                }
            });
        }
    }
}

// Hook it up, bro
$('body').ready(attach_handler);
