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

const SOBEL = `# makeRef() will make a reference image,
# so that we can look at the original image and make changes at the same time
makeRef();

# loop through pixels
for (x = 0; x < width; x = x + 1)
{
    for (y = 0; y < height; y = y + 1)
    {
        # initializes our edge values
        rgx = 0;
        rgy = 0;
        ggx = 0;
        ggy = 0;
        bgx = 0;
        bgy = 0;

        # checks each pixel around target pixel and applies it if it is a valid pixel
        if (x != 0 && y != 0)
        {
            loadRef(x - 1, y - 1);

            rgx = rgx - 1 * r;
            rgy = rgy - 1 * r;
            ggx = ggx - 1 * g;
            ggy = ggy - 1 * g;
            bgx = bgx - 1 * b;
            bgy = bgy - 1 * b;
        };
        if (y != 0)
        {
            loadRef(x, y - 1);

            rgy = rgy - 2 * r;
            ggy = ggy - 2 * g;
            bgy = bgy - 2 * b;
        };
        if (y != 0 && x != width - 1)
        {
            loadRef(x + 1, y - 1);

            rgx = rgx + r;
            ggx = ggx + g;
            bgx = bgx + b;
            rgy = rgy - 1 * r;
            ggy = ggy - 1 * g;
            bgy = bgy - 1 * b;
        };
        if (x != width - 1)
        {
            loadRef(x + 1, y);

            rgx = rgx + 2 * r;
            ggx = ggx + 2 * g;
            bgx = bgx + 2 * b;
        };
        if (y != height - 1 && x != width - 1)
        {
            loadRef(x + 1, y + 1);

            rgx = rgx + r;
            ggx = ggx + g;
            bgx = bgx + b;
            rgy = rgy + r;
            ggy = ggy + g;
            bgy = bgy + b;
        };
        if (y != height - 1)
        {
            loadRef(x, y + 1);

            rgy = rgy + 2 * r;
            ggy = ggy + 2 * g;
            bgy = bgy + 2 * b;
        };
        if (y != height - 1 && x != 0)
        {
            loadRef(x - 1, y + 1);

            rgx = rgx - 1 * r;
            ggx = ggx - 1 * g;
            bgx = bgx - 1 * b;
            rgy = rgy + r;
            ggy = ggy + g;
            bgy = bgy + b;
        };
        if (x != 0)
        {
            loadRef(x - 1, y);

            rgx = rgx - 2 * r;
            ggx = ggx - 2 * g;
            bgx = bgx - 2 * b;
        };

        # calculate our rgb values using our edge values
        rg = rgx * rgx + rgy * rgy;
        gg = ggx * ggx + ggy * ggy;
        bg = bgx * bgx + bgy * bgy;
        rg = sqrt(rg) + 0.5;
        gg = sqrt(gg) + 0.5;
        bg = sqrt(bg) + 0.5;

        # ensure that none of the values are over 255
        if (rg > 255)
        {
            rg = 255;
        };
        if (gg > 255)
        {
            gg = 255;
        };
        if (bg > 255)
        {
            bg = 255;
        };

        # saves values to image
        pixels[x, y] = rgb(rg, gg, bg);
    };
};`;

function grayscale() {
    editor.getDoc().setValue(GRAYSCALE);
}


function sepia() {
    editor.getDoc().setValue(SEPIA);
}


function sobel() {
    editor.getDoc().setValue(SOBEL);
}