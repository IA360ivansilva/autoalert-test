# 📱 SMS VIA COMPOSIO + DIALPAD

## ✅ Script Pronto

Arquivo: `send-sms-via-composio.py`

Funcionalidade:
- ✓ Envia SMS via Composio (integrado com seu Dialpad)
- ✓ Suporta envio individual
- ✓ Suporta batch via CSV
- ✓ Registra logs de envio
- ✓ Respeita Nao Ligar/opt-outs

---

## 🚀 Como Usar (3 passos)

### **Passo 1: Instalar Composio SDK**

```bash
pip install composio-core
```

### **Passo 2: Configurar Credenciais**

```bash
# Se você tem API key do Composio
export COMPOSIO_API_KEY="seu-api-key-aqui"

# Ou configure via Composio CLI
composio configure
```

### **Passo 3: Enviar SMS**

#### **Opção A: Teste com seu número (954-860-0537)**

```bash
python3 send-sms-via-composio.py \
  --phone "9548600537" \
  --message "Hi, test message from Ivan's Agent. askivan.co/edson-david-lower-payment.html"
```

#### **Opção B: Batch da CSV**

```bash
python3 send-sms-via-composio.py \
  --csv /path/to/AUTOALERT_2907_CLIENTES.csv \
  --limit 10
```

#### **Opção C: Test mode (não envia de verdade)**

```bash
python3 send-sms-via-composio.py \
  --phone "9548600537" \
  --message "Test message" \
  --test
```

---

## 📋 Que Dados o Script Usa?

**De CSV (para batch):**
- Nome (Primeiro Nome)
- Cell ou Telefone Principal
- Nao Ligar (respeita opt-outs)
- Carro Atual
- Customer ID

**Automaticamente:**
- Gera mensagem personalizada
- Cria link pra landing page
- Salva log de envio em JSON

---

## 📊 Output

Depois de enviar, você verá:

```
✅ Sent: 10
⊘ Skipped: 2
❌ Failed: 0

📝 Log saved: sms-log-20260909_143022.json
```

Log registra:
- Horário do envio
- Número do telefone
- Preview da mensagem
- Status (sent/failed)
- Resposta/erro

---

## 🔄 Workflow Final

```
1. Você instala Composio: pip install composio-core
2. Você configura credenciais: export COMPOSIO_API_KEY=...
3. Primeiro teste: enviar pra seu número (954-860-0537)
4. Quando confirmar que funciona: batch de 10-50 leads
5. Depois: escalar pra 100+ leads
```

---

## ✅ Status Agora

- ✓ Script criado e commitado
- ✓ Integrado com Composio + Dialpad
- ✓ Pronto pra usar quando instalar SDK
- ✓ Log e tracking inclusos

---

## 📝 Próximo Passo

1. **Instalar:** `pip install composio-core`
2. **Configurar:** `export COMPOSIO_API_KEY=...` (seu-key-aqui)
3. **Testar:** `python3 send-sms-via-composio.py --phone 9548600537 --message "Test"`
4. **Confirmar:** Você deve receber SMS no seu número

**Quando você conseguir instalar e configurar, me avisa que rodamos o teste together.**

---
