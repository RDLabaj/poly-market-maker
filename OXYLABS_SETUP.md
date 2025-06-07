# Oxylabs Residential Proxy Setup - Instrukcja

## 🚀 Szybki start z Oxylabs (7-dniowy darmowy trial)

### 1. Rejestracja (2 minuty)

1. **Idź na**: https://oxylabs.io/products/residential-proxy-pool
2. **Kliknij**: "Start Free Trial" (7 dni gratis)
3. **Wypełnij**:
   - Email (użyj prawdziwego)
   - Silne hasło
   - Company: "Individual" lub dowolna nazwa
   - Use case: "Web scraping" lub "Data collection"
4. **Potwierdź email** z linku w skrzynce

### 2. Konfiguracja Dashboard

Po zalogowaniu:

1. **Dashboard** → **Residential Proxies**
2. **Create Endpoint** (jeśli nie ma domyślnego)
3. **Zapisz dane**:
   - **Username**: customer-[twój_customer_id]
   - **Password**: [wygenerowane_hasło]
   - **Endpoint**: residential.oxylabs.io:8001
   - **Sticky sessions**: Włącz (ważne dla Cloudflare)

### 3. Test połączenia

```bash
# Sprawdź czy działają podstawowe funkcje
curl -x residential.oxylabs.io:8001 -U "customer-XXXXXX:hasło" \
     http://httpbin.org/ip
```

### 4. Konfiguracja w bocie

```bash
# W terminalu ustaw zmienne środowiskowe:
export OXYLABS_USERNAME="customer-XXXXXX"
export OXYLABS_PASSWORD="twoje_hasło"

# Alternatywnie, dodaj do .bashrc/.zshrc:
echo 'export OXYLABS_USERNAME="customer-XXXXXX"' >> ~/.bashrc
echo 'export OXYLABS_PASSWORD="twoje_hasło"' >> ~/.bashrc
source ~/.bashrc
```

### 5. Test z Polymarket

```bash
# Uruchom test
python3 test_oxylabs.py
```

**Oczekiwany rezultat**:
- ✅ Proxy connection test - Success
- ✅ GET requests - 200 OK
- ✅ POST requests - 401/400 (nie 403!)

### 6. Uruchomienie bota

```bash
# Po udanym teście, uruchom bota:
python3 poly_market_maker/app.py \
  --strategy=bands \
  --strategy-config=config/bands.json \
  --condition-id=0x178dee952f29fb0a77f63df1d59514d15009caeb7c011a5c086aad80e6369f8d
```

## 🔧 Troubleshooting

### Problem: 403 Forbidden nadal występuje
**Rozwiązanie**:
1. Sprawdź czy używasz sticky sessions
2. Zmień endpoint region (US/EU):
   - US: `us-pr.oxylabs.io:10000`
   - EU: `pr.oxylabs.io:8001`
3. Dodaj custom headers w request

### Problem: Proxy connection timeout
**Rozwiązanie**:
1. Sprawdź firewall/network
2. Spróbuj różnych portów: 8001, 10000, 40000
3. Użyj HTTP zamiast HTTPS dla proxy connection

### Problem: Rate limiting
**Rozwiązanie**:
1. Włącz rotation w dashboard
2. Zwiększ delay między requestami
3. Użyj session persistence

## 💰 Pricing po trial

- **Starter**: $15/month (2GB)
- **Advanced**: $50/month (10GB) 
- **Professional**: $100/month (25GB)
- **Enterprise**: Custom pricing

**Trial obejmuje**: 7 dni lub 1GB ruchu (co nastąpi pierwsze)

## 🎯 Dlaczego Oxylabs dla Polymarket

1. **Najwyższa success rate**: 98.50% bypass Cloudflare
2. **Residential IPs**: Trudne do wykrycia przez Cloudflare
3. **Global locations**: USA, EU, Asia (ważne dla geo-blocking)
4. **24/7 Support**: Szybka pomoc przy problemach
5. **Sticky sessions**: IP nie zmienia się podczas sesji
6. **High-speed**: Optymalne dla trading botów

## 📊 Monitoring i optymalizacja

### Dashboard metryki:
- **Success rate**: >95% dla Polymarket
- **Response time**: <2s średnio
- **Data usage**: ~10MB/h dla trading bota

### Optymalne ustawienia:
- **Session duration**: 30 minut
- **Location**: USA (najlepiej dla Polymarket)
- **Rotation**: Co 15 minut
- **Retry**: 3 próby z 2s delay

## 🚨 Backup plan

Jeśli Oxylabs nie zadziała:
1. **SmartProxy** (3-day trial)
2. **BrightData** (7-day trial) 
3. **NetNut** (7-day trial)

Wszystkie mają darmowe trialy - możesz testować kolejno! 