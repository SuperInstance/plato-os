#!/usr/bin/env python3
"""
Tile Network Optimization: Caching Implementation
Implements LRU cache for frequently used tiles.
"""

import time
from collections import OrderedDict
from typing import Optional, List, Dict
import sys
sys.path.insert(0, '/tmp')

try:
    from plato_notebook_v2 import PlatoNotebook
    HAS_TILES = True
except:
    HAS_TILES = False

class TileCache:
    """LRU cache for tiles."""
    
    def __init__(self, max_size: int = 100):
        self.cache = OrderedDict()  # tile_id -> (tile, timestamp, access_count)
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
        self.evictions = 0
    
    def get(self, tile_id: str):
        """Get tile from cache, update access time."""
        if tile_id in self.cache:
            # Move to end (most recently used)
            tile_data = self.cache.pop(tile_id)
            self.cache[tile_id] = (tile_data[0], time.time(), tile_data[2] + 1)
            self.hits += 1
            return tile_data[0]
        
        self.misses += 1
        return None
    
    def put(self, tile_id: str, tile):
        """Add tile to cache."""
        if tile_id in self.cache:
            # Update existing
            self.cache.pop(tile_id)
        
        # Add new entry
        self.cache[tile_id] = (tile, time.time(), 1)
        
        # Evict if needed
        if len(self.cache) > self.max_size:
            self._evict()
    
    def _evict(self):
        """Evict least recently used tile."""
        if self.cache:
            self.cache.popitem(last=False)  # Remove first (oldest)
            self.evictions += 1
    
    def get_stats(self) -> Dict:
        """Get cache statistics."""
        total_accesses = self.hits + self.misses
        hit_rate = (self.hits / total_accesses * 100) if total_accesses > 0 else 0
        
        # Calculate average access count
        access_counts = [data[2] for data in self.cache.values()]
        avg_accesses = sum(access_counts) / len(access_counts) if access_counts else 0
        
        # Find most accessed tile
        most_accessed = None
        if self.cache:
            most_accessed = max(self.cache.items(), key=lambda x: x[1][2])
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.1f}%",
            "evictions": self.evictions,
            "avg_accesses_per_tile": f"{avg_accesses:.1f}",
            "most_accessed": most_accessed[0] if most_accessed else None,
            "most_accessed_count": most_accessed[1][2] if most_accessed else 0
        }
    
    def warmup(self, tiles: Dict, access_threshold: int = 2):
        """Warm up cache with frequently accessed tiles."""
        for tile_id, tile in tiles.items():
            if tile.usage_count >= access_threshold:
                self.put(tile_id, tile)
        
        print(f"Cache warmed up with {len(self.cache)} tiles (usage ≥ {access_threshold})")

