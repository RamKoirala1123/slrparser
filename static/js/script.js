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
    var textarea = document.getElementById('grammartext');
    textarea.value = "";
    var newText = "E -> E + T | T \nT -> T * F | F \nF -> ( E ) | id"
    textarea.value += newText;
}

document.addEventListener("DOMContentLoaded", function () {
    // Toggle visibility of augmented grammar, parsing table, and follow table on form submission
    document.querySelector('.formss').addEventListener('submit', function (event) {

        document.querySelector('.augmentedgrammar').style.display = 'block';
        document.querySelector('.first-follow').style.display = 'block';
        document.querySelector('.parsingtable').style.display = 'block';

        // Hide "How to" section
        document.querySelector('.how-to').style.display = 'none';
    });
});