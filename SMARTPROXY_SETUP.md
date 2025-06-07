# SmartProxy Setup - 3-dniowy DARMOWY trial! 🎉

## 🚀 SmartProxy (Rekomendowana opcja)

### ✅ Dlaczego SmartProxy:
- **3-dniowy DARMOWY trial** z 100MB
- **99.55% success rate** bypass Cloudflare
- **115M+ residential IPs** w 195+ krajach
- **Sticky sessions** (IP nie zmienia się)
- **24/7 support**

---

## 📝 INSTRUKCJA REJESTRACJI (3 minuty)

### 1. Idź na stronę SmartProxy
```bash
# Otwórz w przeglądarce:
open https://smartproxy.com/proxies/residential-proxies
```

### 2. Kliknij "Start free trial"
- Znajdziesz przycisk **"Start free trial"** na stronie
- **NIE** potrzebujesz karty kredytowej!

### 3. Wypełnij formularz rejestracji:
- **Email**: Twój prawdziwy email
- **Password**: Silne hasło  
- **Country**: Poland lub dowolny
- Zaakceptuj Terms of Service

### 4. Potwierdź email
- Sprawdź skrzynkę emailową
- Kliknij link w mailu od SmartProxy

### 5. Znajdź credentials w dashboardzie:
Po zalogowaniu znajdziesz:
- **Username**: np. `user-12345678-country-PL`
- **Password**: np. `abcd1234efgh`
- **Endpoint**: `gate.smartproxy.com:7000`

---

## 🔧 KONFIGURACJA W BOCIE

### Ustaw zmienne środowiskowe:
```bash
export SMARTPROXY_USERNAME="user-12345678-country-PL"
export SMARTPROXY_PASSWORD="abcd1234efgh"
```

### Lub dodaj na stałe do profilu:
```bash
echo 'export SMARTPROXY_USERNAME="user-12345678-country-PL"' >> ~/.bashrc
echo 'export SMARTPROXY_PASSWORD="abcd1234efgh"' >> ~/.bashrc
source ~/.bashrc
```

---

## 🧪 TEST PROXY

```bash
# Test podstawowy
python3 -c "
from smartproxy_integration import setup_smartproxy
import os
username = os.getenv('SMARTPROXY_USERNAME')
password = os.getenv('SMARTPROXY_PASSWORD')
if setup_smartproxy(username, password):
    print('✅ SmartProxy działa!')
else:
    print('❌ Błąd konfiguracji')
"
```

---

## 🚀 URUCHOMIENIE BOTA

```bash
# Po udanej konfiguracji:
python3 poly_market_maker/app.py \
  --strategy=bands \
  --strategy-config=config/bands.json \
  --condition-id=0x178dee952f29fb0a77f63df1d59514d15009caeb7c011a5c086aad80e6369f8d
```

**Oczekiwane rezultaty**:
- ✅ SmartProxy residential proxy activated - 3-day FREE trial!
- ✅ GET requests: 200 OK
- ✅ POST requests: 401/400 (nie 403!)
- ✅ Bot generuje i wysyła zlecenia

---

## 📊 Limity darmowego triala:

- **Czas**: 3 dni
- **Transfer**: 100MB
- **Bot usage**: ~10MB/h = **10 godzin darmowego działania**
- **Concurrent sessions**: Unlimited
- **Countries**: Wszystkie 195+ krajów

---

## 💰 Po trialu (opcjonalnie):

- **2GB**: $6/miesiąc
- **8GB**: $22/miesiąc  
- **25GB**: $65/miesiąc

**Trading bot używa ~10MB/h** więc 2GB starczy na **200 godzin** = cały miesiąc!

---

## 🔍 Troubleshooting

### Problem: Nie widzę credentials
**Rozwiązanie**: W dashboardzie idź do **Proxy setup** → **Authentication** 

### Problem: 403 nadal występuje
**Rozwiązanie**: 
1. Sprawdź czy używasz poprawnego username/password
2. Zmień region w dashboardzie na USA
3. Włącz sticky sessions

### Problem: Proxy timeout
**Rozwiązanie**:
1. Spróbuj endpoint: `us.smartproxy.com:10000`
2. Sprawdź firewall/VPN
3. Napisz do 24/7 chat support

---

## 🎯 Następne kroki:

1. **Zarejestruj się** → 3 min
2. **Ustaw credentials** → 1 min
3. **Test proxy** → 1 min
4. **Uruchom bota** → działa!

**Po 3 dniach** możesz przejść na **Oxylabs** (7-dniowy trial) lub wykupić SmartProxy.

**Total**: Masz **10 dni darmowych proxies** (3 + 7) do testów! 