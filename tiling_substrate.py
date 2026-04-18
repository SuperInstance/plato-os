#!/usr/bin/env python3
"""
Minimal tiling substrate for Plato Notebooks.
Implements 60% token reduction by splitting context into semantic tiles.
Based on FM's description of plato-kernel tiling substrate.
"""

import re
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import hashlib

@dataclass
class Tile:
    """A semantic tile - question/answer pair with metadata."""
    question: str
    answer: str
    confidence: float = 1.0
    tags: List[str] = field(default_factory=list)
    usage_count: int = 0
    tile_id: str = field(default_factory=lambda: hashlib.md5().hexdigest()[:8])
    
    def to_markdown(self) -> str:
        """Convert tile to markdown format for storage."""
        return f"""# Tile: {self.tile_id}

## Question
{self.question}

## Answer
{self.answer}

## Metadata
- Confidence: {self.confidence:.2f}
- Usage: {self.usage_count}
- Tags: {', '.join(self.tags)}
"""

@dataclass  
class TilingSubstrate:
    """Splits context into tiles, retrieves only relevant ones."""
    tiles: Dict[str, Tile] = field(default_factory=dict)
    
    def add_tile(self, tile: Tile) -> str:
        """Add a tile to the substrate."""
        self.tiles[tile.tile_id] = tile
        return tile.tile_id
    
    def extract_tiles_from_markdown(self, markdown: str) -> List[Tile]:
        """Extract tile candidates from markdown text."""
        # Simple pattern: ## Question / ## Answer sections
        tiles = []
        pattern = r'## Question\s*\n(.+?)\n\s*## Answer\s*\n(.+?)(?=\n## |\Z)'
        
        for match in re.finditer(pattern, markdown, re.DOTALL | re.IGNORECASE):
            question = match.group(1).strip()
            answer = match.group(2).strip()
            
            # Filter: min length, not just headers
            if len(question) > 30 and len(answer) > 30:
                tile = Tile(
                    question=question,
                    answer=answer,
                    tags=self._extract_tags(question + answer)
                )
                tiles.append(tile)
        
        return tiles
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extract potential tags from text."""
        tags = []
        # Look for bracketed terms [like this]
        tags.extend(re.findall(r'\[([^\]]+)\]', text))
        # Look for hashtags
        tags.extend(re.findall(r'#(\w+)', text))
        return list(set(tags))[:5]
    
    def retrieve_relevant_tiles(self, query: str, max_tiles: int = 5) -> List[Tile]:
        """Retrieve tiles relevant to query (simple keyword matching)."""
        query_terms = set(query.lower().split())
        
        scored = []
        for tile in self.tiles.values():
            # Simple relevance scoring
            tile_text = (tile.question + " " + tile.answer).lower()
            tile_terms = set(tile_text.split())
            
            # Jaccard similarity
            intersection = len(query_terms.intersection(tile_terms))
            union = len(query_terms.union(tile_terms))
            similarity = intersection / union if union > 0 else 0
            
            # Boost by confidence and usage
            score = similarity * tile.confidence * (1 + 0.1 * min(tile.usage_count, 10))
            
            if score > 0:
                scored.append((score, tile))
        
        # Sort by score, return top N
        scored.sort(key=lambda x: x[0], reverse=True)
        return [tile for _, tile in scored[:max_tiles]]
    
    def build_context(self, query: str, max_tokens: int = 2000) -> str:
        """Build context from relevant tiles for a query."""
        relevant = self.retrieve_relevant_tiles(query)
        
        context_parts = []
        token_count = 0
        
        for tile in relevant:
            tile_text = tile.to_markdown()
            tile_tokens = len(tile_text.split())  # Rough estimate
            
            if token_count + tile_tokens > max_tokens:
                break
            
            context_parts.append(tile_text)
            token_count += tile_tokens
            tile.usage_count += 1  # Track usage
        
        return "\n\n".join(context_parts)
    
    def estimate_token_reduction(self, full_context: str, tiled_context: str) -> float:
        """Estimate token reduction percentage."""
        full_tokens = len(full_context.split())
        tiled_tokens = len(tiled_context.split())
        
        if full_tokens == 0:
            return 0.0
        
        reduction = 1.0 - (tiled_tokens / full_tokens)
        return reduction * 100  # percentage

# Example usage
if __name__ == "__main__":
    substrate = TilingSubstrate()
    
    # Load some example tiles from our research
    with open("/home/lucineer/.openclaw/workspace/research/tile-the-manager-pattern.md", "r") as f:
        markdown = f.read()
        tiles = substrate.extract_tiles_from_markdown(markdown)
        for tile in tiles:
            substrate.add_tile(tile)
    
    print(f"Loaded {len(substrate.tiles)} tiles")
    
    # Test retrieval
    query = "How should I choose which model to use for coordination?"
    context = substrate.build_context(query)
    
    print(f"\nQuery: {query}")
    print(f"Context built from {len(context.split())} tokens")
    print(f"First 500 chars of context:\n{context[:500]}...")
    
    # Estimate reduction
    full_context = markdown  # Using the whole file as "full context"
    reduction = substrate.estimate_token_reduction(full_context, context)
    print(f"\nEstimated token reduction: {reduction:.1f}%")
