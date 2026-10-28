<?php
// Sanity check of a built _mysql_dump using PHP's own unserialize():
// every row must unserialize, and every element's 'owner' must be its real parent.
// usage: php tools/check_dump.php path/to/_mysql_dump   (or a .ws_data archive)
$f = $argv[1];
if (substr($f, -8) === '.ws_data') { $z = new ZipArchive(); $z->open($f); $data = $z->getFromName('_mysql_dump'); }
else $data = file_get_contents($f);
function parse_values($s){$rows=[];$i=0;$n=strlen($s);while($i<$n){while($i<$n&&$s[$i]!='(')$i++;if($i>=$n)break;$i++;$row=[];while(true){while($s[$i]==' ')$i++;if($s[$i]=="'"){$i++;$v='';while(true){$c=$s[$i];if($c=='\\'){$d=$s[$i+1];$m=['0'=>"\0",'n'=>"\n",'r'=>"\r",'t'=>"\t",'Z'=>"\x1a",'b'=>"\x08"];$v.=$m[$d]??$d;$i+=2;}elseif($c=="'"){$i++;break;}else{$j=strcspn($s,"\\'",$i);$v.=substr($s,$i,$j);$i+=$j;}}$row[]=$v;}else{$j=strcspn($s,",)",$i);$t=trim(substr($s,$i,$j));$row[]=$t==='NULL'?null:$t;$i+=$j;}if($s[$i]==','){$i++;continue;}if($s[$i]==')'){$i++;break;}}$rows[]=$row;}return $rows;}
$errors = 0; $rows = 0; $nodes = 0;
function chk($o, $parent, &$errors, &$nodes, $where) {
  $nodes++; $a = (array)$o;
  if ($parent !== null && array_key_exists('owner', $a) && $a['owner'] !== $parent) { $errors++; echo "owner mismatch in $where id=".($a['id']??'?')."\n"; }
  if (isset($a['contents']) && is_array($a['contents'])) foreach ($a['contents'] as $c) if (is_object($c)) chk($c, $o, $errors, $nodes, $where);
}
foreach (explode("\n", $data) as $line) {
  if (!preg_match('/^INSERT INTO `([^`]+)` VALUES (.*)$/s', $line, $m)) continue;
  foreach (parse_values($m[2]) as $r) { $rows++;
    foreach ($r as $cell) if (is_string($cell) && preg_match('/^(O|a):\d+:/', $cell)) {
      $o = @unserialize($cell);
      if ($o === false) { $errors++; echo "UNSERIALIZE FAILED: {$m[1]} {$r[0]}\n"; continue; }
      if (is_object($o)) chk($o, null, $errors, $nodes, "{$m[1]}/{$r[0]}");
    }
  }
}
echo "rows=$rows nodes=$nodes errors=$errors\n"; exit($errors ? 1 : 0);
