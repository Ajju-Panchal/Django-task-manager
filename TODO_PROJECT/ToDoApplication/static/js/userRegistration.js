$(document).ready(function() {
  $("#register-form").submit(function(event) {
    event.preventDefault();
    var username = $("#username").val().trim();
    var password = $("#password").val();
    var confirmPassword = $("#password1").val();
    var email = $("#email").val().trim();
    var mobileNumber = $("#phone").val().trim();

    if (!username || !password || !confirmPassword || !email || !mobileNumber) {
      alert("Please fill in all fields.");
      return;
    }
    if (!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(email)) {
      alert("Please enter a valid email address.");
      return;
    }
    if (!/^[0-9]{10}$/.test(mobileNumber)) {
      alert("Enter a 10-digit phone number.");
      return;
    }
    if (password !== confirmPassword) {
      alert("Passwords do not match.");
      return;
    }
    this.submit();
  });
});
