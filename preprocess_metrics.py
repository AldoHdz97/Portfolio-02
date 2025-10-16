import json
import re
from typing import List, Dict, Optional

def extract_campus_from_region(region: str) -> tuple[str, str]:
    """Extract campus ID and name from REGION field - handles multiple formats"""
    
    CAMPUS_MAPPING = {
        'MTY': 'Monterrey',
        'PUE': 'Puebla',
        'GDL': 'Guadalajara',
        'CDJ': 'Cd. Juárez',
        'TOL': 'Toluca',
        'CCM': 'Ciudad de México',
        'CEM': 'Estado de México',
        'QRO': 'Querétaro',
        'CHI': 'Chihuahua',
        'SIN': 'Sinaloa',
        'AGS': 'Aguascalientes',
        'COB': 'Cd. Obregón',
        'LEO': 'León',
        'LAG': 'Laguna',
        'SON': 'Sonora',
        'HGO': 'Hidalgo',
        'SLP': 'San Luis Potosí',
        'CVA': 'Cuernavaca',
        'CSF': 'Santa Fe',
        'SAL': 'Saltillo',
    }
    
    # Strategy 1: Try to extract from parentheses "Campus Name (MTY)"
    match = re.search(r'\((\w+)\)', region)
    if match:
        campus_id = match.group(1).upper()
        campus_name = CAMPUS_MAPPING.get(campus_id, campus_id)
        return campus_id, campus_name
    
    # Strategy 2: Look for campus ID codes directly in the text
    region_upper = region.upper()
    for code in CAMPUS_MAPPING.keys():
        if code in region_upper:
            return code, CAMPUS_MAPPING[code]
    
    # Strategy 3: Look for campus full names in the text
    for code, name in CAMPUS_MAPPING.items():
        if name.lower() in region.lower():
            return code, name
    
    # Fallback: Use first 3 letters
    campus_id = region[:3].upper() if len(region) >= 3 else "UNK"
    return campus_id, region


def process_metrics(current_file: str, previous_file: str, output_file: str):
    """
    Merge current and previous year metrics into Agent2Output format.
    Matches by REGION field and creates unified structure.
    """
    
    print("📖 Reading metrics files...")
    
    # Load current month metrics
    current_data = []
    with open(current_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                current_data.append(json.loads(line))
    
    print(f"✅ Current month: {len(current_data)} regions")
    
    # Load previous year metrics
    previous_data = []
    with open(previous_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                previous_data.append(json.loads(line))
    
    print(f"✅ Previous year: {len(previous_data)} regions")
    
    # Create lookup dictionary for previous data by REGION
    previous_lookup = {item['REGION']: item for item in previous_data}
    
    # Process and merge
    regions = []
    
    for current in current_data:
        region_str = current.get('REGION', '')
        
        # Extract campus info
        campus_id, campus_name = extract_campus_from_region(region_str)
        
        # Find matching previous year data
        previous = previous_lookup.get(region_str, None)
        
        # Create current month metrics
        current_metrics = {
            'POST_COMMENTS__SUM': current.get('POST_COMMENTS__SUM', 0),
            'ALCANCE_TOTAL': current.get('ALCANCE_TOTAL', 0.0),
            'VOLUMEN_DE_PUBLICACIONES': current.get('VOLUMEN_DE_PUBLICACIONES', 0),
            'INTERACCIONES_TOTALES': current.get('INTERACCIONES_TOTALES', 0)
        }
        
        # Create previous year metrics (if exists)
        if previous:
            previous_metrics = {
                'POST_COMMENTS__SUM': previous.get('POST_COMMENTS__SUM', 0),
                'ALCANCE_TOTAL': previous.get('ALCANCE_TOTAL', 0.0),
                'VOLUMEN_DE_PUBLICACIONES': previous.get('VOLUMEN_DE_PUBLICACIONES', 0),
                'INTERACCIONES_TOTALES': previous.get('INTERACCIONES_TOTALES', 0)
            }
        else:
            previous_metrics = {
                'POST_COMMENTS__SUM': 0,
                'ALCANCE_TOTAL': 0.0,
                'VOLUMEN_DE_PUBLICACIONES': 0,
                'INTERACCIONES_TOTALES': 0
            }
            print(f"⚠️  No previous data for {campus_name} ({campus_id})")
        
        # Create combined region object
        region_combined = {
            'campus_id': campus_id,
            'campus_name': campus_name,
            'current_month': current_metrics,
            'previous_year_month': previous_metrics
        }
        
        regions.append(region_combined)
    
    # Create Agent2Output structure
    output = {
        'regions': regions,
        'metadata': {
            'total_regions': len(regions),
            'current_file': current_file,
            'previous_file': previous_file
        }
    }
    
    # Save to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Merged metrics for {len(regions)} regions")
    print(f"💾 JSON saved to: {output_file}")
    
    # Print summary
    print("\n📊 Summary:")
    for region in regions:
        print(f"  {region['campus_id']:4s} | {region['campus_name']:20s} | "
              f"Current: {region['current_month']['INTERACCIONES_TOTALES']:6d} | "
              f"Previous: {region['previous_year_month']['INTERACCIONES_TOTALES']:6d}")
    
    return output


# ============================================================================
# USAGE
# ============================================================================
if __name__ == "__main__":
    process_metrics(
        current_file='Mes_Actual_2_SDMxRegion.json',
        previous_file='Mes_del_A_o_anterior_3_SDMxRegion.json',
        output_file='metrics_estructurado.json'
    )

    