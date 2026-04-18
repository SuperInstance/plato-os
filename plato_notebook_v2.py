#!/usr/bin/env python3
"""
Plato Notebooks Prototype v0.2 - Working with current tiles
"""

import os
import uuid
from datetime import datetime
from typing import Dict, List
import re

class Tile:
    def __init__(self, question, answer, tags=None):
        self.question = question
        self.answer = answer
        self.tags = tags or []
        self.usage_count = 0
        self.tile_id = f"tile_{hash(question) % 10000:04d}"
    
    def __repr__(self):
        return f"Tile({self.tile_id}: {self.question[:30]}...)"

class TilingSubstrate:
    def __init__(self):
        self.tiles: Dict[str, Tile] = {}
        self._load_tiles()
    
    def _load_tiles(self):
        """Load tiles from research files."""
        import glob
        tile_files = glob.glob('/home/lucineer/.openclaw/workspace/research/tile-*.md')
        
        for f in tile_files:
            with open(f, 'r') as fp:
                content = fp.read()
                
                # Extract tile using simple pattern
                q_match = re.search(r'## Question\s*\n(.+?)(?=\n##)', content, re.DOTALL)
                a_match = re.search(r'## Answer\s*\n(.+?)(?=\n##)', content, re.DOTALL)
                tags_match = re.search(r'## Tags\s*\n(.+?)(?=\n##)', content, re.DOTALL)
                
                if q_match and a_match:
                    question = q_match.group(1).strip()
                    answer = a_match.group(1).strip()
                    tags = []
                    if tags_match:
                        tags_text = tags_match.group(1).strip()
                        tags = [t.strip() for t in tags_text.split(',')]
                    
                    tile = Tile(question, answer, tags)
                    self.tiles[tile.tile_id] = tile
        
        print(f"Loaded {len(self.tiles)} tiles with tags")
    
    def retrieve_relevant_tiles(self, query: str, max_tiles: int = 5) -> List[Tile]:
        """Retrieve relevant tiles."""
        query_terms = set(query.lower().split())
        scored = []
        
        for tile in self.tiles.values():
            # Check tags first
            tag_score = 0
            for tag in tile.tags:
                tag_lower = tag.lower()
                if any(term in tag_lower for term in query_terms):
                    tag_score += 0.5
                # Also check if tag contains query as substring
                if any(term in tag_lower for term in query_terms):
                    tag_score += 0.3
            
            # Check content
            content = (tile.question + " " + tile.answer).lower()
            content_terms = set(content.split())
            intersection = len(query_terms.intersection(content_terms))
            union = len(query_terms.union(content_terms))
            similarity = intersection / union if union > 0 else 0
            
            score = similarity + tag_score
            if score > 0:
                scored.append((score, tile))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [tile for _, tile in scored[:max_tiles]]
    
    def tutor_jump(self, anchor: str) -> str:
        """Handle TUTOR_JUMP to anchor."""
        # Try exact tag match first
        for tile in self.tiles.values():
            if anchor.lower() in [t.lower() for t in tile.tags]:
                tile.usage_count += 1
                return f"## Tile: {tile.tile_id}\nQ: {tile.question}\nA: {tile.answer[:500]}..."
        
        # Then try partial match
        relevant = self.retrieve_relevant_tiles(anchor, max_tiles=2)
        if relevant:
            result = f"TUTOR_JUMP to [{anchor}]:\n"
            for tile in relevant:
                tile.usage_count += 1
                result += f"\n## {tile.tile_id}\nQ: {tile.question}\nA: {tile.answer[:300]}...\n"
            return result
        
        return f"No tiles found for anchor [{anchor}]"

