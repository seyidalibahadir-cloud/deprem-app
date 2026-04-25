# main.py
import os
import sys

# --- ANDROID SSL VE GRAFİK YAMASI (KRİTİK) ---
try:
    import certifi
    os.environ['SSL_CERT_FILE'] = certifi.where()
    os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
except ImportError:
    pass

os.environ['KIVY_GL_BACKEND'] = 'sdl2'
# --------------------------------------------

from __future__ import annotations
import re
from datetime import datetime
from threading import Thread

import requests
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel

# AFAD bazen User-Agent kontrolü yapar
AFAD_URL = "https://deprem.afad.gov.tr/apiv2/event/filter"
TIMEOUT = 15

# ... (Buradan sonrası senin yazdığın fonksiyonlar: safe_text, parse_time vb.)
# NOT: Fonksiyonlarını aynen koru, ama fetch_earthquakes içine verify=certifi.where() ekledim:

def fetch_earthquakes():
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10) DepremApp/1.0",
        "Accept": "application/json",
    }
    
    # verify=certifi.where() Android'de SSL hatasını bitirir
    import certifi
    response = requests.get(AFAD_URL, headers=headers, timeout=TIMEOUT, verify=certifi.where())
    response.raise_for_status()

    try:
        payload = response.json()
    except Exception:
        return []

    items = extract_list(payload)
    results = []
    for item in items:
        if not isinstance(item, dict): continue
        if not is_turkiye_event(item): continue
        results.append(normalize_event(item))

    results.sort(key=lambda x: x["dt"] or datetime.min, reverse=True)
    return results

# ... (Senin DepremApp sınıfın ve geri kalan tüm UI kodların aynen devam eder)
# Sadece on_start içine bir try-except daha ekleyerek güvenliği artıralım:

class DepremApp(MDApp):
    # ... (Senin build metodun)
    
    def refresh_data(self):
        if self.loading:
            return
        self.loading = True
        self.set_status("Depremler yükleniyor...")
        self.events_box.clear_widgets()
        # Thread kullanımı Android için en doğrusu, UI'ı dondurmaz
        thread = Thread(target=self._refresh_worker, daemon=True)
        thread.start()

# ... (Geri kalan tüm kodun)

if __name__ == "__main__":
    try:
        DepremApp().run()
    except Exception as e:
        print(f"UYGULAMA HATASI: {e}")
