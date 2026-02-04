<?php
require_once 'StarAsnBot.php';

$bot = new StarAsnBot();
$bot->getLoginPage();
$captcha = $bot->solveCaptcha();

if ($captcha) {
    if ($bot->login(STARASN_USERNAME, STARASN_PASSWORD, $captcha)) {
        $dashboard = $bot->checkStatus();
        if ($dashboard) {
            file_put_contents('dashboard_dump.html', $dashboard);
            bot_log("Dashboard dumped to dashboard_dump.html");
        }
    }
}
$bot->close();
