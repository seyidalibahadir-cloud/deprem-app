[app]
title = Deprem TR
package.name = depremtr
package.domain = org.seyidali
source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,atlas,json,txt
version = 0.1.0

# 🛡️ %100 ZIRHLI REQUIREMENTS: 
# openssl -> Ağ bağlantısının C çekirdeği için
# pillow -> KivyMD arayüz bileşenlerinin çökmemesi için
requirements = python3,kivy==2.3.0,kivymd,pillow,requests,urllib3,certifi,charset-normalizer,idna,openssl

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

android.private_storage = True
android.allow_backup = False

# ✅ KivyMD'nin Android'de modern UI ile çalışması için ZORUNLU satır!
android.enable_androidx = True

# 🛠️ P4A (Python for Android) Optimizasyonu
# Derleme sırasında en stabil ana dalı kullanmasını sağlar
p4a.branch = master

[python]
# Python optimizasyonları
