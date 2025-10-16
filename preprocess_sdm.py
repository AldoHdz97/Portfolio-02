import csv
import json
from typing import List, Dict, Any, Optional

def categorize_score(score: Optional[int]) -> Optional[str]:
    """
    Categorize score based on ranges:
    0-75: deficiente
    76-100: regular
    101-120: satisfactorio
    121-140: sobresaliente
    141+: excepcional
    """
    if score is None:
        return None
    
    if score <= 75:
        return "deficiente"
    elif score <= 100:
        return "regular"
    elif score <= 120:
        return "satisfactorio"
    elif score <= 140:
        return "sobresaliente"
    else:  # 141+
        return "excepcional"


def parse_campus_scores_csv(csv_file: str, json_file: str):
    """
    Parse campus performance scores from 2-column CSV format.
    Converts to structured JSON matching Agent3Output schema.
    Adds score categorization for each metric.
    """
    
    campuses = []
    current_campus = None
    current_platform = None
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        for row in reader:
            if len(row) < 2:
                continue
            
            left_col = row[0].strip().lower()
            right_col = row[1].strip()
            
            # Detect campus name
            if left_col == 'campus':
                # Save previous campus if exists
                if current_campus:
                    campuses.append(current_campus)
                
                # Start new campus
                campus_name = right_col
                campus_id = map_campus_name_to_id(campus_name)
                
                current_campus = {
                    'campus_id': campus_id,
                    'campus_name': campus_name,
                    'facebook': {},
                    'twitter': {},
                    'instagram': {},
                    'totales': {}
                }
                current_platform = None
            
            # Detect platform
            elif left_col in ['facebook', 'twitter', 'instagram', 'totales']:
                current_platform = left_col
            
            # Detect score type
            elif left_col in ['visibilidad', 'resonancia', 'permanencia', 'sentimiento', 'salud de marca']:
                score_type = normalize_score_name(left_col)
                score_value = parse_score(right_col)
                category = categorize_score(score_value)
                
                if current_platform and current_campus:
                    current_campus[current_platform][score_type] = score_value
                    current_campus[current_platform][f"{score_type}_categoria"] = category
        
        # Don't forget last campus
        if current_campus:
            campuses.append(current_campus)
    
    # Create final output structure
    output = {
        'campuses': campuses,
        'metadata': {
            'total_campuses': len(campuses),
            'source': csv_file,
            'categorization': {
                'deficiente': '0-75',
                'regular': '76-100',
                'satisfactorio': '101-120',
                'sobresaliente': '121-140',
                'excepcional': '141+'
            }
        }
    }
    
    # Save to JSON
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Procesados {len(campuses)} campuses con categorización")
    print(f"💾 JSON guardado en: {json_file}")
    
    # Print summary with categories
    print("\n📊 Summary por campus:")
    for campus in campuses:
        print(f"\n  {campus['campus_id']} - {campus['campus_name']}")
        print(f"    Facebook Salud de Marca: {campus['facebook'].get('salud_de_marca')} "
              f"({campus['facebook'].get('salud_de_marca_categoria', 'N/A')})")
        print(f"    Instagram Salud de Marca: {campus['instagram'].get('salud_de_marca')} "
              f"({campus['instagram'].get('salud_de_marca_categoria', 'N/A')})")
        print(f"    Totales Salud de Marca: {campus['totales'].get('salud_de_marca')} "
              f"({campus['totales'].get('salud_de_marca_categoria', 'N/A')})")
    
    return output


def map_campus_name_to_id(campus_name: str) -> str:
    """Map campus full name to campus_id"""
    
    CAMPUS_MAPPING = {
        'Monterrey': 'MTY',
        'Puebla': 'PUE',
        'Guadalajara': 'GDL',
        'Ciudad Juárez': 'CDJ',
        'Toluca': 'TOL',
        'Ciudad de México': 'CCM',
        'Estado de México': 'CEM',
        'Querétaro': 'QRO',
        'Chihuahua': 'CHI',
        'Sinaloa': 'SIN',
        'Aguascalientes': 'AGS',
        'Ciudad Obregón': 'COB',
        'León': 'LEO',
        'Laguna': 'LAG',
        'Sonora': 'SON',
        'Hidalgo': 'HGO',
        'San Luis Potosí': 'SLP',
        'Cuernavaca': 'CVA',
        'Santa Fe': 'CSF',
        'Saltillo': 'SAL',
    }
    
    # Case-insensitive lookup
    for full_name, code in CAMPUS_MAPPING.items():
        if full_name.lower() in campus_name.lower():
            return code
    
    # Fallback
    return campus_name[:3].upper()


def normalize_score_name(score_name: str) -> str:
    """Normalize score field names to match schema"""
    
    mapping = {
        'visibilidad': 'visibilidad',
        'resonancia': 'resonancia',
        'permanencia': 'permanencia',
        'sentimiento': 'sentimiento',
        'salud de marca': 'salud_de_marca'
    }
    
    return mapping.get(score_name.lower(), score_name)


def parse_score(value: str) -> Optional[int]:
    """Parse score value, handle 'calificaciones' and empty values"""
    
    if not value or value.lower() == 'calificaciones':
        return None
    
    try:
        # Remove commas and convert to int
        return int(value.replace(',', ''))
    except ValueError:
        return None


# ============================================================================
# USAGE
# ============================================================================
if __name__ == "__main__":
    parse_campus_scores_csv(
        csv_file='Regiones Unificadas - Valores.csv',
        json_file='sdm_estructurado.json'
    )