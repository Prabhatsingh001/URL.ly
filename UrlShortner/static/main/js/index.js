if (window.history.replaceState) {
    // Remove query parameters from the URL
    const cleanUrl = window.location.protocol + "//" + window.location.host + window.location.pathname;
    window.history.replaceState({}, document.title, cleanUrl);
}