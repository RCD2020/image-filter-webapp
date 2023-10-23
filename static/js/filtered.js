var editor = CodeMirror.fromTextArea(document.getElementById('code'), {
    lineNumbers: true
});

const GRAYSCALE = `# loop through all of the pixels
for (x = 0; x < width; x = x + 1) {
    for (y = 0; y < height; y = y + 1) {

        # load variables r, g, and b into memory
        loadColor(x, y);

        # get average of colors
        avg = (r + g + b) // 3;

        # apply average to pixel
        pixels[x, y] = rgb(avg, avg, avg);
    };
};`;

const SEPIA = `# loop through pixels
for (x = 0; x < width; x = x + 1)
{
    for (y = 0; y < height; y = y + 1)
    {
        # loads variables r, g, b into memory
        loadColor(x, y);

        # this algorithm applies math to make our image appear sepia toned
        sr = 0.393 * r + 0.769 * g + 0.189 * b + 0.5;
        sg = 0.349 * r + 0.686 * g + 0.168 * b + 0.5;
        sb = 0.272 * r + 0.534 * g + 0.131 * b + 0.5;

        # and now we must check that none of our pixels went over 255
        if (sr > 255)
        {
            sr = 255;
        };
        if (sg > 255)
        {
            sg = 255;
        };
        if (sb > 255)
        {
            sb = 255;
        };

        # save it to image
        pixels[x, y] = rgb(sr, sg, sb);
    };
};`;

function grayscale() {
    editor.getDoc().setValue(GRAYSCALE);
}


function sepia() {
    editor.getDoc().setValue(SEPIA);
}