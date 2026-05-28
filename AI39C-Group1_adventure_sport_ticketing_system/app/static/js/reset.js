document.getElementById("forgot-form").addEventListener("submit", function(e){

    e.preventDefault();

    const newPassword = document.getElementById("new-password").value;
    const confirmPassword = document.getElementById("confirm-password").value;

    if(newPassword !== confirmPassword){
        alert("Passwords do not match!");
        return;
    }

    if(newPassword.length < 6){
        alert("Password must be at least 6 characters!");
        return;
    }

    alert("Password Reset Successful!");

    window.location.href = "/login";

});