document.addEventListener('DOMContentLoaded', function() {
    // ==========================
    // Toggle Edit Forms
    // ==========================
    function toggleEdit(field) {
        const editForm = document.getElementById(`edit-${field}`);
        const displayEl = document.getElementById(`display-${field}`);

        if (!editForm) return;

        editForm.classList.toggle('hidden');
        if (displayEl) displayEl.classList.toggle('hidden');

        // Focus first input
        if (!editForm.classList.contains('hidden')) {
            const input = editForm.querySelector('input, textarea');
            if (input) input.focus();
        }
    }

    window.toggleEdit = toggleEdit; // expose globally for inline onclicks

    // ==========================
    // Hide Add Link Form after submit
    // ==========================
    function hideFormAfterSubmit() {
        setTimeout(() => {
            const addLinkForm = document.getElementById('addLinkForm');
            if (addLinkForm) addLinkForm.classList.add('hidden');
        }, 100);
    }

    window.hideFormAfterSubmit = hideFormAfterSubmit;

    // ==========================
    // Copy Shareable Link
    // ==========================
    const copyBtn = document.getElementById('copyBtn');
    const shareLink = document.getElementById('shareLink');
    const toast = document.getElementById('copiedToast');

    if (copyBtn && shareLink && toast) {
        copyBtn.addEventListener('click', async () => {
            try {
                await navigator.clipboard.writeText(shareLink.value);
                showToast();
            } catch (e) {
                shareLink.select();
                document.execCommand('copy');
                showToast();
            }
        });

        function showToast() {
            toast.classList.remove('opacity-0');
            toast.classList.add('opacity-100');
            setTimeout(() => {
                toast.classList.remove('opacity-100');
                toast.classList.add('opacity-0');
            }, 2000);
        }
    }

    // ==========================
    // Auto-hide edit forms when clicking outside
    // ==========================
    document.addEventListener('click', function(e) {
        const editForms = document.querySelectorAll('[id^="edit-"]');
        editForms.forEach(form => {
            if (!form.contains(e.target) && !e.target.closest('button[onclick*="toggleEdit"]')) {
                form.classList.add('hidden');
                const field = form.id.replace('edit-', '');
                const displayEl = document.getElementById(`display-${field}`);
                if (displayEl) displayEl.classList.remove('hidden');
            }
        });
    });

    // ==========================
    // Slide-in animation for new elements
    // ==========================
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(mutation => {
            mutation.addedNodes.forEach(node => {
                if (node.nodeType === 1 && node.classList.contains('slide-in')) {
                    node.style.animation = 'slideIn 0.3s ease-out';
                }
            });
        });
    });

    observer.observe(document.body, { childList: true, subtree: true });

    // ==========================
    // Flash Alert
    // ==========================
    const alert = document.getElementById("flash-alert");
    const closeBtn = document.getElementById("alert-close");

    if (alert) {
        alert.style.transition = "all 0.3s ease-out";
        alert.style.transform = "translate(-50%, -20px)";
        alert.style.opacity = "10";

        setTimeout(() => {
            alert.style.transform = "translate(-50%, 0)";
            alert.style.opacity = "1";
        }, 50);

        setTimeout(() => {
            alert.style.transition = "all 0.3s ease";
            alert.style.opacity = "0";
            alert.style.transform = "translate(-50%, -10px)";
            setTimeout(() => alert.remove(), 300);
        }, 3000);

        if (closeBtn) {
            closeBtn.addEventListener("click", () => {
                alert.style.transition = "all 0.3s ease";
                alert.style.opacity = "0";
                alert.style.transform = "translate(-50%, -10px)";
                setTimeout(() => alert.remove(), 300);
            });
        }
    }
});
