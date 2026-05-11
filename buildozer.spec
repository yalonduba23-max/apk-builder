[app]
title = bughunter
package.name = bughunter
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# KEY FIXES:
# 1. Removed python3==3.11.0 version pin (causes grp/spwd source compile failures)
# 2. Downgraded pyjnius to 1.4.2 (1.6.1 breaks with Python 3.11 Cython)
# 3. Removed pillow (no Android wheel or p4a recipe)
# 4. Removed async_timeout (bundled inside aiohttp, causes conflicts)
# 5. Removed attrs (not needed directly)
# 6. android.modules is NOT a valid buildozer key — removed
requirements = python3==3.11,hostpython3==3.11,kivy==2.3.0,pyjnius==1.4.2,kivymd==1.2.0,aiohttp,requests,cython,certifi,openssl,urllib3,idna,charset-normalizer,multidict,yarl,six,filetype

p4a.version = 2024.01.21
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

# Single arch for debug builds — add armeabi-v7a back only for release
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
