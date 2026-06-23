// Code2Docu Javascript for UserDefined documentation

//Script to exchange language
function changeLang(currentLang) {
    const regEx = new RegExp("/" + currentLang + "/", "gm");

    var currentURL = window.location.href;
    var selectElement = document.getElementById("langSelector");
    var selectedLang = selectElement.options[selectElement.selectedIndex];
    window.document.location.href = currentURL.replace(regEx, "/" + selectedLang.value + "/");
}

// Function to mark every paragraph without text using an extra class.
// This class can be used in the CSS to check whether a paragraph that
// contains an inline math expression has no surrounding text.
document.addEventListener("DOMContentLoaded", function () {
    const paragraphs = document.querySelectorAll("p");
    paragraphs.forEach(paragraph => {
        // Only for paragraphs that contain inline math elements.
        if (hasMathAndInlineClasses(paragraph)) {
            // Check if the paragraph has no text content without considering its descendants.
            // This is necessary because the Node.textContent property returns the text content of
            // the node and all of its descendants.
            const hasNoText = Array.from(paragraph.childNodes).every(node => {
                // hasNoText will be true if every child node is either not a text node or has no text content
                return node.nodeType !== Node.TEXT_NODE || !node.textContent.trim();
            });

            if (hasNoText) {
                // Add a class to the paragraph that we can check in CSS.
                paragraph.classList.add("has-no-text");
            }
        }
    });
});

// Function to check if a paragraph has descendant nodes with both the math and inline CSS classes
function hasMathAndInlineClasses(paragraph) {
    const mathElements = paragraph.querySelectorAll('.math');
    return Array.from(mathElements).some(element => element.classList.contains('inline'));
}
