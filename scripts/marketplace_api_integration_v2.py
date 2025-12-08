#!/usr/bin/env python3
"""
Marketplace API Integration for Real-Time Price Monitoring
Collects data from OLX, Mercado Libre, and other sources
Validates decision-making algorithm with real market data
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Tuple
import requests
from bs4 import BeautifulSoup


class MarketplaceDataCollector:
    """Collects real-time marketplace data for decision validation."""
    
    def __init__(self, product_type: str = "sillon"):
        """Initialize collector for specific product type."""
        self.product_type = product_type
        self.market_data = {}
        self.timestamp = datetime.now().isoformat()
        
    def search_olx(self, query: str, category: str = "furniture",
                   location: str = "La Florida") -> Dict:
        """
        Search OLX Chile using web scraping.
        
        Args:
            query: Search term (e.g., "sillon")
            category: Product category
            location: Geographic location
            
        Returns:
            Dictionary with price data and listings
        """
        try:
            base_url = "https://www.olx.cl/items/q-"
            search_url = f"{base_url}{query}"
            
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36"
                )
            }
            
            response = requests.get(search_url, headers=headers,
                                   timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            listings = []
            prices = []
            
            # Parse OLX listings
            for item in soup.find_all('div', class_='items'):
                try:
                    title_elem = item.find('span', class_='title')
                    price_elem = item.find('span', class_='price')
                    
                    if title_elem and price_elem:
                        title = title_elem.text.strip()
                        price_text = price_elem.text.strip()
                        
                        # Extract numeric price
                        price_match = re.search(
                            r'[\$]?([\d,]+)',
                            price_text
                        )
                        if price_match:
                            price = int(
                                price_match.group(1).replace(',', '')
                            )
                            prices.append(price)
                            listings.append({
                                'title': title,
                                'price': price,
                                'source': 'OLX'
                            })
                except (AttributeError, ValueError):
                    continue
            
            return {
                'source': 'OLX',
                'listings': listings,
                'count': len(listings),
                'prices': prices,
                'avg_price': sum(prices) / len(prices)
                if prices else 0,
                'min_price': min(prices) if prices else 0,
                'max_price': max(prices) if prices else 0,
            }
            
        except Exception as e:
            return {
                'source': 'OLX',
                'error': str(e),
                'listings': [],
                'count': 0
            }
    
    def search_mercadolibre(self, query: str) -> Dict:
        """
        Search Mercado Libre using official API.
        
        Args:
            query: Search term
            
        Returns:
            Dictionary with price data from Mercado Libre
        """
        try:
            base_url = "https://api.mercadolibre.com/sites/MLC/search"
            params = {
                'q': query,
                'limit': 50,
                'sort': 'price_asc'
            }
            
            response = requests.get(base_url, params=params,
                                   timeout=10)
            response.raise_for_status()
            data = response.json()
            
            listings = []
            prices = []
            
            for item in data.get('results', []):
                try:
                    listing = {
                        'title': item.get('title', ''),
                        'price': item.get('price', 0),
                        'currency': item.get('currency_id', 'CLP'),
                        'condition': item.get('condition', 'unknown'),
                        'source': 'Mercado Libre'
                    }
                    listings.append(listing)
                    prices.append(item.get('price', 0))
                except (KeyError, TypeError):
                    continue
            
            return {
                'source': 'Mercado Libre',
                'listings': listings,
                'count': len(listings),
                'prices': prices,
                'avg_price': sum(prices) / len(prices)
                if prices else 0,
                'min_price': min(prices) if prices else 0,
                'max_price': max(prices) if prices else 0,
            }
            
        except Exception as e:
            return {
                'source': 'Mercado Libre',
                'error': str(e),
                'listings': [],
                'count': 0
            }
    
    def analyze_market_data(self, results: List[Dict]) -> Dict:
        """
        Analyze aggregated market data from all sources.
        
        Args:
            results: List of search results from all marketplaces
            
        Returns:
            Comprehensive market analysis
        """
        all_prices = []
        listings_count = 0
        
        for result in results:
            if 'prices' in result:
                all_prices.extend(result['prices'])
                listings_count += result.get('count', 0)
        
        if not all_prices:
            return {'error': 'No price data available'}
        
        all_prices.sort()
        median_price = all_prices[len(all_prices) // 2]
        avg_price = sum(all_prices) / len(all_prices)
        
        return {
            'total_listings': listings_count,
            'avg_price': avg_price,
            'median_price': median_price,
            'min_price': min(all_prices),
            'max_price': max(all_prices),
            'price_std': self._calculate_std(all_prices),
            'saturation_level': self._calculate_saturation(
                listings_count
            ),
            'demand_level': self._assess_demand(listings_count),
        }
    
    def _calculate_saturation(self, listing_count: int) -> float:
        """
        Calculate market saturation (0=low, 1=high).
        
        Args:
            listing_count: Total number of listings
            
        Returns:
            Saturation score 0-1
        """
        # Heuristic: more than 500 listings = saturated market
        if listing_count > 500:
            return 1.0
        elif listing_count > 200:
            return 0.7
        elif listing_count > 50:
            return 0.5
        else:
            return 0.2
    
    def _assess_demand(self, listing_count: int) -> str:
        """
        Assess demand level based on listing volume.
        
        Args:
            listing_count: Total number of listings
            
        Returns:
            Demand level: ALTA, MEDIA, or BAJA
        """
        if listing_count > 200:
            return "BAJA"  # Saturated = low demand
        elif listing_count > 50:
            return "MEDIA"
        else:
            return "ALTA"  # Few listings = high relative demand
    
    def _calculate_std(self, prices: List[float]) -> float:
        """Calculate standard deviation of prices."""
        if len(prices) < 2:
            return 0.0
        mean = sum(prices) / len(prices)
        variance = sum((x - mean) ** 2 for x in prices) / len(prices)
        return variance ** 0.5
    
    def _estimate_days_to_sale(self, listings_count: int,
                               demand: str) -> float:
        """
        Estimate average days to sell based on demand.
        
        Args:
            listings_count: Total marketplace listings
            demand: Demand level (ALTA/MEDIA/BAJA)
            
        Returns:
            Estimated days to sale
        """
        if demand == "ALTA":
            return 7  # High demand, sells fast
        elif demand == "MEDIA":
            return 30
        else:
            return 180  # Low demand, slow sale
    
    def update_probability_with_market_data(
        self,
        prior_probability: float,
        market_data: Dict
    ) -> float:
        """
        Update sale probability using Bayesian rule.
        
        Uses market data (supply/demand/saturation) to update
        prior probability from Gemini analysis.
        
        P(sale|market) = P(market|sale) * P(sale) / P(market)
        
        Args:
            prior_probability: Initial probability from Gemini (e.g., 0.04)
            market_data: Market analysis results
            
        Returns:
            Updated posterior probability
        """
        # Likelihood: P(market|sale happens)
        # If product sells well, we expect ALTA demand
        p_market_given_sale = 0.8 if (
            market_data.get('demand_level') == "ALTA"
        ) else 0.3
        
        # Evidence: P(market) - marginal probability
        demand = market_data.get('demand_level', 'MEDIA')
        if demand == "ALTA":
            p_market = 0.4
        elif demand == "MEDIA":
            p_market = 0.4
        else:
            p_market = 0.2
        
        # Bayesian update
        posterior = (
            (p_market_given_sale * prior_probability) / p_market
        )
        
        # Cap between 0 and 1
        return min(1.0, max(0.0, posterior))
    
    def generate_report(self, results: List[Dict],
                       analysis: Dict,
                       prior_prob: float = 0.04) -> str:
        """
        Generate markdown report of market analysis.
        
        Args:
            results: Search results from marketplaces
            analysis: Market analysis
            prior_prob: Prior probability from Gemini
            
        Returns:
            Markdown formatted report
        """
        posterior = self.update_probability_with_market_data(
            prior_prob,
            analysis
        )
        
        report = f"""# 📊 REPORTE ANÁLISIS MARKETPLACE

