[app]
title = Deprem App
package.name = depremapp
package.domain = org.seyidali
source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,atlas,json,txt
version = 0.1.0

# ZIRHLI REQUIREMENTS: requests için gereken tüm SSL ve ağ bağımlılıkları eklendi
requirements = python3,kivy==2.3.0,kivymd,requests,urllib3,certifi,charset-normalizer,idna

orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

[android]
# Android 13 (API 33) uyumluluğu
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21

# Modern ve eski telefonlar için çift mimari
android.archs = arm64-v8a, armeabi-v7a

# Gerekli izinler
android.permissions = INTERNET, ACCESS_NETWORK_STATE

# HTTPS (SSL) hatalarını önlemek için certifi kullanımı zorunludur
android.meta_data = com.google.android.gms.version=@integer/google_play_services_version

android.private_storage = True
android.allow_backup = False

# Uygulama ikonu (Eğer icon.png varsa açarsın)
# icon.filename = icon.png

[python]
# Python optimizasyonları
