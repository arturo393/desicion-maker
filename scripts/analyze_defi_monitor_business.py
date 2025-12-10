#!/usr/bin/env python3
"""
🔄 ANÁLISIS REAL DeFi Monitor con Gemini API + Algoritmos Decision Framework
"""

import os
import sys
import json
from datetime import datetime

try:
    import google.generativeai as genai
except ImportError:
    print("❌ Instalando google-generativeai...")
    os.system("pip install -q google-generativeai")
    import google.generativeai as genai


def analyze_defi_monitor_with_gemini():
    """Análisis completo con Gemini API"""
    
    # Configurar Gemini
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY no encontrado")
        print("   Usa: export GEMINI_API_KEY=your_key")
        sys.exit(1)
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash-exp")
    
    print("\n" + "="*80)
    print("🔄 ANÁLISIS REAL: DeFi Monitor Business Viability (9 DIC 2025)")
    print("   Framework: v4.5.0 + Gemini 2.0 Flash")
    print("="*80 + "\n")
    
    # ========================================================================
    # FASE 1: MARKET RESEARCH (Monitor Tiempo Real)
    # ========================================================================
    
    print("\n📊 FASE 1: Market Research con Gemini API\n")
    
    market_prompt = """
Eres un experto analista de mercado DeFi. Necesito un análisis DETALLADO y CON DATOS REALES del mercado actual (Diciembre 2025) para evaluar un negocio:

NEGOCIO: **DeFi Monitor** - Dashboard automatizado que monitorea yields de 20+ protocolos DeFi

CONTEXTO:
- MVP completado: GitHub Actions scraping DeFi Llama API cada 6 horas
- Output: JSON con APY de 20+ pools (Aave, Compound, Curve, etc.)
- Estado actual: Solo alertas básicas en JSON
- Fase 2 pendiente: Email alerts + Web dashboard + Freemium model

COMPETENCIA CONOCIDA:
- Telegram bots: DeFi Alert Bot (~50k+ users), Yield Alert (~20k)
- Binance/Coinbase: Adding native yield tracking
- DeFi Llama: Dashboard gratuito (pero sin alertas personalizadas)
- Zapper, DeBank: Portfolio tracking (partial yield alerts)

NECESITO ANÁLISIS CON DATOS REALES DE:

1. **MERCADO DeFi ACTUAL (Diciembre 2025)**:
   - TVL Total DeFi (en USD)
   - Crecimiento YTD 2025
   - Estado bull/bear market
   - Número estimado de usuarios activos DeFi
   - Sentiment general (Google Trends, Twitter)

2. **COMPETENCIA Y SATURACIÓN**:
   - Cuántos servicios similares existen AHORA
   - Usuarios totales estimados en bots/dashboards competidores
   - Saturación del mercado (0-100%)
   - Feature gaps (qué NO ofrecen los competidores)

3. **DEMANDA POR ALERTAS DE YIELD**:
   - Búsquedas Google: "defi yield alerts", "apy notifications"
   - Menciones Twitter/Reddit últimos 30 días
   - Engagement en posts sobre yield farming
   - Willingness to pay ($5-15/mes)

4. **VIABILIDAD TÉCNICA**:
   - APIs DeFi disponibles (DeFi Llama, The Graph, Covalent)
   - Confiabilidad de APIs (uptime, rate limits)
   - Costo de infraestructura (AWS/Vercel para 100-1000 users)

5. **MONETIZACIÓN**:
   - Benchmarks de precios: Bots similares cobran cuánto?
   - Conversion rates típicos: freemium → paid
   - CAC (Customer Acquisition Cost) en crypto/DeFi nicho
   - LTV estimado para usuario pagando

6. **TIMING**:
   - ¿Es buen momento para lanzar? (bull vs bear market)
   - Tendencia de inversión en DeFi últimos 6 meses
   - Predicciones Q1-Q2 2026

**IMPORTANTE**: 
- Usa DATOS REALES y ACTUALES (Diciembre 2025)
- Proporciona números específicos (no rangos vagos)
- Cita fuentes cuando sea posible
- Sé crítico y realista (no optimista sin fundamento)

**OUTPUT ESPERADO**:
JSON con estructura:
{
  "market_analysis": {
    "tvl_total_usd": <número>,
    "ytd_growth_percent": <número>,
    "market_phase": "bull/bear/sideways",
    "active_users_estimate": <número>,
    "google_trends_score": <0-100>
  },
  "competition": {
    "saturation_percent": <0-100>,
    "total_competitors": <número>,
    "total_users_competitors": <número>,
    "feature_gaps": [<lista>]
  },
  "demand": {
    "search_volume_monthly": <número>,
    "social_mentions_30d": <número>,
    "willingness_to_pay_score": <0-10>
  },
  "technical_viability": {
    "api_reliability_score": <0-10>,
    "infrastructure_cost_100_users": <USD/mes>,
    "infrastructure_cost_1000_users": <USD/mes>
  },
  "monetization": {
    "competitor_pricing_usd": [<precios>],
    "freemium_conversion_rate": <0-1>,
    "estimated_cac_usd": <número>,
    "estimated_ltv_usd": <número>
  },
  "timing": {
    "launch_timing_score": <0-10>,
    "q1_q2_2026_outlook": "positive/neutral/negative"
  },
  "summary": "<resumen ejecutivo 3-5 líneas>"
}
"""
    
    try:
        print("   🌐 Consultando Gemini API (esto puede tomar 30-60 seg)...\n")
        response = model.generate_content(market_prompt)
        market_analysis_raw = response.text
        
        print("   ✅ Respuesta recibida\n")
        print("="*80)
        print("📊 GEMINI MARKET ANALYSIS (RAW)")
        print("="*80)
        print(market_analysis_raw)
        print("="*80 + "\n")
        
        # Intentar extraer JSON
        try:
            # Buscar JSON en la respuesta
            json_start = market_analysis_raw.find('{')
            json_end = market_analysis_raw.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                market_json = json.loads(market_analysis_raw[json_start:json_end])
                print("   ✅ JSON parseado exitosamente\n")
            else:
                market_json = {"raw_response": market_analysis_raw}
                print("   ⚠️  No se pudo extraer JSON, usando raw response\n")
        except:
            market_json = {"raw_response": market_analysis_raw}
            print("   ⚠️  Error parseando JSON, usando raw response\n")
        
    except Exception as e:
        print(f"   ❌ Error en Gemini API: {e}\n")
        market_json = {"error": str(e)}
    
    # ========================================================================
    # FASE 2: DECISIÓN CON FRAMEWORK v4.5.0
    # ========================================================================
    
    print("\n🧮 FASE 2: Aplicando Decision Framework v4.5.0\n")
    
    decision_prompt = f"""
Ahora usa el análisis de mercado anterior para evaluar 6 ALTERNATIVAS usando 5 METODOLOGÍAS del Decision Framework v4.5.0:

**ANÁLISIS DE MERCADO (de Gemini):**
```
{market_analysis_raw[:2000]}...
```

**6 ALTERNATIVAS:**
1. DeFi Monitor status quo (sin Fase 2)
2. DeFi Monitor CON Fase 2 (email alerts + web dashboard)
3. Pivotar a Discord Bot
4. Pivotar a B2B API
5. Pivotar a Analytics Premium
6. Abandonar proyecto

**5 METODOLOGÍAS:**

**1. Monitor Tiempo Real (Market Analysis Score 0-10)**
   - Disponibilidad producto (qué tan listo está)
   - Demanda actual (búsquedas, menciones)
   - Saturación mercado (cuánta competencia)

**2. Bayesian Updater (Posterior Probability %)**
   - Prior: 20% (creencia inicial)
   - Likelihood basado en evidencia de mercado
   - Posterior = (Prior × Likelihood) / normalización

**3. Scenario Analysis (Valor Esperado USD)**
   - Pesimista: -20% usuarios, -30% precio
   - Realista: Baseline del mercado
   - Optimista: +50% usuarios, +20% precio
   - VE = (P×V_pes + R×V_real + O×V_opt) / 3

**4. ML Predictor (Satisfaction Score 0-100)**
   - Features: Market fit, Technical complexity, Time to market, Competition
   - Predice satisfacción post-decisión
   - Entrenado en patrones de éxito/fracaso crypto projects

**5. Value at Risk (VaR 95% - Downside USD)**
   - Peor escenario en 95% casos
   - Cuánto puedes perder en dinero + tiempo

**OUTPUT JSON ESPERADO:**
{{
  "alternatives": [
    {{
      "name": "DeFi Monitor sin Fase 2",
      "methodology_1_score": <0-10>,
      "methodology_2_posterior": <0-100%>,
      "methodology_3_expected_value": <USD>,
      "methodology_4_ml_score": <0-100>,
      "methodology_5_var_95": <-USD>
    }},
    ...
  ],
  "voting": {{
    "methodology_1_winner": "<nombre>",
    "methodology_2_winner": "<nombre>",
    "methodology_3_winner": "<nombre>",
    "methodology_4_winner": "<nombre>",
    "methodology_5_winner": "<nombre>"
  }},
  "final_recommendation": {{
    "winner": "<nombre>",
    "votes": <3-5>,
    "confidence_percent": <70-95>,
    "reasoning": "<por qué ganó>"
  }},
  "action_plan": {{
    "immediate_steps": [<lista>],
    "timeline_weeks": <número>,
    "critical_success_factors": [<lista>]
  }}
}}

**SÉ ESPECÍFICO CON NÚMEROS Y USA EL ANÁLISIS DE MERCADO ANTERIOR.**
"""
    
    try:
        print("   🧮 Aplicando metodologías del framework...\n")
        response2 = model.generate_content(decision_prompt)
        decision_analysis_raw = response2.text
        
        print("   ✅ Análisis de decisión completado\n")
        print("="*80)
        print("🎯 GEMINI DECISION ANALYSIS (RAW)")
        print("="*80)
        print(decision_analysis_raw)
        print("="*80 + "\n")
        
        # Intentar extraer JSON
        try:
            json_start = decision_analysis_raw.find('{')
            json_end = decision_analysis_raw.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                decision_json = json.loads(decision_analysis_raw[json_start:json_end])
                print("   ✅ JSON de decisión parseado\n")
            else:
                decision_json = {"raw_response": decision_analysis_raw}
        except:
            decision_json = {"raw_response": decision_analysis_raw}
        
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
        decision_json = {"error": str(e)}
    
    # ========================================================================
    # GUARDAR RESULTADOS
    # ========================================================================
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "framework_version": "v4.5.0",
        "gemini_model": "gemini-2.0-flash-exp",
        "phase_1_market_research": market_json,
        "phase_2_decision_framework": decision_json,
        "raw_market_response": market_analysis_raw,
        "raw_decision_response": decision_analysis_raw
    }
    
    output_file = "/Users/arturo/development/GitHub/desicion-maker/DEFI_MONITOR_GEMINI_ANALYSIS.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados guardados en: {output_file}\n")
    
    # ========================================================================
    # RESUMEN EJECUTIVO
    # ========================================================================
    
    print("\n" + "="*80)
    print("✨ RESUMEN EJECUTIVO")
    print("="*80 + "\n")
    
    if "final_recommendation" in decision_json:
        rec = decision_json["final_recommendation"]
        print(f"🏆 GANADOR: {rec.get('winner', 'N/A')}")
        print(f"📊 VOTOS: {rec.get('votes', 'N/A')}/5 metodologías")
        print(f"✅ CONFIANZA: {rec.get('confidence_percent', 'N/A')}%")
        print(f"\n💡 RAZÓN:\n   {rec.get('reasoning', 'N/A')}")
        
        if "action_plan" in decision_json:
            plan = decision_json["action_plan"]
            print(f"\n📋 PLAN DE ACCIÓN:")
            print(f"   Timeline: {plan.get('timeline_weeks', 'N/A')} semanas")
            print(f"   Pasos inmediatos:")
            for step in plan.get('immediate_steps', [])[:3]:
                print(f"     - {step}")
    else:
        print("⚠️  Revisar JSON de decisión manualmente")
    
    print("\n" + "="*80)
    print("🎯 Análisis completado con éxito")
    print("="*80 + "\n")
    
    return results


if __name__ == "__main__":
    results = analyze_defi_monitor_with_gemini()
