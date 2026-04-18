#!/usr/bin/env python3
"""
Integration of tiling substrate with plato-os-si I2I hub.
Replaces simple TUTOR_JUMP logging with actual tile retrieval.
"""

import sys
sys.path.insert(0, '/tmp')

from tiling_substrate import TilingSubstrate
from tutor_jump_integration import TutorJumpEngine
import json

class EnhancedI2IHub:
    """I2I hub with tiling substrate integration."""
    
    def __init__(self):
        self.substrate = TilingSubstrate()
        self.tutor = TutorJumpEngine(self.substrate)
        
        # Load tiles from our research
        import glob
        tile_files = glob.glob('/home/lucineer/.openclaw/workspace/research/tile-*.md')
        for f in tile_files:
            with open(f, 'r') as fp:
                tiles = self.substrate.extract_tiles_from_markdown(fp.read())
                for tile in tiles:
                    self.substrate.add_tile(tile)
        
        self.tutor.auto_register_anchors()
        print(f"Enhanced I2I Hub initialized with {len(self.substrate.tiles)} tiles, {len(self.tutor.word_anchors)} word anchors")
    
    async def handle_constraint_check(self, header, payload, writer):
        """Enhanced constraint check with tile anchor validation."""
        user_input = payload.get('command', '')
        print(f"Running enhanced audit for: {user_input}")
        
        violations = []
        
        # 1. Basic security checks (original)
        forbidden = ['rm -rf', 'sudo', 'chmod 777', ':(){:|:&};']
        for term in forbidden:
            if term in user_input:
                violations.append(f"Forbidden command sequence: {term}")
        
        # 2. Tile anchor validation (new)
        import re
        anchors = re.findall(r'\[([^\]]+)\]', user_input)
        unresolved_anchors = []
        
        for anchor in anchors:
            result = self.tutor.handle_tutor_jump(anchor)
            if result.startswith("No tile found"):
                unresolved_anchors.append(anchor)
        
        if unresolved_anchors:
            violations.append(f"Unresolved tile anchors: {unresolved_anchors}")
        
        # Determine result
        result = "Allow"
        if violations:
            result = "RetryRequired"
        
        # Build context from relevant tiles if allowed
        context = ""
        if result == "Allow":
            relevant_tiles = self.substrate.retrieve_relevant_tiles(user_input, max_tiles=3)
            context_parts = []
            for tile in relevant_tiles:
                context_parts.append(f"Tile {tile.tile_id}: {tile.question[:100]}...")
            context = "\n".join(context_parts)
        
        # Send response
        response = {
            "result": result,
            "violations": violations,
            "original_command": user_input,
            "context_preview": context[:500] if context else "",
            "tiles_considered": len(relevant_tiles) if result == "Allow" else 0
        }
        
        # In real implementation, send via writer
        print(f"Enhanced audit complete: {result}")
        print(f"Violations: {violations}")
        if context:
            print(f"Context preview: {context[:200]}...")
        
        return response
    
    async def handle_tutor_jump(self, header, payload):
        """Enhanced TUTOR_JUMP with actual tile retrieval."""
        anchor = payload.get('anchor', '')
        print(f"Processing enhanced TUTOR_JUMP to anchor: [{anchor}]")
        
        # Retrieve tile content
        tile_content = self.tutor.handle_tutor_jump(anchor)
        
        # Build response
        response = {
            "anchor": anchor,
            "tile_content": tile_content,
            "tile_found": not tile_content.startswith("No tile found"),
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"TUTOR_JUMP result: {'Found' if response['tile_found'] else 'Not found'}")
        if response['tile_found']:
            print(f"Content preview: {tile_content[:200]}...")
        
        return response
    
    def inject_tutor_jump(self, anchor: str):
        """Manual inject with tile retrieval."""
        print(f"Manual enhanced inject: TUTOR_JUMP to [{anchor}]")
        tile_content = self.tutor.handle_tutor_jump(anchor)
        
        if tile_content.startswith("No tile found"):
            print(f"Result: No tile found for [{anchor}]")
            # Fallback: search similar
            similar = self.substrate.retrieve_relevant_tiles(anchor, max_tiles=3)
            if similar:
                print(f"Similar tiles found:")
                for tile in similar:
                    print(f"  - {tile.tile_id}: {tile.question[:80]}...")
        else:
            print(f"Tile found: {tile_content[:300]}...")
        
        return tile_content
    
    def run_audit(self, command: str):
        """Manual audit with tile validation."""
        print(f"Manual enhanced audit of: {command}")
        
        # Simulate async call
        import asyncio
        from datetime import datetime
        
        class MockHeader:
            def get(self, key, default):
                return default
        
        class MockWriter:
            async def drain(self):
                pass
        
        # Run constraint check
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        header = MockHeader()
        payload = {"command": command}
        writer = MockWriter()
        
        response = loop.run_until_complete(
            self.handle_constraint_check(header, payload, writer)
        )
        
        print(f"\nEnhanced CONSTRAINT_RESULT:")
        print(f"Result: {response['result']}")
        print(f"Violations: {response['violations']}")
        if response.get('context_preview'):
            print(f"Context preview: {response['context_preview']}")
        
        return response

if __name__ == "__main__":
    from datetime import datetime
    
    hub = EnhancedI2IHub()
    
    print("\n=== Testing Enhanced I2I Hub ===")
    
    # Test 1: Manual TUTOR_JUMP
    print("\n1. Manual TUTOR_JUMP [manager-pattern]:")
    content = hub.inject_tutor_jump("manager-pattern")
    print(f"Result length: {len(content)} chars")
    
    # Test 2: Manual audit
    print("\n2. Manual audit of command with anchors:")
    test_command = "Use [manager-pattern] with [immune-system] for coordination"
    hub.run_audit(test_command)
    
    # Test 3: Audit with forbidden command
    print("\n3. Manual audit with forbidden command:")
    hub.run_audit("sudo rm -rf /")
    
    print("\n=== Hub Ready ===")
    print(f"Total tiles: {len(hub.substrate.tiles)}")
    print(f"Total word anchors: {len(hub.tutor.word_anchors)}")
    print("Sample anchors:", list(hub.tutor.word_anchors.keys())[:5])