**Fecha:** {self.timestamp}
**Producto:** {self.product_type}

## 1. DATOS RECABADOS

"""
        
        for result in results:
            if 'error' not in result:
                report += f"""
### {result.get('source')}
- Listings encontrados: {result.get('count')}
- Precio promedio: ${result.get('avg_price', 0):,.0f}
- Rango: ${result.get('min_price', 0):,} - \
${result.get('max_price', 0):,}

"""
        
        report += f"""## 2. ANÁLISIS AGREGADO

- **Total Listings:** {analysis.get('total_listings')}
- **Precio Promedio:** ${analysis.get('avg_price', 0):,.0f}
- **Precio Mediano:** ${analysis.get('median_price', 0):,.0f}
- **Desv. Estándar:** ${analysis.get('price_std', 0):,.0f}
- **Saturación:** {analysis.get('saturation_level', 0):.1%}
- **Demanda:** {analysis.get('demand_level')}

## 3. ACTUALIZACIÓN PROBABILÍSTICA

- Prior (Gemini): {prior_prob:.1%}
- Posterior (Bayes): {posterior:.1%}
- Cambio: {(posterior - prior_prob):.1%}

### Interpretación

"""
        
        if posterior > 0.3:
            report += "✅ Demanda significativa en mercado"
        elif posterior > 0.1:
            report += "⚠️  Demanda limitada"
        else:
            report += "❌ Demanda muy baja"
        
        return report


def main():
    """Main execution function."""
    print("🔍 Iniciando búsqueda de mercado...")
    
    collector = MarketplaceDataCollector(product_type="sillon restaurado")
    
    # Search marketplaces
    print("   → Buscando en OLX...")
    olx_results = collector.search_olx("sillon", location="La Florida")
    
    print("   → Buscando en Mercado Libre...")
    ml_results = collector.search_mercadolibre("sillon")
    
    results = [olx_results, ml_results]
    
    # Analyze data
    print("   → Analizando datos...")
    analysis = collector.analyze_market_data(results)
    
    # Generate report
    report = collector.generate_report(
        results,
        analysis,
        prior_prob=0.04
    )
    
    # Save results
    output_file = "scripts/marketplace_report.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ Reporte guardado en: {output_file}")
    print("\n" + "=" * 60)
    print(report)
    print("=" * 60)


if __name__ == "__main__":
    main()
