[app]
title = Deprem TR
package.name = depremtr
package.domain = org.seyidali
source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,atlas,json,txt
version = 0.1.0

# Kivy 2.3.0 ve HTTPS için gerekli tüm paketler
requirements = python3,kivy==2.3.0,kivymd,pillow,requests,urllib3,certifi,charset-normalizer,idna,openssl

orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

[android]
# API 33 ve NDK 25b uyumu (En stabil ikili)
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a, armeabi-v7a
android.permissions = INTERNET, ACCESS_NETWORK_STATE
android.private_storage = True
android.allow_backup = False
android.enable_androidx = True
android.accept_sdk_license = True

# Derleme sırasında Buildozer'ın kafasının karışmaması için boş bırakıyoruz, 
# YML dosyasında bu yolları biz dikte edeceğiz.
android.sdk_path = 
android.ndk_path = 
