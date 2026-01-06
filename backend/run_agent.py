#!/usr/bin/env python3
"""
FD Agent System - Interactive Runner
=====================================
This script provides an interactive CLI to use the AI agent system
for analyzing codebases and handling change requests.
"""

import asyncio
import os
import sys
import json
from datetime import datetime
from typing import Optional

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.orchestrator import AgentOrchestrator


class AgentCLI:
    """Interactive CLI for the FD Agent System"""
    
    def __init__(self):
        self.orchestrator: Optional[AgentOrchestrator] = None
        self.project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.analyzed = False
        
    async def initialize(self):
        """Initialize the agent orchestrator"""
        print("\n🚀 Initializing FD Agent System...")
        self.orchestrator = AgentOrchestrator()
        await self.orchestrator.initialize()
        print("✅ Agent system initialized successfully!\n")
        
    async def analyze_codebase(self, path: Optional[str] = None):
        """Analyze the codebase"""
        target_path = path or self.project_path
        
        print(f"\n📂 Analyzing codebase at: {target_path}")
        print("   This may take a moment...\n")
        
        try:
            results = await self.orchestrator.analyze_codebase(target_path)
            
            print("=" * 60)
            print("📊 CODEBASE ANALYSIS RESULTS")
            print("=" * 60)
            
            print("\n🎯 Flutter Analysis:")
            flutter = results.get('flutter', {})
            print(f"   • Widgets found:    {flutter.get('widgets', 0)}")
            print(f"   • BLoC patterns:    {flutter.get('blocs', 0)}")
            print(f"   • API calls:        {flutter.get('api_calls', 0)}")
            print(f"   • Routes:           {flutter.get('routes', 0)}")
            
            print("\n🐍 Python Analysis:")
            python = results.get('python', {})
            print(f"   • API endpoints:    {python.get('endpoints', 0)}")
            print(f"   • Pydantic models:  {python.get('models', 0)}")
            print(f"   • Services:         {python.get('services', 0)}")
            print(f"   • Validators:       {python.get('validators', 0)}")
            
            print("\n💾 Memory Stats:")
            memory = results.get('memory_stats', {})
            print(f"   • Entities stored:  {memory.get('total_entities', 'N/A')}")
            print(f"   • Relationships:    {memory.get('total_relationships', 'N/A')}")
            
            print("=" * 60)
            
            self.analyzed = True
            return results
            
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def handle_change_request(self, description: str):
        """Handle a change request"""
        print(f"\n📝 Processing Change Request:")
        print(f"   \"{description}\"")
        print("   Processing...\n")
        
        try:
            result = await self.orchestrator.handle_change_request(description)
            
            print("=" * 60)
            print("📋 CHANGE REQUEST ANALYSIS")
            print("=" * 60)
            
            print(f"\n🆔 CR ID: {result.get('cr_id', 'N/A')}")
            print(f"⏰ Timestamp: {result.get('timestamp', 'N/A')}")
            
            cr_result = result.get('result', {})
            analysis = cr_result.get('analysis', {})
            
            print(f"\n🔍 Analysis:")
            print(f"   • Pattern identified: {analysis.get('pattern', 'N/A')}")
            print(f"   • Confidence: {analysis.get('confidence', 0):.0%}")
            print(f"   • Keywords matched: {', '.join(analysis.get('keywords', []))}")
            
            # Affected components
            affected = cr_result.get('affected_components', {})
            if affected:
                print(f"\n📁 Affected Components:")
                for component_type, components in affected.items():
                    print(f"   {component_type}:")
                    for comp in components[:3]:  # Show first 3
                        if isinstance(comp, dict):
                            print(f"      - {comp.get('name', comp.get('file', 'Unknown'))}")
                        else:
                            print(f"      - {comp}")
            
            # Implementation suggestions
            impl = cr_result.get('implementation', {})
            if impl:
                print(f"\n💡 Implementation Suggestions:")
                
                flutter_changes = impl.get('flutter_changes', {})
                if flutter_changes:
                    print(f"   Flutter changes:")
                    for change_type, changes in list(flutter_changes.items())[:2]:
                        print(f"      • {change_type}: {len(changes) if isinstance(changes, list) else 1} items")
                
                python_changes = impl.get('python_changes', {})
                if python_changes:
                    print(f"   Python changes:")
                    for change_type, changes in list(python_changes.items())[:2]:
                        print(f"      • {change_type}: {len(changes) if isinstance(changes, list) else 1} items")
            
            # Effort estimate
            effort = cr_result.get('estimated_effort', {})
            if effort:
                print(f"\n⏱️  Estimated Effort:")
                print(f"   • Complexity: {effort.get('complexity', 'N/A')}")
                print(f"   • Total days: {effort.get('total_days', 'N/A')}")
                print(f"   • Frontend: {effort.get('frontend_days', 'N/A')} days")
                print(f"   • Backend: {effort.get('backend_days', 'N/A')} days")
            
            # Test scenarios
            tests = cr_result.get('test_scenarios', [])
            if tests:
                print(f"\n🧪 Test Scenarios: ({len(tests)} total)")
                for test in tests[:3]:
                    if isinstance(test, dict):
                        print(f"   • {test.get('name', test.get('scenario', 'Test'))}")
                    else:
                        print(f"   • {test}")
            
            # Compliance
            compliance = cr_result.get('compliance_considerations', [])
            if compliance:
                print(f"\n⚖️  Compliance Considerations:")
                for item in compliance[:3]:
                    print(f"   • {item}")
            
            print("=" * 60)
            
            return result
            
        except Exception as e:
            print(f"❌ Error processing CR: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def search_context(self, query: str, context_type: str = 'all'):
        """Search for relevant context"""
        print(f"\n🔍 Searching for: \"{query}\"")
        print(f"   Context type: {context_type}\n")
        
        try:
            results = await self.orchestrator.get_context_for_query(query, context_type)
            
            print("=" * 60)
            print("🔎 SEARCH RESULTS")
            print("=" * 60)
            
            for key, items in results.items():
                if items:
                    print(f"\n📌 {key}:")
                    for item in items[:3]:
                        if isinstance(item, dict):
                            print(f"   • {item.get('file_path', item.get('name', 'Unknown'))}")
                        else:
                            print(f"   • {item}")
            
            print("=" * 60)
            return results
            
        except Exception as e:
            print(f"❌ Error searching: {e}")
            return None

    def print_help(self):
        """Print help information"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║             FD AGENT SYSTEM - INTERACTIVE CLI                ║
╠══════════════════════════════════════════════════════════════╣
║  Commands:                                                    ║
║                                                               ║
║  analyze [path]  - Analyze codebase (default: current project)║
║  cr <description> - Process a change request                  ║
║  search <query>   - Search for relevant context               ║
║  help            - Show this help message                     ║
║  quit/exit       - Exit the CLI                               ║
║                                                               ║
║  Example CRs:                                                 ║
║  • "Add UPI AutoPay mandate feature for recurring payments"   ║
║  • "Implement biometric authentication with fingerprint"      ║
║  • "Add offline Aadhaar KYC verification"                     ║
║  • "Implement transaction limits based on KYC level"          ║
║  • "Add annual tax statement generation feature"              ║
╚══════════════════════════════════════════════════════════════╝
""")

    async def run_interactive(self):
        """Run interactive CLI mode"""
        await self.initialize()
        self.print_help()
        
        while True:
            try:
                user_input = input("\n🤖 Agent> ").strip()
                
                if not user_input:
                    continue
                    
                parts = user_input.split(maxsplit=1)
                command = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""
                
                if command in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                    
                elif command == 'help':
                    self.print_help()
                    
                elif command == 'analyze':
                    path = args if args else None
                    await self.analyze_codebase(path)
                    
                elif command == 'cr':
                    if not args:
                        print("❌ Please provide a CR description. Example:")
                        print("   cr Add UPI AutoPay mandate feature")
                    else:
                        await self.handle_change_request(args)
                        
                elif command == 'search':
                    if not args:
                        print("❌ Please provide a search query. Example:")
                        print("   search UPI payment validation")
                    else:
                        await self.search_context(args)
                        
                else:
                    print(f"❓ Unknown command: {command}")
                    print("   Type 'help' for available commands")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except EOFError:
                print("\n\n👋 Goodbye!")
                break


