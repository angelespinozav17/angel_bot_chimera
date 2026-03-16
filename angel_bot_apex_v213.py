# ================================================================================
# PROJECT: 🔥 ANGEL BOT APEX CHIMERA v213 🐺 (TRADING 1H + RADAR MKT 15m CONSTANTE)
# ESTADO: BINANCE FUTURES (SOLUSDT) + MEAN REVERSION + MARKETING AUTOMÁTICO
# ================================================================================

import sys
import time
import os
import asyncio
import logging
import threading
import requests
import pandas as pd
from datetime import datetime
from binance.client import Client
from flask import Flask, redirect
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.error import TimedOut, NetworkError

if sys.stdout.encoding.lower() != 'utf-8':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError: pass

# ==============================================================================
# [1] CREDENCIALES Y AJUSTES TÁCTICOS (🔒 SANITIZADO PARA GITHUB)
# ==============================================================================
API_KEY = "TU_API_KEY_AQUI"
API_SECRET = "TU_API_SECRET_AQUI"

TOKEN_TELEGRAM = "TU_TOKEN_DE_TELEGRAM_AQUI"
CHAT_ID = "TU_CHAT_ID_PRIVADO_AQUI" 

# 📣 CANALES DE MARKETING (Embudo)
CANAL_VIP = "ID_CANAL_VIP_AQUI"
CANAL_FREE = "ID_CANAL_FREE_AQUI"
FIVERR_LINK = "https://www.fiverr.com/s/xXBEPmQ"

# 🎯 AJUSTES TÁCTICOS SOLANA (TRADING REAL 1H)
SYMBOL = "SOLUSDT"                 
APALANCAMIENTO = 10                
INVERSION_USD = 4.00               # 💵 Tu capital real
TAKE_PROFIT_PORC = 45.0            # 🎯 TP Apalancado
STOP_LOSS_PORC = 15.0              # 🛡️ SL Apalancado

