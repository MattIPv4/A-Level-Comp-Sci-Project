(() => {
    const handleClick = (elm) => {
        if (elm.classList.contains("unchecked")) {
            elm.classList.remove("unchecked");
            elm.getElementsByTagName("input")[0].checked = true;
        } else {
            elm.classList.add("unchecked");
            elm.getElementsByTagName("input")[0].checked = false;
        }
    };

    const checkboxes = Array.from(document.getElementsByClassName("checkbox"));
    checkboxes.forEach(function (elm) {
        elm.onclick = () => {
            handleClick(elm);
        };
    });
})();