class PlatoNotebook:
    """Simplified Plato Notebooks prototype."""
    
    def __init__(self):
        self.substrate = TilingSubstrate()
        self.trace_file = f"traces/notebook-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
        os.makedirs("traces", exist_ok=True)
    
    def _log(self, message: str):
        """Log to trace file."""
        timestamp = datetime.now().isoformat()
        with open(self.trace_file, 'a') as f:
            f.write(f"| {timestamp} | {message} |\n")
    
    def execute_cell(self, content: str) -> str:
        """Execute a notebook cell."""
        self._log(f"Cell executed: {content[:50]}...")
        
        # Extract anchors for TUTOR_JUMP
        anchors = re.findall(r'\[([^\]]+)\]', content)
        
        # Build context from tiles
        relevant_tiles = self.substrate.retrieve_relevant_tiles(content, max_tiles=3)
        
        # Simulate execution
        output = f"Executed cell\n"
        if anchors:
            output += f"Anchors detected: {anchors}\n"
            for anchor in anchors:
                jump_result = self.substrate.tutor_jump(anchor)
                output += f"\nTUTOR_JUMP [{anchor}]:\n{jump_result[:200]}...\n"
        
        output += f"\nContext from {len(relevant_tiles)} tiles:\n"
        for tile in relevant_tiles:
            output += f"- {tile.tile_id}: {tile.question[:60]}...\n"
        
        return output
    
    def constraint_check(self, command: str) -> Dict:
        """Run CONSTRAINT_CHECK."""
        anchors = re.findall(r'\[([^\]]+)\]', command)
        
        violations = []
        unresolved = []
        
        # Security
        forbidden = ['rm -rf', 'sudo', 'chmod 777']
        for term in forbidden:
            if term in command:
                violations.append(f"Forbidden: {term}")
        
        # Anchor resolution
        for anchor in anchors:
            result = self.substrate.tutor_jump(anchor)
            if "No tiles found" in result:
                unresolved.append(anchor)
        
        result = "Allow"
        if violations or unresolved:
            result = "RetryRequired"
        
        return {
            "result": result,
            "violations": violations,
            "unresolved_anchors": unresolved,
            "command": command
        }

# Demo
if __name__ == "__main__":
    print("=== Plato Notebooks Prototype v0.2 ===\n")
    
    plato = PlatoNotebook()
    
    print("=== Tile Network ===")
    print(f"Tiles loaded: {len(plato.substrate.tiles)}")
    for tile_id, tile in plato.substrate.tiles.items():
        print(f"\n{tile_id}: {tile.question[:60]}...")
        if tile.tags:
            print(f"  Tags: {', '.join(tile.tags)}")
    
    print("\n=== TUTOR_JUMP Tests ===")
    test_anchors = ["management", "delegation", "model-routing", "cognitive-styles", "spatial-computing"]
    for anchor in test_anchors:
        print(f"\n[{anchor}]:")
        result = plato.substrate.tutor_jump(anchor)
        print(result[:150] + "..." if len(result) > 150 else result)
    
    print("\n=== Notebook Cell Execution ===")
    cells = [
        "Use [management] and [delegation] to coordinate agents",
        "Apply [spatial-computing] to notebook design",
        "Compare [model-routing] with [cognitive-styles]"
    ]
    
    for i, cell in enumerate(cells):
        print(f"\nCell {i+1}: {cell}")
        output = plato.execute_cell(cell)
        print(f"Output: {output[:200]}...")
    
    print("\n=== CONSTRAINT_CHECK ===")
    commands = [
        "Use [management] for coordination",
        "sudo install package",
        "Apply [non-existent] concept"
    ]
    
    for cmd in commands:
        print(f"\nCommand: {cmd}")
        result = plato.constraint_check(cmd)
        print(f"Result: {result['result']}")
        if result['violations']:
            print(f"Violations: {result['violations']}")
        if result['unresolved_anchors']:
            print(f"Unresolved: {result['unresolved_anchors']}")
    
    print(f"\n=== Trace File ===")
    print(f"Git-auditable trace: {plato.trace_file}")
    if os.path.exists(plato.trace_file):
        with open(plato.trace_file, 'r') as f:
            print(f.read())
    
    print("\n=== Prototype Summary ===")
    print(f"• Tiles: {len(plato.substrate.tiles)} with tags")
    print(f"• TUTOR_JUMP: working with tag-based anchors")
    print(f"• CONSTRAINT_CHECK: security + anchor validation")
    print(f"• Trace: git-auditable markdown")
    print(f"• Ready for integration with plato-tui")
