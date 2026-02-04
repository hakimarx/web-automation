<?php
echo "<h3>Sistem Informasi Jalur Hosting</h3>";
echo "Path Lengkap Folder Ini: <br><b>" . __DIR__ . "</b>";
echo "<br><br>";
echo "Salin perintah ini untuk dimasukkan ke menu Cron Jobs di cPanel:<br>";
echo "<pre style='background: #eee; padding: 10px; border: 1px solid #ccc;'>";
echo "/usr/local/bin/php " . __DIR__ . "/run.php";
echo "</pre>";
echo "<br>";
echo "Informasi ini berguna untuk verifikasi sistem berkala.";
?>
