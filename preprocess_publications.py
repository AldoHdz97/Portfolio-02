# preprocess_publications.py
import json
import re
from collections import defaultdict

def filter_publications(input_file, output_file):
    """
    Reads large publication file, filters to top posts per campus BY PLATFORM:
    - Top 4 Instagram posts per campus
    - Top 4 Facebook posts per campus  
    - No Twitter/X posts
    Total: 8 posts per campus maximum
    ONLY keeps essential fields to reduce data size
    Campus ID is stored at parent level only (not repeated in each post)
    """
    print(f"📖 Reading {input_file}...")
    
    # Read all publications
    publications_data = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                publications_data.append(json.loads(line))
    
    print(f"✅ Loaded {len(publications_data)} publications")
    
    # Group by campus AND platform
    campus_platform_posts = defaultdict(lambda: defaultdict(list))
    
    for pub in publications_data:
        account = pub.get('ACCOUNT', '')
        social_network = pub.get('SOCIAL_NETWORK', '').lower()
        
        # Extract campus ID
        match = re.search(r'Campus\s+(\w+)\s+\[', account, re.IGNORECASE)
        
        if match:
            campus_id = match.group(1).upper()
            interactions = pub.get('INTERACCIONES_GENERAL__SUM', 0) or 0
            alcance = pub.get('ALCANCE_GENERAL__SUM', 0) or 0
            
            # Calculate engagement score
            engagement_score = (interactions * 10) + alcance
            
            # Normalize platform names - ONLY Instagram and Facebook
            if 'instagram' in social_network:
                platform = 'instagram'
            elif 'facebook' in social_network:
                platform = 'facebook'
            else:
                continue  # Skip all other platforms
            
            # Keep ONLY essential fields
            # NOTE: campus_id is NOT included here - it's at parent level
            filtered_pub = {
                'PUBLISHEDTIME': pub.get('PUBLISHEDTIME', ''),
                'SOCIAL_NETWORK': pub.get('SOCIAL_NETWORK', ''),
                'INTERACCIONES_GENERAL__SUM': interactions,
                'ACCOUNT': pub.get('ACCOUNT', ''),
                'ALCANCE_GENERAL__SUM': alcance,
                'OUTBOUND_POST': pub.get('OUTBOUND_POST', ''),
                'engagement_score': engagement_score
            }
            
            campus_platform_posts[campus_id][platform].append(filtered_pub)
    
    # Filter to top 4 per platform per campus
    platform_limits = {
        'instagram': 4,
        'facebook': 4,
    }
    
    campus_grouped_output = []
    campus_stats = {}
    
    for campus_id, platforms in campus_platform_posts.items():
        campus_posts = []
        campus_breakdown = {}
        
        for platform, posts in platforms.items():
            limit = platform_limits.get(platform, 0)
            
            if limit > 0:
                # Sort by engagement score and take top N
                sorted_posts = sorted(posts, key=lambda x: x['engagement_score'], reverse=True)
                top_posts = sorted_posts[:limit]
                campus_posts.extend(top_posts)
                
                campus_breakdown[platform] = len(top_posts)
        
        # Create grouped structure for this campus
        # campus_id is here at parent level, NOT in each post
        campus_grouped_output.append({
            'campus_id': campus_id,
            'publications': campus_posts  # All 8 posts for this campus
        })
        
        campus_stats[campus_id] = {
            'total': len(campus_posts),
            'breakdown': campus_breakdown
        }
    
    # Save grouped data (one JSON object per campus)
    print(f"\n💾 Saving {len(campus_grouped_output)} campuses with their publications to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        for campus_data in campus_grouped_output:
            f.write(json.dumps(campus_data, ensure_ascii=False) + '\n')
    
    # Print statistics
    total_pubs = sum(len(c['publications']) for c in campus_grouped_output)
    print(f"\n✅ Filtered file created: {output_file}")
    print(f"📊 Reduction: {len(publications_data)} → {total_pubs} publications")
    print(f"🎯 {len(campus_stats)} campuses found")
    print(f"📦 Output format: Pre-grouped by campus (one line per campus)")
    print(f"🧹 Cleaner structure: campus_id only at parent level (not repeated in posts)\n")
    
    print("📈 Breakdown per campus:")
    for campus_id, stats in sorted(campus_stats.items()):
        breakdown = ', '.join([f"{k}: {v}" for k, v in stats['breakdown'].items()])
        print(f"   {campus_id}: {stats['total']} posts ({breakdown})")

if __name__ == "__main__":
    filter_publications(
        input_file='Todas_las_publicaciones_con_sus_metricas_1_SDMxRegion.json',
        output_file='Publicaciones_estructuradas_Top8.json'
    )