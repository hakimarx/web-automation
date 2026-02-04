<?php
/**
 * StarASN System Task Runner
 */

require_once 'StarAsnService.php';

// Only run on working days (Mon-Fri)
$dayOfWeek = date('w');
if ($dayOfWeek == 0 || $dayOfWeek == 6) {
    app_log("Hari libur.");
    exit();
}

$service = new StarAsnService();

// 1. Get Page
$service->getLoginPage();

// 2. Authentication Loop
$maxAttempts = 5;
$isLoggedIn = false;

for ($i = 1; $i <= $maxAttempts; $i++) {
    app_log("Percobaan autentikasi ke-$i...");
    
    $captcha = $service->solveCaptcha();
    if (!$captcha) {
        continue;
    }

    if ($service->login(STARASN_USERNAME, STARASN_PASSWORD, $captcha)) {
        $isLoggedIn = true;
        break;
    }
    
    sleep(2);
    $service->getLoginPage(); 
}

if (!$isLoggedIn) {
    app_log("Autentikasi gagal.");
    exit();
}

// 3. Update Status
$hour = (int)date('H');
$type = ($hour < 12) ? 'masuk' : 'pulang';

app_log("Memulai modul $type...");
$result = $service->doPresence($type);

// 4. Report
if (strpos($result, 'success') !== false) {
    $service->sendEmail("Laporan Status StarASN: $type", "Modul $type berhasil diupdate pada " . date('Y-m-d H:i:s'));
} else {
    $service->sendEmail("Laporan Gagal StarASN: $type", "Gagal update modul $type. Response: $result");
}

app_log("Selesai.");
$service->close();