if not os.path.exists('logs'): os.makedirs('logs')
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', 
                    handlers=[logging.FileHandler("logs/angel_bot_v213.log", encoding='utf-8'), logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("ApexQuant")

# ==============================================================================
# [2] SERVIDOR WEB FLASK
# ==============================================================================
app_web = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="2">
    <title>🔥 APEX v213 - SOL DUAL CORE</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Inter:wght@400;600;800&display=swap');
        :root { --bg: #050505; --card: #111111; --border: #333333; --text-main: #f4f4f5; --text-sec: #a1a1aa; --green: #10b981; --red: #ef4444; --gold: #eab308; --fire: #f97316; --cyan: #06b6d4; }
        body { background: var(--bg); color: var(--text-main); font-family: 'Inter', sans-serif; display: flex; flex-direction: column; align-items: center; padding: 20px; margin: 0; }
        .container { width: 100%; max-width: 950px; background: var(--card); border-radius: 12px; padding: 25px; border: 1px solid var(--border); box-shadow: 0 10px 50px rgba(16, 185, 129, 0.05); }
        h2 { text-align: center; margin: 0 0 5px 0; font-weight: 900; font-size: 28px; background: linear-gradient(90deg, #10b981, #06b6d4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: 1.5px; text-transform: uppercase; }
        .sub-header { text-align: center; font-size: 11px; color: var(--text-sec); margin-bottom: 20px; font-weight: 600; text-transform: uppercase; letter-spacing: 2px; border-bottom: 1px solid var(--border); padding-bottom: 10px;}
        .status-box { background: rgba(0,0,0,0.5); border-left: 4px solid _ESTADO_COLOR_; padding: 15px; margin-bottom: 20px; border-radius: 6px; font-family: 'Share Tech Mono', monospace; }
        .status-box .status-text { font-size: 16px; font-weight: bold; color: _ESTADO_COLOR_; margin-bottom: 5px; }
        .target-box { background: rgba(16, 185, 129, 0.05); border: 1px solid var(--green); padding: 12px; border-radius: 8px; margin-bottom: 15px; font-size: 14px; text-align: center; box-shadow: inset 0 0 10px rgba(16, 185, 129, 0.1); font-weight:bold; letter-spacing: 1px;}
        .radar-box { background: rgba(0,0,0,0.3); border: 1px solid _COLOR_POSICION_; padding: 15px; border-radius: 8px; margin-bottom: 20px; font-size: 14px; font-family: 'Share Tech Mono', monospace; }
        .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px; }
        .box { background: rgba(255,255,255,0.03); padding: 15px; border-radius: 10px; text-align: center; border: 1px solid var(--border); }
        .box label { display: block; font-size: 10px; color: var(--text-sec); text-transform: uppercase; margin-bottom: 5px; font-weight: 600; }
        .box span { font-size: 20px; font-weight: bold; font-family: 'Share Tech Mono', monospace; }
        .controls-box { display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.02); padding: 20px; border-radius: 8px; border: 1px solid var(--border); margin-bottom: 20px; }
        .btn { padding: 10px 18px; text-decoration: none; border-radius: 6px; font-size: 12px; font-weight: bold; border: 1px solid var(--border); cursor: pointer; display: inline-block; color: var(--text-main); transition: 0.2s; }
        .btn:hover { background: rgba(255,255,255,0.05); border-color: var(--cyan); }
        .table-wrapper { overflow-y: auto; width: 100%; border-radius: 8px; border: 1px solid var(--border); background: rgba(0,0,0,0.4); }
        table { width: 100%; border-collapse: collapse; font-size: 12px; text-align: center; }
        th { padding: 12px; background: rgba(20, 20, 25, 0.9); color: var(--text-sec); border-bottom: 1px solid var(--border); text-transform: uppercase; font-weight: 600; }
        td { padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.02); }
        tr:hover td { background: rgba(16, 185, 129, 0.05); }
    </style>
</head>
<body>
    <div class="container">
        <h2>🔥 APEX CHIMERA v213 🐺</h2>
        <div class="sub-header">TRADING: 1H | RADAR MKT: 15m CONSTANTE | TP: +_TP_% / SL: -_SL_% | UPTIME: ⏱️ _UPTIME_</div>
        <div class="status-box">
            <div class="status-text">[_ESTADO_BOT_]</div>
            <div style="color:var(--text-sec); font-size:12px; margin-top: 8px;">Actividad: <span style="color:var(--text-main);">_ACCION_ACTUAL_</span></div>
        </div>
        <div class="target-box">🎯 BINANCE FUTURES: SOL/USDT (PERPETUAL) 🎯</div>
        <div class="radar-box">
            <strong style="color:var(--text-sec); font-size:11px; display:block; margin-bottom:5px; text-transform:uppercase; font-family:'Inter', sans-serif;">Posición Activa:</strong>
            <span style="color:var(--text-main);">_MENSAJE_POSICION_</span>
        </div>
        <div class="grid">
            <div class="box"><label>Billetera (USDT)</label><span style="color:_COLOR_SALDO_">$_SALDO_USDT_</span></div>
            <div class="box"><label>Ganancia Neta</label><span style="color:_COLOR_PNL_">$_PNL_NETO_</span></div>
            <div class="box"><label>Victorias</label><span style="color:var(--green)">_LOGRADAS_</span> <span style="font-size:14px;color:var(--text-sec);">/</span> <span style="color:var(--red)">_FALLIDAS_</span></div>
            <div class="box"><label>Win Rate</label><span style="color:var(--gold)">_WIN_RATE_%</span></div>
        </div>
        <div class="grid">
            <div class="box"><label>Precio SOL</label><span>$_PRECIO_ASSET_</span></div>
            <div class="box"><label>Apalancamiento</label><span style="color:var(--cyan);">_APALANCAMIENTO_x</span></div>
            <div class="box"><label>Radar Oráculo 1H</label><span style="font-size:14px; color:var(--fire);">_METRICAS_ORACULO_</span></div>
            <div class="box"><label>Tamaño Pos.</label><span>_TAMAÑO_POS_</span></div>
        </div>
        <div class="controls-box">
            <div>_BTN_MOTOR_HTML_</div>
            <div><a href="/action/sync" class="btn">🔄 Sync Billetera</a></div>
        </div>
        <div class="table-wrapper">
            <table>
                <thead><tr><th>Hora</th><th>Dirección</th><th>Entrada ($)</th><th>Salida ($)</th><th>PnL Final</th><th>Motivo</th></tr></thead>
                <tbody>_FILAS_HISTORIAL_</tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

@app_web.route('/')
def index(): return core.current_html if hasattr(core, 'current_html') else "Cargando motor de guerra..."
@app_web.route('/action/<cmd>')
def web_action(cmd):
    if cmd == 'stop':
        core.auto_trading_activo = False
        core.estado_bot = "💤 MODO REPOSO"
        core.accion_actual = "🛑 Motor detenido manualmente."
        core.trigger_stop_notif = True 
    elif cmd == 'start':
        core.auto_trading_activo = True
        core.estado_bot = "🔥 VIGILANDO (Trading 1H | Radar 15m)"
        core.accion_actual = "🟢 Motor Apex encendido."
        core.trigger_start_notif = True
    elif cmd == 'sync':
        core._sync_saldo()
        core.accion_actual = "✅ Saldo Binance Sincronizado."
    return redirect('/')

def run_web_server():
    log = logging.getLogger('werkzeug'); log.setLevel(logging.ERROR)
    app_web.run(host="0.0.0.0", port=5000, use_reloader=False)

# ==============================================================================
# [3] CLASE MAESTRA: ANGEL FUTURES
# ==============================================================================
class AngelFuturesBot:
    def __init__(self):
        self.client = Client(API_KEY, API_SECRET)
        self.start_time = time.time()
        self.auto_trading_activo = False
        self.trigger_stop_notif = False 
        self.trigger_start_notif = False
        
        self.saldo_usdt = 0.0
        self.saldo_al_entrar = 0.0
        self.precio_actual_cache = 0.0
        self.precio_entrada = 0.0
        self.detalles_tecnicos_cache = "Calibrando radares..."
        
        self.posicion_activa = False
        self.dir_posicion = ""
        self.cantidad_asset_actual = 0.0
        
        self.cooldown_hasta = 0.0         
        self.cooldown_prediccion = 0.0     # Inicializa en 0 para disparar de inmediato al encender
        
        self.estado_bot = "⚙️ INICIANDO..."
        self.mensaje_posicion = "Esperando operaciones..." 
        self.accion_actual = "Revisando historial y posiciones..."
        
        self.csv_path = 'historial_v213_sol.csv'
        self.total_operaciones = 0; self.logradas = 0; self.fallidas = 0
        self.session_ganada = 0.0; self.session_perdida = 0.0
        
        self._cargar_historial()
        self._configurar_futuros()
        self._sync_saldo()
        self._recuperar_posicion_activa() 
        self.actualizar_html()

    def _cargar_historial(self):
        if os.path.exists(self.csv_path):
            try:
                df = pd.read_csv(self.csv_path)
                self.logradas = len(df[df['PnL'] > 0])
                self.fallidas = len(df[df['PnL'] <= 0])
                self.total_operaciones = self.logradas + self.fallidas
                self.session_ganada = df[df['PnL'] > 0]['PnL'].sum()
                self.session_perdida = abs(df[df['PnL'] < 0]['PnL'].sum())
            except: pass

    def _configurar_futuros(self):
        try:
            try: self.client.futures_change_margin_type(symbol=SYMBOL, marginType='ISOLATED')
            except: pass
            self.client.futures_change_leverage(symbol=SYMBOL, leverage=APALANCAMIENTO)
        except Exception as e: logger.error(f"Apalancamiento: {e}")

    def _sync_saldo(self):
        try:
            for b in self.client.futures_account_balance():
                if b['asset'] == 'USDT':
                    self.saldo_usdt = float(b['balance']); break
        except: pass

    def _recuperar_posicion_activa(self):
        try:
            posiciones = self.client.futures_position_information(symbol=SYMBOL)
            for pos in posiciones:
                amt = float(pos['positionAmt'])
                if amt != 0.0:
                    self.posicion_activa = True
                    self.dir_posicion = "LONG" if amt > 0 else "SHORT"
                    self.cantidad_asset_actual = abs(amt)
                    self.precio_entrada = float(pos['entryPrice'])
                    pnl_flotante = float(pos['unRealizedProfit'])
                    self.saldo_al_entrar = self.saldo_usdt - pnl_flotante
                    
                    self.auto_trading_activo = True
                    self.estado_bot = "🛡️ POSICIÓN RECUPERADA"
                    self.mensaje_posicion = f"ADOPTADA: {self.dir_posicion} | Entrada: ${self.precio_entrada:.2f} | PnL Flotante: {pnl_flotante:+.2f}"
                    self.accion_actual = "Monitoreando operación existente..."
                    break
        except Exception as e: logger.error(f"Error recuperando: {e}")

    # 🔮 ORÁCULO DE MARKETING (RADAR 15 MINUTOS CONSTANTE)
    def obtener_analisis_predictor_15m(self):
        try:
            k = self.client.futures_klines(symbol=SYMBOL, interval=Client.KLINE_INTERVAL_15MINUTE, limit=30)
            c = [float(x[4]) for x in k]
            df = pd.DataFrame(c, columns=['close'])
            ema_9 = df['close'].ewm(span=9, adjust=False).mean().iloc[-1]
            
            # Ahora NO pide extremos de RSI. Siempre evalúa la tendencia actual para reportarla.
            precio_actual = c[-1]
            tendencia = "LONG (Bullish)" if precio_actual > ema_9 else "SHORT (Bearish)"
            
            return tendencia, precio_actual
        except: return "WAITING", 0.0

    # 📣 EMBUDO DE VENTAS CONSTANTE (Cada 15 min exactos)
    def broadcast_prediccion_15m(self, senal, precio_actual):
        moneda = "SOL/USDT"
        
        # Para el VIP, calculamos los porcentajes específicos de un trade scalper (Ej: 1.5% TP)
        tp = precio_actual * 1.015 if "LONG" in senal else precio_actual * 0.985
        sl = precio_actual * 0.990 if "LONG" in senal else precio_actual * 1.010

        msg_vip = (
            f"👑 *APEX VIP SCALP RADAR (15m)* 👑\n\n"
            f"🎯 Asset: {moneda}\n"
            f"⚡ Trend Detected: *{senal}*\n"
            f"💰 Entry Point: ${precio_actual:.2f}\n"
            f"✅ Take Profit: ${tp:.2f}\n"
            f"🛑 Stop Loss: ${sl:.2f}\n\n"
            f"🐺 _Waiting for extreme volatility confirmation to execute._"
        )
        msg_free = (
            f"🚨 *15m MARKET RADAR UPDATE* 🚨\n\n"
            f"Asset: {moneda}\n"
            f"📈 Current Algorithm Trend: *{senal}*\n\n"
            f"🔒 _Exact Entry, TP & SL points are calculated and sent to VIP members._\n\n"
            f"🐺 Want full access or your own 24/7 Bot? Get it here:\n"
            f"👉 {FIVERR_LINK}"
        )
        
        url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
        try:
            requests.post(url, json={"chat_id": CANAL_VIP, "text": msg_vip, "parse_mode": "Markdown"})
            requests.post(url, json={"chat_id": CANAL_FREE, "text": msg_free, "parse_mode": "Markdown"})
            logger.info(f"📣 Reporte de Radar 15m ({senal}) enviado al embudo.")
        except Exception as e:
            logger.error(f"🚨 Error en Marketing Broadcast: {e}")


    # 🎯 ORÁCULO DE TRADING REAL (1 HORA - MODO FRANCOTIRADOR SEGURO)
    def obtener_analisis_trading_1h(self):
        try:
            k = self.client.futures_klines(symbol=SYMBOL, interval=Client.KLINE_INTERVAL_1HOUR, limit=30)
            c = [float(x[4]) for x in k]
            df = pd.DataFrame(c, columns=['close'])
            ema_9 = df['close'].ewm(span=9, adjust=False).mean().iloc[-1]
            tendencia = "ARRIBA" if c[-1] > ema_9 else "ABAJO"

            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            rsi_actual = rsi.iloc[-1]
            
            self.precio_actual_cache = c[-1]
            self.detalles_tecnicos_cache = f"1h: {tendencia} | RSI: {rsi_actual:.1f}"

            if tendencia == "ARRIBA" and rsi_actual < 35: return "LONG"
            elif tendencia == "ABAJO" and rsi_actual > 65: return "SHORT"
            return "ESPERAR"
        except: return "ESPERAR"

    def _revisar_posiciones_abiertas(self):
        try:
            for pos in self.client.futures_position_information(symbol=SYMBOL):
                if float(pos['positionAmt']) != 0.0: return True 
            return False 
        except: return True

    def ejecutar_orden_compra(self, direccion):
        try:
            self._sync_saldo()
            self.saldo_al_entrar = self.saldo_usdt
            self.precio_entrada = self.precio_actual_cache
            self.dir_posicion = direccion
            
            side = 'BUY' if direccion == "LONG" else 'SELL'
            side_inverso = 'SELL' if direccion == "LONG" else 'BUY'
            tamaño_posicion_usd = INVERSION_USD * APALANCAMIENTO
            
            self.cantidad_asset_actual = round(tamaño_posicion_usd / self.precio_actual_cache, 2)
            if self.cantidad_asset_actual <= 0.01: return False, "Inversión muy baja para SOL."

            mov_tp = (TAKE_PROFIT_PORC / APALANCAMIENTO) / 100.0
            mov_sl = (STOP_LOSS_PORC / APALANCAMIENTO) / 100.0
            p_tp = round(self.precio_actual_cache * (1 + mov_tp), 3) if direccion == "LONG" else round(self.precio_actual_cache * (1 - mov_tp), 3)
            p_sl = round(self.precio_actual_cache * (1 - mov_sl), 3) if direccion == "LONG" else round(self.precio_actual_cache * (1 + mov_sl), 3)

            # Disparo Market a Binance
            self.client.futures_create_order(symbol=SYMBOL, side=side, type='MARKET', quantity=self.cantidad_asset_actual)
            self.client.futures_create_order(symbol=SYMBOL, side=side_inverso, type='TAKE_PROFIT_MARKET', stopPrice=p_tp, closePosition=True, timeInForce='GTC')
            self.client.futures_create_order(symbol=SYMBOL, side=side_inverso, type='STOP_MARKET', stopPrice=p_sl, closePosition=True, timeInForce='GTC')

            self.posicion_activa = True
            self.estado_bot = "🛡️ POSICIÓN BLINDADA (1H)"
            self.mensaje_posicion = f"ACTIVO: {direccion} | Entrada: ${self.precio_entrada:.2f} | TP: ${p_tp:.2f}"
            self.accion_actual = "Operación montada. Francotirador en posición."
            
            msg_tg = (
                f"🚀 **ORDEN REAL FRANCOTIRADOR (1H)** 🚀\n"
                f"📈 Dirección: `{direccion}`\n"
                f"💵 Entrada: `${self.precio_entrada:.2f}`\n"
                f"🎯 Take Profit: `${p_tp:.2f}` (+45%)\n"
                f"🛡️ Stop Loss: `${p_sl:.2f}` (-15%)\n"
                f"💲 Inversión Real: `{INVERSION_USD} USDT`\n"
                f"⚡ Apalancamiento: `{APALANCAMIENTO}x`"
            )
            return True, msg_tg
        except Exception as e:
            self.posicion_activa = False
            return False, f"Error: {e}"

    def procesar_cierre(self):
        self._sync_saldo()
        ganancia_real = self.saldo_usdt - self.saldo_al_entrar
        
        if ganancia_real > 0:
            self.logradas += 1; self.session_ganada += ganancia_real; motivo = "🎯 Take Profit (+45%)"
        else:
            self.fallidas += 1; self.session_perdida += abs(ganancia_real); motivo = "🛡️ Stop Loss (-15%)"
            
        self.total_operaciones += 1
        df_new = pd.DataFrame([{"Fecha_Hora": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "Senal": self.dir_posicion, "Op_Compra": round(self.precio_entrada, 2), "Op_Venta": round(self.precio_actual_cache, 2), "PnL": round(ganancia_real, 2), "Motivo": motivo}])
        df_new.to_csv(self.csv_path, mode='a', header=not os.path.exists(self.csv_path), index=False)
        
        self.posicion_activa = False
        self.cantidad_asset_actual = 0.0
        self.cooldown_hasta = time.time() + 300 # Descansa 5 minutos tras operar (1H)
        self.estado_bot = "💤 RECARGANDO"
        self.mensaje_posicion = "Esperando operaciones..."
        self.accion_actual = f"Operación cerrada. PnL: {ganancia_real:+.2f} USDT"
        return ganancia_real, motivo

    def actualizar_html(self):
        wr = (self.logradas / self.total_operaciones * 100) if self.total_operaciones > 0 else 0.0
        pnl_neto = self.session_ganada - self.session_perdida
        
        estado_color = "var(--green)" if self.auto_trading_activo else "var(--text-sec)"
        if self.posicion_activa: estado_color = "var(--gold)"
            
        color_posicion = "var(--cyan)" if self.posicion_activa else "var(--text-sec)"
        if "LONG" in self.mensaje_posicion: color_posicion = "var(--green)"
        if "SHORT" in self.mensaje_posicion: color_posicion = "var(--red)"
            
        if self.auto_trading_activo:
            btn_motor_html = '<a href="/action/stop" class="btn" style="background:rgba(239,68,68,0.15); border: 2px solid var(--red); color:var(--red); font-size:14px; font-weight:800; padding: 12px 20px;">[🛑] APAGAR SNIPER</a>'
        else:
            btn_motor_html = '<a href="/action/start" class="btn" style="background:rgba(16,185,129,0.15); border: 2px solid var(--green); color:var(--green); font-size:14px; font-weight:800; padding: 12px 20px;">[🔥] ENCENDER SNIPER</a>'

        filas_historial = ""
        if os.path.exists(self.csv_path):
            try:
                for _, r in pd.read_csv(self.csv_path).tail(12).iloc[::-1].iterrows():
                    c_pnl = "var(--green)" if float(r['PnL']) >= 0 else "var(--red)"
                    dir_icono = "▲" if "LONG" in r['Senal'] else "▼"
                    filas_historial += f"<tr><td>{str(r['Fecha_Hora'])[11:16]}</td><td style='color:{'var(--green)' if dir_icono=='▲' else 'var(--red)'}; font-weight:bold;'>{r['Senal']} {dir_icono}</td><td>${float(r['Op_Compra']):.2f}</td><td>${float(r['Op_Venta']):.2f}</td><td><span style='color:{c_pnl}; font-weight:bold;'>${float(r['PnL']):+.2f}</span></td><td>{r['Motivo']}</td></tr>"
            except: pass
        if not filas_historial: filas_historial = "<tr><td colspan='6' style='padding:20px; color:var(--text-sec);'>[ AÚN NO HAY VÍCTIMAS ]</td></tr>"

        acciones_disp = f"{self.cantidad_asset_actual} SOL" if self.posicion_activa else "0 SOL"
        uptime_sec = int(time.time() - self.start_time); hrs, rem_sec = divmod(uptime_sec, 3600); mins, _ = divmod(rem_sec, 60)
        
        html = HTML_TEMPLATE.replace("_ESTADO_COLOR_", estado_color)
        html = html.replace("_COLOR_POSICION_", color_posicion)
        html = html.replace("_TP_", str(TAKE_PROFIT_PORC))
        html = html.replace("_SL_", str(STOP_LOSS_PORC))
        html = html.replace("_UPTIME_", f"{hrs}h {mins}m")
        html = html.replace("_ESTADO_BOT_", self.estado_bot)
        html = html.replace("_ACCION_ACTUAL_", self.accion_actual)
        html = html.replace("_MENSAJE_POSICION_", self.mensaje_posicion)
        html = html.replace("_SALDO_USDT_", f"{self.saldo_usdt:,.2f}")
        html = html.replace("_COLOR_SALDO_", "var(--green)" if self.saldo_usdt >= 1.0 else "var(--red)")
        html = html.replace("_PNL_NETO_", f"{pnl_neto:+.2f}")
        html = html.replace("_COLOR_PNL_", "var(--green)" if pnl_neto >= 0 else "var(--red)")
        html = html.replace("_LOGRADAS_", str(self.logradas))
        html = html.replace("_FALLIDAS_", str(self.fallidas))
        html = html.replace("_WIN_RATE_", f"{wr:.1f}")
        html = html.replace("_PRECIO_ASSET_", f"${self.precio_actual_cache:.2f}")
        html = html.replace("_APALANCAMIENTO_", str(APALANCAMIENTO))
        html = html.replace("_METRICAS_ORACULO_", self.detalles_tecnicos_cache)
        html = html.replace("_TAMAÑO_POS_", acciones_disp)
        html = html.replace("_BTN_MOTOR_HTML_", btn_motor_html)
        html = html.replace("_FILAS_HISTORIAL_", filas_historial)
        self.current_html = html

# ==============================================================================
# [4] MOTOR PRINCIPAL Y CONTROLADORES TELEGRAM
# ==============================================================================
core = AngelFuturesBot()

def get_keyboard():
    txt_motor = "🔴 APAGAR SNIPER" if core.auto_trading_activo else "🔥 ENCENDER SNIPER"
    cb_motor = "off" if core.auto_trading_activo else "on"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(txt_motor, callback_data=cb_motor)],
        [InlineKeyboardButton("📡 Estatus", callback_data='estatus'), InlineKeyboardButton("🔄 Sync Saldo", callback_data='sync_saldo')],
        [InlineKeyboardButton("📊 Stats Sesión", callback_data='stats_sesion')]
    ])

