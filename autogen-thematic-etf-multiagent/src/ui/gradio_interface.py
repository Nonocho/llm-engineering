"""
Gradio Web Interface for Thematic ETF Advisor
Multi-agent AI system with interactive web UI

Based on AutoGen and Gradio concepts from Dr. Ryan Ahmed's LLM Engineering course
"""

import gradio as gr
import autogen
import sys
import io
import time
import threading
from typing import List, Tuple, Dict, Any, Optional
from ..agents import AgentFactory
from ..config import config_manager


class ThematicETFAdvisorUI:
    """Gradio interface for multi-agent thematic ETF advisory system"""

    def __init__(self):
        """Initialize the UI and agent system"""
        self.factory = AgentFactory()
        self.agents = None
        self.groupchat = None
        self.manager = None
        self.chat_history = []
        self.current_messages = []
        self.is_processing = False
        self.stop_requested = False
        self.total_messages = 0
        self.start_time = None

    def initialize_agents(self) -> str:
        """Initialize all AI agents"""
        try:
            # Create all agents
            self.agents = self.factory.create_all_agents(
                include_user_proxy=False  # No user proxy needed for Gradio
            )

            # Create GroupChat with custom speaker selection
            agent_list = [
                self.agents["cio"],
                self.agents["portfolio_analyst"],
                self.agents["market_research"],
                self.agents["marketing_strategist"],
            ]

            # Define speaker selection function
            def custom_speaker_selection(last_speaker, groupchat):
                """Select next speaker based on conversation flow"""
                messages = groupchat.messages

                # If no messages yet or just user message, start with CIO for strategy
                if len(messages) <= 1:
                    return self.agents["cio"]

                # After CIO, go to Portfolio Analyst for analysis
                if last_speaker == self.agents["cio"]:
                    return self.agents["portfolio_analyst"]

                # After Portfolio Analyst, can go to Market Research or terminate
                if last_speaker == self.agents["portfolio_analyst"]:
                    return None  # End conversation

                return None  # Default: end conversation

            self.groupchat = autogen.GroupChat(
                agents=agent_list,
                messages=[],
                max_round=6,  # Short demo conversations - 1-2 agents respond
                speaker_selection_method=custom_speaker_selection,  # Use custom function
                allow_repeat_speaker=False,  # Prevent same agent speaking twice in a row
            )

            # Create GroupChatManager with Claude config
            claude_config = config_manager.get_claude_config(temperature=0.3)
            self.manager = autogen.GroupChatManager(
                groupchat=self.groupchat,
                llm_config=claude_config,
            )

            return "✅ Agent team initialized successfully!\n\n**Team Members:**\n- Chief Investment Officer (Claude)\n- Portfolio Analyst (Claude)\n- Market Research Specialist (Claude)\n- Marketing Strategist (Claude)"

        except Exception as e:
            return f"❌ Error initializing agents: {str(e)}\n\nPlease check your .env file and API keys."

    def reset_conversation(self) -> Tuple[str, List]:
        """Reset the conversation and clear history"""
        if self.agents:
            self.factory.reset_all_agents()

        if self.groupchat:
            self.groupchat.messages = []

        self.chat_history = []
        return "🔄 Conversation reset. Ready for new discussion.", None

    def process_message_streaming(
        self,
        user_message: str,
        history: List[Dict[str, str]]
    ):
        """
        Process user message with real-time streaming updates
        Generator function that yields updates as they happen
        """
        if not self.agents or not self.manager:
            error_msg = "⚠️ Please initialize agents first using the 'Initialize Agent Team' button."
            if history is None:
                history = []
            history.append({"role": "user", "content": user_message})
            history.append({"role": "assistant", "content": error_msg})
            yield history, ""
            return

        try:
            # Initialize history if None
            if history is None:
                history = []

            # Add user message to history
            history.append({"role": "user", "content": user_message})
            history.append({"role": "assistant", "content": "🚀 **Starting agent collaboration...**\n\n"})
            yield history, ""

            self.is_processing = True
            self.stop_requested = False
            self.current_messages = []
            self.start_time = time.time()

            # Create a temporary user proxy to send the message
            user_proxy = autogen.UserProxyAgent(
                name="User",
                human_input_mode="NEVER",
                max_consecutive_auto_reply=0,
                code_execution_config=False,
            )

            # Reset groupchat messages if this is a new conversation
            if len(self.groupchat.messages) == 0:
                self.groupchat.agents.insert(0, user_proxy)

            # Store initial message count
            initial_msg_count = len(self.groupchat.messages)

            # Start agent chat in a separate thread
            def run_chat():
                try:
                    user_proxy.initiate_chat(
                        self.manager,
                        message=user_message,
                        clear_history=False,
                    )
                except Exception as e:
                    self.current_messages.append(("ERROR", str(e)))
                finally:
                    self.is_processing = False

            chat_thread = threading.Thread(target=run_chat, daemon=True)
            chat_thread.start()

            # Poll for new messages and yield updates
            last_msg_count = initial_msg_count
            response_parts = []
            last_speaker = None

            while self.is_processing or len(self.groupchat.messages) > last_msg_count:
                if self.stop_requested:
                    history[-1] = {"role": "assistant", "content": "⚠️ **Conversation stopped by user**\n\n" + "\n\n---\n\n".join(response_parts)}
                    yield history, ""
                    break

                # Check for new messages
                current_msg_count = len(self.groupchat.messages)

                if current_msg_count > last_msg_count:
                    # Process new messages
                    for msg in self.groupchat.messages[last_msg_count:]:
                        # Skip ONLY the User proxy messages (not agent messages)
                        if msg.get("name") == "User":
                            continue

                        # Get agent name and content
                        agent_name = msg.get("name", "Agent")
                        content = msg.get("content", "")

                        if content:
                            # Remove TERMINATE keyword from display (but keep the rest)
                            display_content = content.replace("TERMINATE", "").strip()

                            if display_content:  # Only add if there's content after removing TERMINATE
                                # Format the response with agent name
                                self.total_messages += 1
                                elapsed_time = time.time() - self.start_time
                                last_speaker = agent_name
                                response_parts.append(f"**{agent_name}:**\n\n{display_content}")

                                # Update the display
                                current_response = "\n\n---\n\n".join(response_parts)
                                if self.is_processing:
                                    current_response += f"\n\n⏳ *{agent_name} just responded. Waiting for next agent... ({self.total_messages} messages, {elapsed_time:.1f}s)*"

                                history[-1] = {"role": "assistant", "content": current_response}
                                yield history, ""

                    last_msg_count = current_msg_count
                elif self.is_processing and last_speaker:
                    # Show waiting status with last speaker
                    elapsed_time = time.time() - self.start_time
                    current_response = "\n\n---\n\n".join(response_parts) if response_parts else ""
                    if current_response:
                        current_response += f"\n\n⏳ *Waiting for next agent to respond... ({elapsed_time:.1f}s)*"
                    else:
                        current_response = f"⏳ *Agents are thinking... ({elapsed_time:.1f}s)*"

                    history[-1] = {"role": "assistant", "content": current_response}
                    yield history, ""

                time.sleep(0.5)  # Poll every 0.5 seconds

            # Final update
            if response_parts:
                elapsed_time = time.time() - self.start_time
                final_response = "\n\n---\n\n".join(response_parts)
                final_response += f"\n\n---\n\n✅ **Collaboration complete!** ({self.total_messages} messages in {elapsed_time:.1f}s)"
            else:
                final_response = "❌ No response from agents. Please check console for errors."

            history[-1] = {"role": "assistant", "content": final_response}
            yield history, ""

            # Reset counter
            self.total_messages = 0

            # Remove user proxy from groupchat for next round
            if user_proxy in self.groupchat.agents:
                self.groupchat.agents.remove(user_proxy)

        except Exception as e:
            import traceback
            error_response = f"❌ **Error:** {str(e)}\n\n```\n{traceback.format_exc()}\n```"
            history[-1] = {"role": "assistant", "content": error_response}
            yield history, ""
        finally:
            self.is_processing = False

    def stop_conversation(self) -> str:
        """Stop the current conversation"""
        self.stop_requested = True
        return "⚠️ Stop requested. Waiting for current agent to finish..."

    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface"""

        # Use Gradio's built-in Soft theme with professional colors
        theme = gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="slate",
            neutral_hue="slate",
            font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
        ).set(
            body_background_fill="*neutral_50",
            button_primary_background_fill="*primary_600",
            button_primary_background_fill_hover="*primary_700",
        )

        with gr.Blocks(title="AI ETF Advisor", theme=theme) as interface:

            # Header
            with gr.Row():
                with gr.Column():
                    gr.Markdown(
                        """
                        # 🤖 AI ETF Advisor
                        ### Multi-Agent Analysis System for AI & Technology ETFs
                        """,
                        elem_id="header"
                    )

            gr.Markdown("---")

            # Status display
            status_display = gr.Markdown("", visible=False)

            # Main chat area
            with gr.Row():
                with gr.Column(scale=1):
                    chatbot = gr.Chatbot(
                        height=550,
                        label="💬 Agent Collaboration",
                        show_label=True,
                        container=True,
                    )

            # Input section
            with gr.Row():
                with gr.Column(scale=9):
                    msg_input = gr.Textbox(
                        placeholder="💡 Ask about AI & technology ETFs... (e.g., 'Analyze top 3 AI ETFs')",
                        label="Your Question",
                        show_label=False,
                        lines=2,
                        max_lines=4,
                    )
                with gr.Column(scale=1, min_width=100):
                    submit_btn = gr.Button("🚀 Send", variant="primary", size="lg")

            # Control panel
            gr.Markdown("---")
            with gr.Row():
                with gr.Column():
                    gr.Markdown("**🎛️ Controls**")
                    with gr.Row():
                        init_btn = gr.Button("⚡ Initialize Agents", variant="secondary", size="sm")
                        clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary", size="sm")
                        stop_btn = gr.Button("⛔ Stop", variant="stop", size="sm", visible=False)

            # Info section
            with gr.Accordion("ℹ️ About this System", open=False):
                gr.Markdown(
                    """
                    **Agent Team:**
                    - 🎯 **Chief Investment Officer** - Strategic direction and investment philosophy
                    - 📊 **Portfolio Analyst** - Quantitative analysis and performance metrics
                    - 🔍 **Market Research Specialist** - Industry trends and competitive intelligence
                    - 📢 **Marketing Strategist** - Client communication and positioning

                    **How to use:**
                    1. Click "Initialize Agents" to start the system
                    2. Ask questions about AI & Technology ETFs
                    3. Watch the agents collaborate in real-time

                    *Powered by Claude (Anthropic) via AutoGen framework*
                    """
                )

            # Status updates
            with gr.Row():
                status_display = gr.Markdown("", visible=True)

            # Event handlers
            init_btn.click(
                fn=self.initialize_agents,
                outputs=status_display,
            )

            submit_btn.click(
                fn=self.process_message_streaming,
                inputs=[msg_input, chatbot],
                outputs=[chatbot, msg_input],
            )

            msg_input.submit(
                fn=self.process_message_streaming,
                inputs=[msg_input, chatbot],
                outputs=[chatbot, msg_input],
            )

            stop_btn.click(
                fn=self.stop_conversation,
                outputs=status_display,
            )

            clear_btn.click(
                fn=self.reset_conversation,
                outputs=[status_display, chatbot],
            )

        return interface


def launch_app(share: bool = False, server_port: int = 7860):
    """
    Launch the Gradio application

    Args:
        share: Whether to create public share link
        server_port: Port to run the server on
    """
    app = ThematicETFAdvisorUI()
    interface = app.create_interface()

    try:
        print("🚀 Launching Thematic ETF Advisor...")
        print("📊 Multi-Agent AI Team for Technology Investment Analysis")
        print("=" * 60)
    except UnicodeEncodeError:
        print("Launching Thematic ETF Advisor...")
        print("Multi-Agent AI Team for Technology Investment Analysis")
        print("=" * 60)

    interface.launch(
        share=share,
        server_port=server_port,
        show_error=True,
    )


if __name__ == "__main__":
    launch_app()