class OptimizedTilingSubstrate:
    """Tiling substrate with caching optimization."""
    
    def __init__(self, cache_size: int = 100):
        if not HAS_TILES:
            print("ERROR: PlatoNotebook not available")
            return
        
        self.plato = PlatoNotebook()
        self.cache = TileCache(max_size=cache_size)
        
        # Warm up cache with existing usage data
        self.cache.warmup(self.plato.substrate.tiles, access_threshold=1)
        
        print(f"Optimized substrate ready: {len(self.plato.substrate.tiles)} tiles, cache size {cache_size}")
    
    def tutor_jump_with_cache(self, anchor: str) -> str:
        """TUTOR_JUMP with caching."""
        start = time.time()
        
        # Try to find tile by tag match (cached)
        cached_tiles = []
        for tile_id, tile in self.plato.substrate.tiles.items():
            if anchor.lower() in [t.lower() for t in tile.tags]:
                # Check cache first
                cached_tile = self.cache.get(tile_id)
                if cached_tile:
                    cached_tiles.append(cached_tile)
                else:
                    # Not in cache, add it
                    self.cache.put(tile_id, tile)
                    cached_tiles.append(tile)
                
                if len(cached_tiles) >= 3:
                    break
        
        latency = (time.time() - start) * 1000
        
        if cached_tiles:
            result = f"TUTOR_JUMP to [{anchor}] (cached: {len(cached_tiles)} tiles, {latency:.2f} ms):\n"
            for tile in cached_tiles[:2]:
                result += f"\n## {tile.tile_id}\nQ: {tile.question}\nA: {tile.answer[:150]}...\n"
            return result
        
        # Fallback: retrieve relevant
        relevant = self.plato.substrate.retrieve_relevant_tiles(anchor, max_tiles=2)
        if relevant:
            # Cache these tiles
            for tile in relevant:
                self.cache.put(tile.tile_id, tile)
            
            result = f"TUTOR_JUMP to [{anchor}] (retrieved: {len(relevant)} tiles, {latency:.2f} ms):\n"
            for tile in relevant:
                result += f"\n## {tile.tile_id}\nQ: {tile.question}\nA: {tile.answer[:150]}...\n"
            return result
        
        return f"No tiles found for anchor [{anchor}] ({latency:.2f} ms)"
    
    def build_context_with_cache(self, query: str, max_tokens: int = 2000) -> str:
        """Build context with caching optimization."""
        start = time.time()
        
        # Get relevant tiles
        relevant = self.plato.substrate.retrieve_relevant_tiles(query, max_tiles=5)
        
        context = ""
        token_count = 0
        cached_count = 0
        
        for tile in relevant:
            # Check cache
            cached_tile = self.cache.get(tile.tile_id)
            if cached_tile:
                cached_count += 1
                tile_to_use = cached_tile
            else:
                # Add to cache
                self.cache.put(tile.tile_id, tile)
                tile_to_use = tile
            
            # Build context
            tile_text = f"## {tile_to_use.tile_id}\nQ: {tile_to_use.question}\nA: {tile_to_use.answer[:300]}\n\n"
            tile_tokens = len(tile_text.split())
            
            if token_count + tile_tokens > max_tokens:
                break
            
            context += tile_text
            token_count += tile_tokens
            tile_to_use.usage_count += 1
        
        latency = (time.time() - start) * 1000
        
        stats = self.cache.get_stats()
        return f"""Context built ({latency:.2f} ms):
- Tiles used: {len(relevant)} ({cached_count} from cache)
- Tokens: {token_count}
- Cache hit rate: {stats['hit_rate']}
- Cache size: {stats['size']}/{stats['max_size']}

{context}"""
    
    def run_performance_test(self, num_iterations: int = 100) -> Dict:
        """Run performance test with caching."""
        test_anchors = ["management", "spatial-computing", "immune-system", "coordination", "tile-networks"]
        
        results = {
            "without_cache": [],
            "with_cache": [],
            "cache_stats": []
        }
        
        # Test without cache (first iteration)
        print("Testing without cache...")
        for anchor in test_anchors:
            start = time.time()
            result = self.plato.substrate.tutor_jump(anchor)
            latency = (time.time() - start) * 1000
            found = not result.startswith("No tiles found")
            
            results["without_cache"].append({
                "anchor": anchor,
                "latency_ms": latency,
                "found": found
            })
        
        # Test with cache (multiple iterations)
        print("Testing with cache...")
        for i in range(num_iterations):
            anchor = test_anchors[i % len(test_anchors)]
            start = time.time()
            result = self.tutor_jump_with_cache(anchor)
            latency = (time.time() - start) * 1000
            found = not result.startswith("No tiles found")
            
            results["with_cache"].append({
                "iteration": i + 1,
                "anchor": anchor,
                "latency_ms": latency,
                "found": found
            })
            
            # Record cache stats every 10 iterations
            if (i + 1) % 10 == 0:
                results["cache_stats"].append({
                    "iteration": i + 1,
                    **self.cache.get_stats()
                })
        
        return results

# Test optimization
if __name__ == "__main__":
    if not HAS_TILES:
        print("ERROR: Need plato_notebook_v2.py in /tmp")
        exit(1)
    
    print("=== Tile Network Optimization: Caching ===\n")
    
    # Create optimized substrate
    substrate = OptimizedTilingSubstrate(cache_size=50)
    
    # Test TUTOR_JUMP with cache
    print("\n=== TUTOR_JUMP with Caching ===")
    test_anchors = ["management", "spatial-computing", "immune-system", "coordination"]
    
    for anchor in test_anchors:
        print(f"\nAnchor: [{anchor}]")
        result = substrate.tutor_jump_with_cache(anchor)
        print(result[:200] + "..." if len(result) > 200 else result)
    
    # Test context building
    print("\n=== Context Building with Cache ===")
    test_queries = [
        "How to coordinate AI agents?",
        "What is spatial computing?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        context = substrate.build_context_with_cache(query, max_tokens=500)
        print(context[:300] + "..." if len(context) > 300 else context)
    
    # Get cache statistics
    print("\n=== Cache Statistics ===")
    stats = substrate.cache.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Performance comparison
    print("\n=== Performance Comparison ===")
    results = substrate.run_performance_test(num_iterations=20)
    
    avg_without = sum(r['latency_ms'] for r in results['without_cache']) / len(results['without_cache'])
    avg_with = sum(r['latency_ms'] for r in results['with_cache']) / len(results['with_cache'])
    
    print(f"Average latency without cache: {avg_without:.2f} ms")
    print(f"Average latency with cache: {avg_with:.2f} ms")
    print(f"Improvement: {((avg_without - avg_with) / avg_without * 100):.1f}%")
    
    # Save optimization report
    import json
    report = {
        "optimization": "tile_caching",
        "cache_stats": stats,
        "performance_improvement": f"{((avg_without - avg_with) / avg_without * 100):.1f}%",
        "recommendations": [
            "Increase cache size for larger tile sets",
            "Implement time-based eviction for stale tiles",
            "Add predictive preloading based on usage patterns"
        ]
    }
    
    with open("/tmp/tile_cache_optimization_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\nOptimization report saved to /tmp/tile_cache_optimization_report.json")
    print("\n=== Optimization Complete ===")
    print("Caching implemented and tested. Ready for integration.")