async def cmd_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        estado = 'ACTIVO 🔥' if core.auto_trading_activo else 'REPOSO 💤'
        pnl_neto = core.session_ganada - core.session_perdida
        msj = f"🤖 **APEX CHIMERA v213.0 (DUAL CORE)**\nEstado: `{estado}`\nBilletera: `{core.saldo_usdt:.2f} USDT`\n\n📊 **Sesión Actual:**\n⚖️ Neto: `${pnl_neto:+.2f}`"
        await update.message.reply_text(msj, reply_markup=get_keyboard(), parse_mode='Markdown')
    except: pass

async def btn_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        q = update.callback_query; await q.answer()
        if q.data == 'on':
            core.auto_trading_activo = True
            core.estado_bot = "🔥 VIGILANDO (Trading 1H | Radar 15m)"
            try: await q.edit_message_reply_markup(reply_markup=get_keyboard())
            except: pass
        elif q.data == 'off':
            core.auto_trading_activo = False
            if not core.posicion_activa: core.estado_bot = "💤 MODO REPOSO"
            try: await q.edit_message_reply_markup(reply_markup=get_keyboard())
            except: pass
        elif q.data == 'estatus':
            pos = core.mensaje_posicion if core.posicion_activa else "Ninguna"
            await q.message.reply_text(f"📡 Estatus: `{core.estado_bot}`\n🎯 Oráculo 1H: `{core.detalles_tecnicos_cache}`\n🛡️ Posición: `{pos}`", parse_mode='Markdown')
        elif q.data == 'sync_saldo':
            core._sync_saldo()
            await q.message.reply_text(f"✅ **Saldo Sincronizado:** `{core.saldo_usdt:.2f} USDT`", parse_mode='Markdown')
        elif q.data == 'stats_sesion':
            pnl_neto = core.session_ganada - core.session_perdida
            msj = f"📊 **ESTADÍSTICAS DE GUERRA**\n✅ Victorias: `{core.logradas}`\n❌ Derrotas: `{core.fallidas}`\n⚖️ **PnL NETO: `${pnl_neto:+.2f}`**"
            await q.message.reply_text(msj, parse_mode='Markdown')
    except: pass

