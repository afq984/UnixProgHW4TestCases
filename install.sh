set -eux
sha256sum -c - <<< 'e381827d362bd12ab0c74eab4f1374be90788fa94b7f7c7f068b5a8d1c5080b8  docroot.tbz'
tar xf docroot.tbz
ln -sf /proc/1/environ testcase/noperm
install -dm755 testcase/xdir1
install -Tm000 testcase/dir1/index.html testcase/xdir1/index.html
install -dm311 testcase/xdir2
install -Tm755 testcase/printenv_php.txt testcase/printenv.php
install -Tm755 testcase/printenv_sh.txt testcase/printenv.sh
chmod -x testcase/printenv_sh.txt
echo '#!/bin/sh
echo "Content-Type: text/plain
"
printenv
echo
cat' > testcase/post.php
chmod +x testcase/post.php
