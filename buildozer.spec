[app]
title = bughunter
package.name = bughunter
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# Fix: use 3.11.0 not 3.11 (GitHub tag is v3.11.0, not v3.11)
requirements = python3==3.11.0,hostpython3==3.11.0,kivy==2.3.0,pyjnius==1.6.1,kivymd==1.2.0,aiohttp,requests,cython,certifi,openssl,urllib3,idna,charset-normalizer,multidict,async_timeout,attrs,yarl,six,filetype,pillow
# Use master branch for latest bug fixes
p4a.version = 2024.01.21

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,ACCESS_NETWORK_STATE,BIND_VPN_SERVICE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.add_src = src/org/test/bughunter/VpnEngine.java
android.services = VpnEngine:org.test.bughunter.VpnEngine

android.api = 33
android.minapi = 21
android.accept_sdk_license = True
android.ndk = 25b
android.build_tools = 34.0.0
android.archs = armeabi-v7a, arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
