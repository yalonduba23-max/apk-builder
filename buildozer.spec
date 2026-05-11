[app]
title = bughunter
package.name = bughunter
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# No python3/hostpython3 version pin — p4a.branch = develop manages this internally
# pyjnius not listed — sdl2 bootstrap adds it automatically
# cython not listed — p4a pins its own version
requirements = python3,hostpython3,kivy==2.3.0,kivymd==1.2.0,aiohttp,requests,certifi,openssl,urllib3,idna,charset-normalizer,multidict,yarl,six

p4a.branch = develop

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,ACCESS_NETWORK_STATE,BIND_VPN_SERVICE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.add_src = src/org/test/bughunter/VpnEngine.java

android.api = 33
android.minapi = 21
android.ndk = 25b
android.build_tools = 34.0.0
android.accept_sdk_license = True
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
