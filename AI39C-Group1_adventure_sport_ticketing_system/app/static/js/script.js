function toggleMenu(){
    const socialIcons = document.getElementById("socialIcons");
    socialIcons.classList.toggle("show");
}

// ══ Share Button Scroll Animation ══
let scrollTimeout;
const shareBtn = document.getElementById("shareBtn");

window.addEventListener("scroll", () => {
    if (shareBtn) {
        // Add jump animation while scrolling
        shareBtn.classList.add("scrolling");
        
        // Clear existing timeout
        clearTimeout(scrollTimeout);
        
        // Remove animation after scroll stops (300ms)
        scrollTimeout = setTimeout(() => {
            shareBtn.classList.remove("scrolling");
        }, 300);
    }
});