[app]

title = bughunter
package.name = bughunter
package.domain = org.test

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1

requirements = python3==3.11, hostpython3==3.11, kivy==2.3.0, pyjnius, kivymd, aiohttp, requests, certifi, openssl, urllib3, idna, charset-normalizer, multidict, yarl, attrs, async_timeout

# Important: Use the master branch for python-for-android to fix 404s
p4a.branch = master

orientation = portrait
fullscreen = 0

android.permissions = INTERNET, ACCESS_NETWORK_STATE, BIND_VPN_SERVICE, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# Java Service Setup
android.add_src = src/org/test/bughunter/VpnEngine.java
android.services = VpnEngine:org.test.bughunter.VpnEngine

# Stable Android configuration
android.api = 33
android.minapi = 21

# VERY IMPORTANT
android.accept_sdk_license = True

# Force stable toolchain
android.ndk = 25b
android.build_tools = 34.0.0

android.archs = armeabi-v7a, arm64-v8a

[buildozer]

log_level = 2
warn_on_root = 1