async def demo_mode():
    """Run a quick demo of the agent capabilities"""
    print("\n" + "=" * 60)
    print("   FD AGENT SYSTEM - DEMO MODE")
    print("=" * 60)
    
    cli = AgentCLI()
    await cli.initialize()
    
    # Demo 1: Analyze codebase
    print("\n📌 DEMO 1: Analyzing the FD Agent codebase...\n")
    await cli.analyze_codebase()
    
    # Demo 2: Process a sample CR
    print("\n📌 DEMO 2: Processing a sample Change Request...\n")
    await cli.handle_change_request(
        "Add UPI AutoPay mandate feature for recurring payments with merchant registration"
    )
    
    print("\n✅ Demo complete! Run with --interactive for full CLI experience.")


async def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--demo':
            await demo_mode()
        elif sys.argv[1] == '--interactive' or sys.argv[1] == '-i':
            cli = AgentCLI()
            await cli.run_interactive()
        elif sys.argv[1] == '--analyze':
            cli = AgentCLI()
            await cli.initialize()
            path = sys.argv[2] if len(sys.argv) > 2 else None
            await cli.analyze_codebase(path)
        elif sys.argv[1] == '--cr':
            if len(sys.argv) < 3:
                print("❌ Please provide a CR description")
                print("   Usage: python run_agent.py --cr 'Add feature X'")
                sys.exit(1)
            cli = AgentCLI()
            await cli.initialize()
            await cli.handle_change_request(' '.join(sys.argv[2:]))
        elif sys.argv[1] == '--feature-graph':
            cli = AgentCLI()
            await cli.initialize()
            path = sys.argv[2] if len(sys.argv) > 2 else None
            graph = await cli.orchestrator.build_feature_graph(path or cli.project_path)  # type: ignore
            print(json.dumps(graph, indent=2))
        elif sys.argv[1] == '--gap-report':
            cli = AgentCLI()
            await cli.initialize()
            path = sys.argv[2] if len(sys.argv) > 2 else None
            report = await cli.orchestrator.generate_gap_report(path or cli.project_path)  # type: ignore
            print(json.dumps(report, indent=2))
        elif sys.argv[1] in ['--help', '-h']:
            print("""
FD Agent System - Command Line Interface

Usage:
  python run_agent.py [options]

Options:
  --demo           Run a quick demo
  --interactive    Start interactive CLI mode
  -i               Same as --interactive
  --analyze [path] Analyze a codebase
    --feature-graph [path] Build and persist feature graph (read-only)
    --gap-report [path] Generate API/contract gap report (read-only)
  --cr <desc>      Process a change request
  --help, -h       Show this help

Examples:
  python run_agent.py --demo
  python run_agent.py --interactive
  python run_agent.py --analyze /path/to/project
    python run_agent.py --feature-graph /path/to/project
    python run_agent.py --gap-report /path/to/project
  python run_agent.py --cr "Add UPI AutoPay feature"
""")
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help for usage information")
    else:
        # Default: run demo
        await demo_mode()


if __name__ == "__main__":
    asyncio.run(main())
