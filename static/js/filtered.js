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

function grayscale() {
    editor.getDoc().setValue(GRAYSCALE);
}