async def motor_maestro(app: Application):
    bot_tg = app.bot
    try:
        await bot_tg.set_my_commands([BotCommand("panel", "Abrir Panel de Control")])
        msj_inicio = f"🔥 **APEX CHIMERA v213 INICIADO** 🦅\n\nModo: `DUAL CORE (Trading 1H / Radar Constante 15m)`\nRisk/Reward: `+{TAKE_PROFIT_PORC}% / -{STOP_LOSS_PORC}%`\nSaldo: `{core.saldo_usdt:.2f} USDT`\n\n_Escribe /panel para ver controles._"
        await bot_tg.send_message(chat_id=CHAT_ID, text=msj_inicio, reply_markup=get_keyboard(), parse_mode='Markdown')
    except: pass
    
    while True:
        try:
            if core.trigger_stop_notif:
                pnl_neto = core.session_ganada - core.session_perdida
                msj = f"🤖 **PANEL v213**\nEstado: `REPOSO 💤`\nSaldo: `{core.saldo_usdt:.2f} USDT`\n⚖️ Neto: `${pnl_neto:+.2f}`"
                try: await bot_tg.send_message(chat_id=CHAT_ID, text=msj, reply_markup=get_keyboard(), parse_mode='Markdown')
                except: pass
                core.trigger_stop_notif = False
                
            if core.trigger_start_notif:
                pnl_neto = core.session_ganada - core.session_perdida
                msj = f"🤖 **PANEL v213**\nEstado: `ACTIVO 🔥`\nSaldo: `{core.saldo_usdt:.2f} USDT`\n⚖️ Neto: `${pnl_neto:+.2f}`"
                try: await bot_tg.send_message(chat_id=CHAT_ID, text=msj, reply_markup=get_keyboard(), parse_mode='Markdown')
                except: pass
                core.trigger_start_notif = False

            # ==========================================
            # EL CORAZÓN DE LA BESTIA
            # ==========================================
            if core.auto_trading_activo:
                
                # 📢 TAREA 1: RADAR DE 15 MINUTOS CONSTANTE (MARKETING)
                if time.time() > core.cooldown_prediccion:
                    senal_15m, precio_15m = core.obtener_analisis_predictor_15m()
                    if senal_15m != "WAITING":
                        # Lanza el mensaje al canal en segundo plano
                        threading.Thread(target=core.broadcast_prediccion_15m, args=(senal_15m, precio_15m)).start()
                        # Silencio por 15 minutos exactos (900 segundos)
                        core.cooldown_prediccion = time.time() + 900 
                
                # 🎯 TAREA 2: TRADING REAL 1H (BINANCE)
                if not core.posicion_activa:
                    if time.time() > core.cooldown_hasta:
                        core.estado_bot = "🔥 VIGILANDO (Trading 1H | Radar 15m)"
                        senal_1h = core.obtener_analisis_trading_1h()
                        
                        if senal_1h in ["LONG", "SHORT"]:
                            core.accion_actual = f"⚡ Señal 1H {senal_1h} detectada. Disparando bala real..."
                            exito, msg = core.ejecutar_orden_compra(senal_1h)
                            if exito:
                                try: await bot_tg.send_message(CHAT_ID, msg, parse_mode='Markdown')
                                except: pass
                            else:
                                core.cooldown_hasta = time.time() + 60 
                    else:
                        restan = int(core.cooldown_hasta - time.time())
                        core.estado_bot = f"ENFRIANDO 1H ({restan}s)"
                        
                elif core.posicion_activa:
                    sigue_adentro = core._revisar_posiciones_abiertas()
                    if not sigue_adentro:
                        pnl_trade, motivo_trade = core.procesar_cierre()
                        if pnl_trade > 0:
                            icono = "🟢 ✅ ¡FRANCOTIRADOR ACERTÓ!"
                            color_dinero = f"+${pnl_trade:.2f} USDT"
                        else:
                            icono = "🔴 ❌ ESCUDO ACTIVADO"
                            color_dinero = f"-${abs(pnl_trade):.2f} USDT"
                            
                        msj_cierre = f"{icono}\n\n💸 PnL: `{color_dinero}`\nℹ️ Razón: `{motivo_trade}`\n💰 Nuevo Saldo: `{core.saldo_usdt:.2f} USDT`"
                        try: await bot_tg.send_message(CHAT_ID, msj_cierre, parse_mode='Markdown')
                        except: pass

            core.actualizar_html()
            await asyncio.sleep(5) 
            
        except Exception as e:
            logger.error(f"Error loop principal: {e}")
            await asyncio.sleep(10)

def start_bot():
    app = Application.builder().token(TOKEN_TELEGRAM).build()
    app.add_handler(CommandHandler("panel", cmd_panel))
    app.add_handler(CallbackQueryHandler(btn_handler))
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(motor_maestro(app))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    print("Iniciando 🔥 APEX CHIMERA v213 (DUAL CORE) 🐺...")
    while True:
        try: start_bot()
        except (TimedOut, NetworkError): time.sleep(10)
        except Exception as e: print(f"🚨 Error de Red: {e}"); time.sleep(15)
