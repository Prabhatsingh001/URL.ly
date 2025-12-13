function copyUrl(button) {
    const url = button.getAttribute("data-url");
    navigator.clipboard.writeText(url).then(() => {
        showToast("Copied to clipboard!", false);
    }).catch(err => {
        console.error("Failed to copy: ", err);
        showToast("Failed to copy!", true);
    });
}


function showToast(message, isError = false) {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    
    // Enhanced toast styling
    const baseClasses = "fixed bottom-8 left-1/2 transform -translate-x-1/2 z-50 px-6 py-3 rounded-2xl shadow-2xl text-sm font-semibold backdrop-blur-lg border transition-all duration-500 ease-out";
    const successClasses = "bg-emerald-500/90 text-white border-emerald-400/50 shadow-emerald-500/25";
    const errorClasses = "bg-red-500/90 text-white border-red-400/50 shadow-red-500/25";
    
    toast.className = `${baseClasses} ${isError ? errorClasses : successClasses}`;

    // Show animation
    toast.classList.remove("hidden", "opacity-0", "translate-y-4", "scale-95");
    toast.classList.add("opacity-100", "scale-100");

    // Hide animation
    setTimeout(() => {
        toast.classList.add("opacity-0", "translate-y-4", "scale-95");
    }, 2500);

    setTimeout(() => {
        toast.classList.add("hidden");
    }, 3000);
}

function confirmDelete() {
    return confirm('Are you sure you want to delete this URL?\n\nThis action cannot be undone.');
}

document.querySelectorAll('button, a').forEach(element => {
    element.addEventListener('click', function(e) {
        if (!this.classList.contains('group/copy') && !this.classList.contains('group/edit') && !this.classList.contains('group/delete')) return;
        
        const ripple = document.createElement('span');
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.classList.add('absolute', 'bg-white/30', 'rounded-full', 'animate-ping', 'pointer-events-none');
        
        this.style.position = 'relative';
        this.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    });
});