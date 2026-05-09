[app]

title = bughunter
package.name = bughunter
package.domain = org.test

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1

requirements = python3,kivy==2.3.0,requests,certifi,openssl,urllib3,idna,charset-normalizer,kivymd

orientation = portrait
fullscreen = 0

android.permissions = INTERNET, ACCESS_NETWORK_STATE, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
# Stable Android configuration
android.api = 34
android.minapi = 28

# VERY IMPORTANT
android.accept_sdk_license = True

# Force stable toolchain
android.ndk = 25b
android.build_tools = 34.0.0

android.archs = armeabi-v7a, arm64-v8a

[buildozer]

log_level = 2
warn_on_root = 1
