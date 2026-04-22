"""LangGraph-based ReAct agent for AI Tax Buddy."""

import logging
from typing import Annotated, TypedDict, Sequence
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from aitaxbuddy.config import settings
from aitaxbuddy.observability import observability
from aitaxbuddy.memory import TaxBuddyMemory
from aitaxbuddy.guardrails import guardrails
from aitaxbuddy.prompts import SYSTEM_PROMPT, USER_CONTEXT_TEMPLATE
from aitaxbuddy.tools import (
    calculate_tax_bracket,
    calculate_medicare_levy,
    query_ato_guidelines,
    validate_deduction,
)

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State for the agent graph."""
    
    messages: Annotated[Sequence[BaseMessage], "The messages in the conversation"]
    iterations: Annotated[int, "Number of iterations (for loop prevention)"]
    user_id: Annotated[str, "User identifier for memory"]


class TaxBuddyAgent:
    """The main AI Tax Buddy agent using LangGraph."""
    
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.memory = TaxBuddyMemory(user_id)
        self.llm = self._initialize_llm()
        self.tools = self._get_tools()
        self.graph = self._build_graph()
    
    def _initialize_llm(self):
        """Initialize the LLM based on configuration."""
        if settings.model_provider == "openai":
            return ChatOpenAI(
                model=settings.model_name,
                temperature=settings.temperature,
                api_key=settings.openai_api_key,
            )
        elif settings.model_provider == "anthropic":
            return ChatAnthropic(
                model=settings.model_name,
                temperature=settings.temperature,
                api_key=settings.anthropic_api_key,
            )
        else:
            raise ValueError(f"Unsupported model provider: {settings.model_provider}")
    
    def _get_tools(self):
        """Get the list of tools available to the agent."""
        # Wrap the tools with @tool decorator for LangChain
        @tool
        def calculate_tax(income: float) -> dict:
            """
            Calculate Australian tax bracket and tax payable for a given income.
            
            Args:
                income: Annual taxable income in AUD
            
            Returns:
                Dictionary with tax calculation details
            """
            result = calculate_tax_bracket(income)
            return result.model_dump()
        
        @tool
        def calculate_levy(income: float, is_single: bool = True, num_dependents: int = 0) -> dict:
            """
            Calculate Medicare levy for a given income.
            
            Args:
                income: Annual income in AUD
                is_single: Whether taxpayer is single
                num_dependents: Number of dependent children
            
            Returns:
                Dictionary with Medicare levy calculation
            """
            result = calculate_medicare_levy(income, is_single, num_dependents)
            return result.model_dump()
        
        @tool
        def query_ato(topic: str) -> dict:
            """
            Query ATO guidelines for general tax information.
            
            Args:
                topic: Tax topic (work_related_expenses, home_office, crypto, side_hustle, rental_property)
            
            Returns:
                Dictionary with ATO guideline information
            """
            result = query_ato_guidelines(topic)
            return result.model_dump()
        
        @tool
        def validate_deduction_claim(
            deduction_type: str, description: str, amount: float | None = None
        ) -> dict:
            """
            Validate a proposed tax deduction and assess audit risk.
            
            Args:
                deduction_type: Type of deduction (car, home_office, clothing, etc.)
                description: Description of the expense
                amount: Optional claim amount in AUD
            
            Returns:
                Dictionary with validation result and risk assessment
            """
            result = validate_deduction(deduction_type, description, amount)
            return result.model_dump()
        
        return [calculate_tax, calculate_levy, query_ato, validate_deduction_claim]
    
    def _build_graph(self):
        """Build the LangGraph state machine."""
        
        def agent_node(state: AgentState) -> AgentState:
            """The agent reasoning node."""
            messages = state["messages"]
            iterations = state.get("iterations", 0)
            
            # Check max iterations
            if iterations >= settings.max_iterations:
                logger.warning("Max iterations reached, forcing end")
                return {
                    **state,
                    "messages": messages
                    + [
                        AIMessage(
                            content="I've reached my reasoning limit. Could you rephrase your question or break it into smaller parts?"
                        )
                    ],
                }
            
            # Bind tools to LLM
            llm_with_tools = self.llm.bind_tools(self.tools)
            
            # Get memory context
            last_message = messages[-1] if messages else None
            if last_message and isinstance(last_message, HumanMessage):
                memory_context = self.memory.get_context(last_message.content)
            else:
                memory_context = self.memory.get_context()
            
            # Prepare messages with system prompt
            system_message = AIMessage(content=SYSTEM_PROMPT)
            
            # Add memory context if available
            if memory_context and "No previous context" not in memory_context:
                context_message = AIMessage(content=f"\n\n{memory_context}\n\n")
                messages_with_context = [system_message, context_message] + list(messages)
            else:
                messages_with_context = [system_message] + list(messages)
            
            # Call LLM
            response = llm_with_tools.invoke(messages_with_context)
            
            return {
                **state,
                "messages": messages + [response],
                "iterations": iterations + 1,
            }
        
        def should_continue(state: AgentState) -> str:
            """Determine if we should continue to tools or end."""
            messages = state["messages"]
            last_message = messages[-1]
            
            # If there are tool calls, continue to tools
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                return "tools"
            
            # Otherwise end
            return "end"
        
        # Build the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("agent", agent_node)
        workflow.add_node("tools", ToolNode(self.tools))
        
        # Add edges
        workflow.set_entry_point("agent")
        workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", "end": END})
        workflow.add_edge("tools", "agent")
        
        return workflow.compile()
    
    def process_message(self, user_message: str) -> str:
        """
        Process a user message and return the agent's response.
        
        Args:
            user_message: The user's input message
        
        Returns:
            The agent's response
        """
        # Apply guardrails to user input
        if settings.enable_content_guardrails:
            guardrail_result = guardrails.check_and_filter(user_message, context="user")
            
            if not guardrail_result.allowed:
                violation = guardrail_result.violations[0] if guardrail_result.violations else "unknown"
                return guardrails.get_prohibition_response(violation)
            
            # Use filtered content
            filtered_message = guardrail_result.modified_content
            
            if guardrail_result.warnings:
                logger.info(f"PII filtered: {guardrail_result.warnings}")
        else:
            filtered_message = user_message
        
        # Create initial state
        initial_state = {
            "messages": [HumanMessage(content=filtered_message)],
            "iterations": 0,
            "user_id": self.user_id,
        }
        
        # Run the graph
        final_state = self.graph.invoke(initial_state)
        
        # Extract final response
        final_message = final_state["messages"][-1]
        response = final_message.content if hasattr(final_message, "content") else str(final_message)
        
        # Add disclaimer
        if settings.enable_content_guardrails:
            response = guardrails.add_disclaimer(response)
        
        # Store in memory
        conversation = [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": response},
        ]
        self.memory.add_conversation(conversation)
        
        return response
    
    def chat(self) -> None:
        """Start an interactive chat session."""
        from rich.console import Console
        from rich.panel import Panel
        from rich.markdown import Markdown
        from rich.prompt import Prompt
        from rich import box
        
        console = Console()
        
        # Welcome banner
        console.print()
        console.print(Panel.fit(
            "[bold cyan]🇦🇺 AI Tax Buddy[/bold cyan]\n\n"
            "[dim]Australian Tax Guidance Agent[/dim]\n"
            "[yellow]⚠️  General Advice Only[/yellow]",
            border_style="cyan",
            box=box.DOUBLE
        ))
        console.print()
        console.print("[dim]Ask me about Australian tax rules, deductions, and obligations.[/dim]")
        console.print("[dim]Type [bold]'exit'[/bold], [bold]'quit'[/bold], or [bold]'bye'[/bold] to end the conversation.[/dim]")
        console.print()
        
        while True:
            try:
                # Get user input with styled prompt
                user_input = Prompt.ask("\n[bold green]You[/bold green]").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
                    console.print()
                    console.print(Panel(
                        "[bold cyan]Thanks for chatting![/bold cyan]\n\n"
                        "[dim]Remember to lodge by October 31! 🇦🇺[/dim]",
                        border_style="cyan",
                        box=box.ROUNDED
                    ))
                    console.print()
                    break
                
                # Show thinking indicator
                with console.status("[bold cyan]Tax Buddy is thinking...[/bold cyan]", spinner="dots"):
                    response = self.process_message(user_input)
                
                # Display response in a styled panel
                console.print()
                console.print(Panel(
                    Markdown(response),
                    title="[bold cyan]💼 Tax Buddy[/bold cyan]",
                    border_style="cyan",
                    box=box.ROUNDED,
                    padding=(1, 2)
                ))
                
            except KeyboardInterrupt:
                console.print("\n")
                console.print(Panel(
                    "[bold cyan]Session ended[/bold cyan]\n[dim]Goodbye![/dim]",
                    border_style="cyan"
                ))
                console.print()
                break
            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)
                console.print()
                console.print(Panel(
                    "[bold red]⚠️  Error[/bold red]\n\n"
                    "[dim]Sorry, I encountered an error. Please try again.[/dim]",
                    border_style="red",
                    box=box.ROUNDED
                ))
                console.print()


def create_agent(user_id: str = "default") -> TaxBuddyAgent:
    """
    Create a new TaxBuddyAgent instance.
    
    Args:
        user_id: User identifier for memory
    
    Returns:
        TaxBuddyAgent instance
    """
    return TaxBuddyAgent(user_id=user_id)
