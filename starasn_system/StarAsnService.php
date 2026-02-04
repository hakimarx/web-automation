<?php
/**
 * StarASN Service Class
 * Handles Login and Presence
 */

require_once 'config.php';

class StarAsnService {
    private $ch;
    private $csrf_token = '';
    private $tkv = '';

    public function __construct() {
        $this->initCurl();
    }

    private function initCurl() {
        $this->ch = curl_init();
        curl_setopt($this->ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($this->ch, CURLOPT_COOKIEJAR, COOKIE_FILE);
        curl_setopt($this->ch, CURLOPT_COOKIEFILE, COOKIE_FILE);
        curl_setopt($this->ch, CURLOPT_USERAGENT, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
        curl_setopt($this->ch, CURLOPT_FOLLOWLOCATION, true);
        curl_setopt($this->ch, CURLOPT_SSL_VERIFYPEER, false);
    }

    public function getLoginPage() {
        app_log("Membuka halaman login...");
        curl_setopt($this->ch, CURLOPT_URL, 'https://star-asn.kemenimipas.go.id/authentication/login');
        curl_setopt($this->ch, CURLOPT_POST, false);
        $html = curl_exec($this->ch);

        // Extract CSRF meta token
        if (preg_match('/content="([^"]+)" name="csrf-token"/', $html, $matches)) {
            $this->csrf_token = $matches[1];
            app_log("Security Token found.");
        }

        // Extract tkv hidden input
        if (preg_match('/name="tkv" value="([^"]+)"/', $html, $matches)) {
            $this->tkv = $matches[1];
            app_log("Verification segment found.");
        }

        return $html;
    }

    public function solveCaptcha() {
        app_log("Loading security image...");
        $captchaUrl = 'https://star-asn.kemenimipas.go.id/authentication/captcha?t=' . round(microtime(true) * 1000);
        curl_setopt($this->ch, CURLOPT_URL, $captchaUrl);
        curl_setopt($this->ch, CURLOPT_POST, false);
        $imageData = curl_exec($this->ch);

        if (!$imageData) {
            app_log("Gagal memuat data keamanan.");
            return null;
        }

        // Save temporarily
        $tempPath = __DIR__ . '/temp_auth.png';
        file_put_contents($tempPath, $imageData);

        // Solve using OCR.space
        app_log("Verifikasi data keamanan...");
        $ocrUrl = 'https://api.ocr.space/parse/image';
        
        $postData = [
            'apikey' => OCR_SPACE_API_KEY,
            'isOverlayRequired' => 'false',
            'file' => new CURLFile($tempPath),
            'language' => 'eng',
            'scale' => 'true',
            'isTable' => 'false',
            'OCREngine' => '2' 
        ];

        $chOcr = curl_init();
        curl_setopt($chOcr, CURLOPT_URL, $ocrUrl);
        curl_setopt($chOcr, CURLOPT_POST, true);
        curl_setopt($chOcr, CURLOPT_POSTFIELDS, $postData);
        curl_setopt($chOcr, CURLOPT_RETURNTRANSFER, true);
        $response = curl_exec($chOcr);
        curl_close($chOcr);

        $result = json_decode($response, true);
        if (isset($result['ParsedResults'][0]['ParsedText'])) {
            $text = trim($result['ParsedResults'][0]['ParsedText']);
            $text = preg_replace('/[^A-Za-z0-9]/', '', $text);
            app_log("Security data processed.");
            return $text;
        }

        app_log("Gagal memproses data keamanan.");
        return null;
    }

    public function login($username, $password, $captcha) {
        app_log("Autentikasi akun...");
        $loginUrl = 'https://star-asn.kemenimipas.go.id/authentication/login';
        
        $postBody = [
            'tkv' => $this->tkv,
            'username' => $username,
            'password' => $password,
            'kv-captcha' => $captcha
        ];

        curl_setopt($this->ch, CURLOPT_URL, $loginUrl);
        curl_setopt($this->ch, CURLOPT_POST, true);
        curl_setopt($this->ch, CURLOPT_POSTFIELDS, $postBody);
        
        curl_setopt($this->ch, CURLOPT_HTTPHEADER, [
            'X-Requested-With: XMLHttpRequest',
            'KV-TOKEN: ' . $this->csrf_token
        ]);

        $response = curl_exec($this->ch);
        $resObj = json_decode($response, true);

        if (isset($resObj['status']) && $resObj['status'] == 'success') {
            app_log("Sesi berhasil dibuka.");
            return true;
        } else {
            $error = isset($resObj['message']) ? $resObj['message'] : 'Gagal';
            app_log("Sesi gagal dibuka: $error");
            return false;
        }
    }

    public function checkStatus() {
        app_log("Mengecek modul...");
        curl_setopt($this->ch, CURLOPT_URL, 'https://star-asn.kemenimipas.go.id/statistic');
        curl_setopt($this->ch, CURLOPT_POST, false);
        curl_setopt($this->ch, CURLOPT_HTTPHEADER, []); 
        $html = curl_exec($this->ch);

        if (strpos($html, 'PRESENSI MASUK') !== false) {
            app_log("Modul termuat.");
            return $html;
        }

        app_log("Modul tidak ditemukan.");
        return null;
    }

    public function doPresence($type = 'masuk') {
        app_log("Update status $type...");
        $url = 'https://star-asn.kemenimipas.go.id/presence/save'; 
        
        $postData = [
            'latitude' => LATITUDE,
            'longitude' => LONGITUDE,
            'type' => $type 
        ];

        curl_setopt($this->ch, CURLOPT_URL, $url);
        curl_setopt($this->ch, CURLOPT_POST, true);
        curl_setopt($this->ch, CURLOPT_POSTFIELDS, http_build_query($postData));
        curl_setopt($this->ch, CURLOPT_HTTPHEADER, [
            'X-Requested-With: XMLHttpRequest',
            'KV-TOKEN: ' . $this->csrf_token
        ]);

        $response = curl_exec($this->ch);
        app_log("Response status: Update selesai");
        
        return $response;
    }

    public function sendEmail($subject, $message) {
        if (NOTIFY_EMAIL === '' || EMAIL_FROM === '') return;

        app_log("Mengirim laporan...");
        
        $to = NOTIFY_EMAIL;
        $headers = "From: " . EMAIL_FROM . "\r\n";
        $headers .= "Reply-To: " . EMAIL_FROM . "\r\n";
        $headers .= "X-Mailer: PHP/" . phpversion();

        @mail($to, $subject, $message, $headers);
    }

    public function close() {
        curl_close($this->ch);
    }
}
