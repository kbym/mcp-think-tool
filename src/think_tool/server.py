#!/usr/bin/env python3

from typing import Any, Dict, List, Optional
import json
import datetime
import os
import time
from mcp.server.fastmcp import FastMCP

class ThinkToolServer:
    def __init__(self, server_name="think-tool"):
        # Initialize FastMCP server
        self.mcp = FastMCP(server_name)
        
        # Store the thoughts for logging purposes
        self.thoughts_log = []
        
        # Get timezone from environment or system
        self.timezone_name = self.get_system_timezone()
        
        # Register tools
        self.register_tools()
    
    def get_system_timezone(self):
        """Get timezone from environment variable or system default"""
        # First check TZ environment variable
        tz_env = os.environ.get('TZ')
        if tz_env:
            return tz_env
        
        # Try to get system timezone
        # This returns abbreviation like 'JST', 'PST', etc.
        return time.tzname[time.daylight]
    
    def get_local_timestamp(self):
        """Get current timestamp in local timezone with timezone info"""
        now = datetime.datetime.now()
        # Format with timezone abbreviation
        return f"{now.isoformat()} {self.timezone_name}"
    
    def register_tools(self):
        # Register the think tool
        @self.mcp.tool()
        async def think(
            thought: str = "",
            pattern: Optional[str] = None,
            confidence: Optional[float] = None,
            alternatives: Optional[List[str]] = None,
            justification: Optional[str] = None
        ) -> str:
            """Use this tool to think about something. It will not obtain new information or change anything, 
            but just append the thought to the log. Use it when complex reasoning or cache memory is needed.

            Args:
                thought: A thought to think about. This can be structured reasoning, step-by-step analysis,
                        policy verification, or any other mental process that helps with problem-solving.
                pattern: The thinking pattern used (e.g., "analytical", "creative", "critical", "exploratory")
                confidence: Confidence level in this thought (0.0 to 1.0)
                alternatives: List of alternative thoughts or approaches considered
                justification: Reasoning or evidence supporting this thought
            """
            # Log the thought with a timestamp in local timezone
            timestamp = self.get_local_timestamp()
            thought_entry = {
                "timestamp": timestamp,
                "thought": thought
            }
            
            # Add optional structured parameters if provided
            if pattern is not None:
                thought_entry["pattern"] = pattern
            if confidence is not None:
                thought_entry["confidence"] = confidence
            if alternatives is not None:
                thought_entry["alternatives"] = alternatives
            if justification is not None:
                thought_entry["justification"] = justification
            
            self.thoughts_log.append(thought_entry)
            
            # Return a confirmation with structured info
            confirmation = f"Thought recorded: {thought[:100]}..."
            if pattern:
                confirmation += f" [Pattern: {pattern}]"
            if confidence is not None:
                confirmation += f" [Confidence: {confidence:.2f}]"
            
            return confirmation

        @self.mcp.tool()
        async def get_thoughts() -> str:
            """Retrieve all thoughts recorded in the current session.
            
            This tool helps review the thinking process that has occurred so far.
            """
            if not self.thoughts_log:
                return "No thoughts have been recorded yet."
            
            formatted_thoughts = []
            for i, entry in enumerate(self.thoughts_log, 1):
                # Basic thought info
                thought_str = f"Thought #{i} ({entry['timestamp']}):"
                
                # Add pattern and confidence if present
                metadata = []
                if "pattern" in entry:
                    metadata.append(f"Pattern: {entry['pattern']}")
                if "confidence" in entry:
                    metadata.append(f"Confidence: {entry['confidence']:.2f}")
                
                if metadata:
                    thought_str += f" [{', '.join(metadata)}]"
                
                thought_str += f"\n{entry['thought']}"
                
                # Add justification if present
                if "justification" in entry:
                    thought_str += f"\nJustification: {entry['justification']}"
                
                # Add alternatives if present
                if "alternatives" in entry and entry['alternatives']:
                    thought_str += f"\nAlternatives considered: {', '.join(entry['alternatives'])}"
                
                thought_str += "\n"
                formatted_thoughts.append(thought_str)
            
            return "\n".join(formatted_thoughts)

        @self.mcp.tool()
        async def clear_thoughts() -> str:
            """Clear all recorded thoughts from the current session.
            
            Use this to start fresh if the thinking process needs to be reset.
            """
            count = len(self.thoughts_log)
            self.thoughts_log = []
            return f"Cleared {count} recorded thoughts."

        @self.mcp.tool()
        async def get_thought_stats() -> str:
            """Get statistics about the thoughts recorded in the current session."""
            if not self.thoughts_log:
                return "No thoughts have been recorded yet."
            
            total_thoughts = len(self.thoughts_log)
            avg_length = sum(len(entry["thought"]) for entry in self.thoughts_log) / total_thoughts if total_thoughts else 0
            longest_thought = max((len(entry["thought"]), i) for i, entry in enumerate(self.thoughts_log)) if self.thoughts_log else (0, -1)
            
            # Pattern statistics
            pattern_counts = {}
            confidence_values = []
            thoughts_with_justification = 0
            thoughts_with_alternatives = 0
            
            for entry in self.thoughts_log:
                if "pattern" in entry:
                    pattern = entry["pattern"]
                    pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
                
                if "confidence" in entry:
                    confidence_values.append(entry["confidence"])
                
                if "justification" in entry:
                    thoughts_with_justification += 1
                
                if "alternatives" in entry and entry["alternatives"]:
                    thoughts_with_alternatives += 1
            
            stats = {
                "total_thoughts": total_thoughts,
                "average_length": round(avg_length, 2),
                "longest_thought_index": longest_thought[1] + 1 if longest_thought[1] >= 0 else None,
                "longest_thought_length": longest_thought[0] if longest_thought[0] > 0 else None,
                "pattern_distribution": pattern_counts,
                "average_confidence": round(sum(confidence_values) / len(confidence_values), 2) if confidence_values else None,
                "thoughts_with_justification": thoughts_with_justification,
                "thoughts_with_alternatives": thoughts_with_alternatives
            }
            
            return json.dumps(stats, indent=2)
    
    def run(self, transport='stdio'):
        """Run the server with the specified transport"""
        print(f"Starting Think Tool MCP Server with {transport} transport...")
        print(f"Using timezone: {self.timezone_name}")
        print(f"Current time: {self.get_local_timestamp()}")
        self.mcp.run(transport=transport)


def main():
    server = ThinkToolServer()
    server.run()


if __name__ == "__main__":
    main()