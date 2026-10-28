<?php
// Emulates websico's .htaccess for `php -S`
$root = $_SERVER['DOCUMENT_ROOT'];
$uri = urldecode(parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH));
$f = preg_match('#^/cache/(ws_images/.*)$#', $uri, $m) ? $root.'/ws_lib/ws_core/'.$m[1] : $root.$uri;
if (!is_file($f) && preg_match('#/((data|ws_lib)/.*)$#', $uri, $m)) $f = $root.'/'.$m[1];
if ($uri !== '/' && is_file($f) && !preg_match('/\.php$/', $f)) {
  $types = ['css'=>'text/css','js'=>'application/javascript','png'=>'image/png','jpg'=>'image/jpeg','jpeg'=>'image/jpeg','gif'=>'image/gif','svg'=>'image/svg+xml','ico'=>'image/x-icon','pdf'=>'application/pdf','woff2'=>'font/woff2','woff'=>'font/woff','webp'=>'image/webp'];
  $ext = strtolower(pathinfo($f, PATHINFO_EXTENSION));
  if (isset($types[$ext])) header('Content-Type: '.$types[$ext]);
  readfile($f); return true;
}
if (preg_match('/\.php$/', $f) && is_file($f)) { chdir(dirname($f)); require $f; return true; }
chdir($root); require $root.'/index.php';
