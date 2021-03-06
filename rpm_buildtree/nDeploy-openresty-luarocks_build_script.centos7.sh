#!/bin/bash
#Author: Anoop P Alias

##Vars
LUAROCKS_VERSION="2.4.2"
LUAROCKS_RPM_ITER="1.el7"

rm -rf luarocks*

wget http://luarocks.github.io/luarocks/releases/luarocks-${LUAROCKS_VERSION}.tar.gz
tar -xzf luarocks-${LUAROCKS_VERSION}.tar.gz
cd luarocks-${LUAROCKS_VERSION}
./configure --prefix=/etc/nginx/luajit --with-lua=/etc/nginx/luajit --lua-suffix=jit --with-lua-include=/etc/nginx/luajit/include/luajit-2.1
make build
make DESTDIR=$(pwd)/tempo install
cd tempo
fpm -s dir -t rpm -C ../tempo --vendor "Anoop P Alias" --version ${LUAROCKS_VERSION} --iteration ${LUAROCKS_RPM_ITER} -a $(arch) -m anoopalias01@gmail.com -e --description "nDeploy custom luarocks package" --url http://luarocks.github.io/ -d openresty-nDeploy --name openresty-nDeploy-luarocks .
rsync -av openresty-nDeploy-luarocks* root@autom8n.com:/usr/share/nginx/autom8n/CentOS/7/x86_64/
