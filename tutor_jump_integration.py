from typing import List, Dict, Optional
#!/usr/bin/env python3
"""
TUTOR_JUMP integration with tiling substrate.
Simulates plato-tui's TUTOR_JUMP verb for context jumps to word anchors.
"""

import re
from tiling_substrate import TilingSubstrate, Tile

class TutorJumpEngine:
    """Handles TUTOR_JUMP requests for word anchor context jumps."""
    
    def __init__(self, substrate: TilingSubstrate):
        self.substrate = substrate
        self.word_anchors = {}  # anchor -> tile_id mapping
    
    def register_word_anchor(self, anchor: str, tile_id: str):
        """Register a word anchor [like_this] to point to a tile."""
        self.word_anchors[anchor.lower()] = tile_id
    
    def extract_anchors_from_text(self, text: str) -> List[str]:
        """Extract word anchors from text: [like_this] patterns."""
        return re.findall(r'\[([^\]]+)\]', text)
    
    def handle_tutor_jump(self, anchor: str) -> str:
        """Handle TUTOR_JUMP request for a word anchor."""
        anchor = anchor.lower()
        
        # Check if anchor registered
        if anchor in self.word_anchors:
            tile_id = self.word_anchors[anchor]
            tile = self.substrate.tiles.get(tile_id)
            if tile:
                return tile.answer
        
        # Fallback: search tiles for anchor in tags or content
        for tile in self.substrate.tiles.values():
            if (anchor in tile.tags or 
                anchor in tile.question.lower() or 
                anchor in tile.answer.lower()):
                return tile.answer
        
        return f"No tile found for anchor [{anchor}]"
    
    def auto_register_anchors(self):
        """Auto-register word anchors from tile tags and content."""
        for tile_id, tile in self.substrate.tiles.items():
            # Register tags as anchors
            for tag in tile.tags:
                self.register_word_anchor(tag, tile_id)
            
            # Extract anchors from question/answer
            for anchor in self.extract_anchors_from_text(tile.question):
                self.register_word_anchor(anchor, tile_id)
            for anchor in self.extract_anchors_from_text(tile.answer):
                self.register_word_anchor(anchor, tile_id)

# Example integration with I2I protocol
class I2ISimulator:
    """Simulates I2I/1.0 protocol messages."""
    
    def __init__(self, tutor_engine: TutorJumpEngine):
        self.tutor_engine = tutor_engine
    
    def handle_i2i_message(self, verb: str, target: str, payload: dict) -> dict:
        """Handle I2I message, return response."""
        if verb == "TUTOR_JUMP":
            anchor = payload.get("anchor", "")
            context = self.tutor_engine.handle_tutor_jump(anchor)
            return {
                "verb": "TUTOR_JUMP_RESPONSE",
                "anchor": anchor,
                "context": context,
                "tiles_used": 1
            }
        elif verb == "CONSTRAINT_CHECK":
            command = payload.get("command", "")
            # Simple constraint: must contain valid anchor if brackets present
            anchors = self.tutor_engine.extract_anchors_from_text(command)
            valid = all(self.tutor_engine.handle_tutor_jump(a) != f"No tile found for anchor [{a}]" 
                       for a in anchors)
            return {
                "verb": "CONSTRAINT_RESULT",
                "command": command,
                "result": "Allow" if valid else "RetryRequired",
                "message": "All anchors resolved" if valid else "Some anchors not found"
            }
        else:
            return {"verb": "ERROR", "message": f"Unknown verb: {verb}"}

if __name__ == "__main__":
    # Setup
    substrate = TilingSubstrate()
    tutor = TutorJumpEngine(substrate)
    i2i = I2ISimulator(tutor)
    
    # Load some tiles
    import glob
    for research_file in glob.glob("/home/lucineer/.openclaw/workspace/research/tile-*.md"):
        with open(research_file, "r") as f:
            tiles = substrate.extract_tiles_from_markdown(f.read())
            for tile in tiles:
                substrate.add_tile(tile)
    
    print(f"Loaded {len(substrate.tiles)} tiles")
    
    # Auto-register anchors
    tutor.auto_register_anchors()
    print(f"Registered {len(tutor.word_anchors)} word anchors")
    
    # Test TUTOR_JUMP
    test_anchor = "manager-pattern"
    response = i2i.handle_i2i_message("TUTOR_JUMP", "kernel-alpha", {"anchor": test_anchor})
    print(f"\nTUTOR_JUMP [{test_anchor}]:")
    print(f"Response: {response['verb']}")
    print(f"Context (first 200 chars): {response['context'][:200]}...")
    
    # Test CONSTRAINT_CHECK
    test_command = "Use the [manager-pattern] to coordinate [poly-model-ideation]"
    constraint = i2i.handle_i2i_message("CONSTRAINT_CHECK", "kernel-alpha", {"command": test_command})
    print(f"\nCONSTRAINT_CHECK: {test_command}")
    print(f"Result: {constraint['result']} - {constraint['message']}")
    
    # Test failed constraint
    bad_command = "Use [non-existent-anchor] for coordination"
    bad_constraint = i2i.handle_i2i_message("CONSTRAINT_CHECK", "kernel-alpha", {"command": bad_command})
    print(f"\nCONSTRAINT_CHECK (bad): {bad_command}")
    print(f"Result: {bad_constraint['result']} - {bad_constraint['message']}")
