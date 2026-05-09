[app]

title = bughunter
package.name = bughunter
package.domain = org.test

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1

requirements = python3,kivy,requests

orientation = portrait
fullscreen = 0

# Permissions (keep minimal for stability)
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# Android settings (ONLY ONCE - no duplicates allowed)
android.api = 34
android.minapi = 28
android.archs = armeabi-v7a, arm64-v8a

# =========================
# DO NOT ADD DUPLICATES BELOW
# =========================

[buildozer]
log_level = 2
warn_on_root = 1
