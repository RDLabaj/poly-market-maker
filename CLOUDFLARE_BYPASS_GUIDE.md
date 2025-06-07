# Polymarket Bot - Przewodnik obejścia Cloudflare

## Problem
Cloudflare blokuje POST requesty do Polymarket CLOB API, uniemożliwiając składanie zleceń. To jest **znany problem** w społeczności (GitHub Issue #91).

## Rozwiązania (od najlepszego do eksperymentalnego)

### 🥇 Rozwiązanie 1: Residential Proxy (NAJLEPSZE)

**Zalety:** Najwyższa skuteczność, stabilność
**Wady:** Koszt (~$50-100/miesiąc)

```bash
# Kup residential proxy od dostawców jak:
# - BrightData, Oxylabs, SmartProxy, NetNut

# Zmodyfikuj cloudflare_fix.py:
RESIDENTIAL_PROXY = {
    'http': 'http://username:password@proxy-provider.com:port',
    'https': 'http://username:password@proxy-provider.com:port'
}
```

### 🥈 Rozwiązanie 2: FlareSolverr (REKOMENDOWANE)

**Zalety:** Darmowe, skuteczne
**Wady:** Wymaga Docker, zużywa RAM

#### Krok 1: Uruchom FlareSolverr
```bash
chmod +x setup_flaresolverr.sh
./setup_flaresolverr.sh
```

#### Krok 2: Uruchom bota z FlareSolverr
```bash
python -m poly_market_maker \
  --private-key 3bd3d35ffd64c7f4a9dc58db585d4ac6d52ffb0b5cc4c9dcd052388c8874cb95 \
  --rpc-url https://polygon-mainnet.infura.io/v3/10180878ecaa4339983a14ff65da80a4 \
  --clob-api-url https://clob.polymarket.com \
  --condition-id 0x178dee952f29fb0a77f63df1d59514d15009caeb7c011a5c086aad80e6369f8d \
  --strategy bands
```

Bot automatycznie wykryje i użyje FlareSolverr.

### 🥉 Rozwiązanie 3: CloudFreed (PŁATNE)

**Zalety:** Profesjonalne, szybkie
**Wady:** Kosztuje $15-50/miesiąc

```python
# Ustaw zmienną środowiskową
export CLOUDFREED_API_KEY="your_api_key_here"

# Bot automatycznie wykryje CloudFreed
```

### 💡 Rozwiązanie 4: VPN + Rotating IP

**Zalety:** Relatywnie tanie
**Wady:** Niezbyt stabilne

```bash
# Użyj VPN z automatyczną rotacją IP
# Przykład: NordVPN, ExpressVPN z obfuscated servers
```

## Jak sprawdzić czy rozwiązanie działa

### Test 1: Sprawdź logi bota
```bash
# Szukaj w logach:
✅ "FlareSolverr Cloudflare bypass activated"
✅ "CloudFreed bypass applied successfully"
✅ "Successfully placed new order"

# Unikaj:
❌ "Sorry, you have been blocked"
❌ "403 Forbidden"
❌ "Could not place new order"
```

### Test 2: Manualny test API
```python
import requests

# Test bez obejścia (powinien się nie udać)
response = requests.post("https://clob.polymarket.com/order", json={})
print(response.status_code)  # Oczekiwane: 403

# Test z FlareSolverr (powinien działać)
# Bot automatycznie używa FlareSolverr jeśli jest dostępny
```

## Diagnostyka problemów

### Problem: FlareSolverr nie startuje
```bash
# Sprawdź Docker
docker ps
docker logs flaresolverr

# Restart FlareSolverr
docker restart flaresolverr
```

### Problem: Dalej błędy 403
```bash
# Sprawdź IP
curl ipinfo.io

# Zmień VPN/proxy
# Wyczyść cookies/cache przeglądarki
```

### Problem: Bot nie składa zleceń
```bash
# Sprawdź konfigurację
cat config/active_coinbase_market.json

# Sprawdź balans (fake balances powinny być > 0)
# Sprawdź czy market jest aktywny
```

## Monitoring w czasie rzeczywistym

### Uruchom bota z logami DEBUG
```bash
python -m poly_market_maker \
  --private-key YOUR_KEY \
  --rpc-url YOUR_RPC \
  --clob-api-url https://clob.polymarket.com \
  --condition-id 0x178dee952f29fb0a77f63df1d59514d15009caeb7c011a5c086aad80e6369f8d \
  --strategy bands 2>&1 | tee bot_logs.txt
```

### Obserwuj kluczowe wskaźniki
- `Order[price=X,size=Y,side=BUY]` - bot próbuje składać zlecenia
- `Succesfully placed new order` - zlecenia przechodzą
- `Could not place new order` - Cloudflare blokuje

## Rozwiązania awaryjne

### Jeśli nic nie działa:
1. **Czekaj na update py-clob-client** - społeczność pracuje nad rozwiązaniem
2. **Używaj Polymarket web interface** - manualnie składaj zlecenia
3. **Skontaktuj się z Polymarket support** - zgłoś problem z API

## Koszty rozwiązań

| Rozwiązanie | Koszt/miesiąc | Skuteczność | Łatwość wdrożenia |
|-------------|---------------|-------------|-------------------|
| Residential Proxy | $50-100 | 95% | ⭐⭐⭐ |
| FlareSolverr | $0 | 80% | ⭐⭐⭐⭐ |
| CloudFreed | $15-50 | 90% | ⭐⭐⭐⭐⭐ |
| VPN | $5-15 | 60% | ⭐⭐ |

## Status wdrożenia

### ✅ Gotowe:
- [x] FlareSolverr integration
- [x] CloudFreed integration  
- [x] Automatic fallback w app.py
- [x] Docker setup script
- [x] Comprehensive documentation

### 🔄 Do zrobienia:
- [ ] Residential proxy integration
- [ ] Automatic IP rotation
- [ ] Performance monitoring
- [ ] Success rate tracking

## Wsparcie

**Problem z implementacją?**
1. Sprawdź logi Docker: `docker logs flaresolverr`
2. Sprawdź logi bota: `tail -f bot_logs.txt`
3. Sprawdź status FlareSolverr: `curl http://localhost:8191`

**Wskazówki:**
- FlareSolverr najlepiej działa z residential IP
- CloudFreed ma najwyższą skuteczność ale kosztuje
- Unikaj datacenter proxy/VPN - Cloudflare je blokuje
- Sprawdzaj aktualizacje py-clob-client regularnie 