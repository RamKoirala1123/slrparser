document.addEventListener('DOMContentLoaded', function () {
    const navLinks = document.querySelectorAll('.nav-links li a');
    navLinks.forEach(link => {
        link.addEventListener('click', function () {
            navLinks.forEach(otherLink => otherLink.classList.remove('active'));
            this.classList.add('active');
        });
    });
});

function addTextToTextarea() {
    // Get the textarea element
    var textarea = document.getElementById('grammartext');

    // Add your desired text
    // var newText = " E -> E + T | T
    //  		T -> T * F | F
    //  		F -> ( E ) | id"
    textarea.value = "";
    var newText = "E -> E + T | T \nT -> T * F | F \nF -> ( E ) | id"

    // Append the text to the textarea
    textarea.value += newText;
}