//  The previous calculator code...
function calculate(expression) {
    try {
        let result = eval(expression);
        return result;
    } catch (error) {
        alert("Error: " + error.message);
        return null;
    }
}

function updateDisplay(value) {
    document.getElementById('display').innerHTML = value;
}