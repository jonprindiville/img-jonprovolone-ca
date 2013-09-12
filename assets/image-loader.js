/* Load more images into the current HTML document
 *
 * TODO: update nav links as more images get loaded into the page?
 */

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
        }
    );
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
            more.attr('onclick', 'image_loader();');
        } if (more.hasClass('no-more')) {
            more.attr('onclick', '$("#more-images").fadeOut(1000);');
        }
    }
}

// Hook it up, bro
$('body').ready(attach_handler);
