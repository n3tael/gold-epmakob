function enable_copy_button() {
    const button = document.querySelector("button.link-copy");
    const input = document.querySelector("input.link-copy");

    button.classList.remove("hide");

    button.addEventListener("click", () => {
        copy_to_clipboard(input.value);
    });
}

function fallback_copy_to_clipboard(text) {
    var textArea = document.createElement("textarea");

    textArea.value = text;
    textArea.style.top = "0";
    textArea.style.left = "0";
    textArea.style.position = "fixed";

    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();

    try {
        document.execCommand('copy');
    } catch (err) {
        console.error('[Fallback] Could not copy text: ', err);
    }

    document.body.removeChild(textArea);
}

function copy_to_clipboard(text) {
    if (!navigator.clipboard) {
        fallback_copy_to_clipboard(text);
        return;
    }

    navigator.clipboard.writeText(text).then(null, function(err) {
        console.error('Could not copy text: ', err);
    });
}

document.addEventListener("DOMContentLoaded", enable_copy_button);