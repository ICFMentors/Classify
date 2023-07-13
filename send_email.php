<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
  $question = $_POST["question"];
  $to = "hamzabandarkar929@gmail.com"; // Replace with your email address
  $subject = "Contact Form Submission";
  $message = "Question: " . $question;
  $headers = "From: hamzabandarkar929@gmail.com"; // Replace with your email address or name

  // Send email
  if (mail($to, $subject, $message, $headers)) {
    echo "Email sent successfully.";
  } else {
    echo "Failed to send email.";
  }
}
?>