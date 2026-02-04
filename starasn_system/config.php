<?php
/**
 * StarASN System Configuration
 */

// Path for cookies
define('COOKIE_FILE', __DIR__ . '/session_data.txt');

// Credentials
define('STARASN_USERNAME', '198006032003122001');
define('STARASN_PASSWORD', 'Bima041010');

// OCR API (OCR.space is free, register at https://ocr.space/OCRAPI)
define('OCR_SPACE_API_KEY', 'K81317003988957'); 

// Email Notification (Optional)
define('NOTIFY_EMAIL', 'hakimarx@gmail.com');
define('EMAIL_FROM', 'hakimarx@gmail.com');
define('EMAIL_PASS', 'wrou awdc ayan pxlk');

// Geolocation (Samarinda)
define('LATITUDE', -0.4937);
define('LONGITUDE', 117.1505);

// Log file
define('LOG_FILE', __DIR__ . '/app_status.log');

/**
 * Helper function for logging
 */
function app_log($message) {
    if (!defined('LOG_FILE')) return;
    $timestamp = date('Y-m-d H:i:s');
    $logEntry = "[$timestamp] $message\n";
    file_put_contents(LOG_FILE, $logEntry, FILE_APPEND);
    echo $logEntry;
}
