# 📚 Course Attribution

This project is built using concepts, methodologies, and design patterns from:

## Dr. Ryan Ahmed's LLM Engineering Course

**Course Title:** *Building Interactive Multi-Model AI Agent Teams with AutoGen*

**Instructor:** Dr. Ryan Ahmed

**LinkedIn:** [www.linkedin.com/in/dr-ryan-ahmed](https://www.linkedin.com/in/dr-ryan-ahmed)

---

## Concepts Applied from the Course

### 1. Multi-Agent Architecture with AutoGen

The project implements the AutoGen framework concepts taught in the course:
- `ConversableAgent` for creating specialized AI agents
- `GroupChat` for orchestrating multi-agent conversations
- `GroupChatManager` for managing conversation flow
- `UserProxyAgent` pattern for human-in-the-loop interactions

**Reference:** Course Module on "AUTOGEN 101" and "CREATE AN AI AGENT"

### 2. Multi-Model AI Systems

Following the course's demonstration of using different LLMs for different roles:
- Google Gemini for strategic planning (Chief Investment Officer)
- OpenAI GPT for analytical work (Portfolio Analyst, Market Research)
- Anthropic Claude for creative content (Marketing Strategist)

**Reference:** Course Module on "CONFIGURE MULTI-MODEL AGENTS IN AUTOGEN"

### 3. LLM Configuration Management

Configuration patterns learned from the course:
```python
config_list = [{
    "model": "model-name",
    "api_key": api_key,
    "api_type": "provider"
}]

llm_config = {
    "config_list": config_list,
    "temperature": 0.7,
    "timeout": 120,
}
```

**Reference:** Course sections on LLM configuration for OpenAI, Gemini, and Claude

### 4. System Message Design

Agent personality and role definition using system messages:
- Defining agent expertise and responsibilities
- Setting communication styles
- Establishing agent collaboration patterns

**Reference:** Course examples of CMO, Brand Marketer, and Social Media Strategist prompts

### 5. Human-in-the-Loop (HIL) Patterns

Adaptation of the course's HIL concepts:
- Original: Terminal-based `UserProxyAgent` with `human_input_mode="ALWAYS"`
- This project: Web-based Gradio interface for better UX

**Reference:** Course Module on "ADDING HUMAN GUIDANCE (USER PROXY AGENT)"

### 6. Gradio Integration

Using Gradio for web interfaces as demonstrated in the course:
- Interactive chat interfaces
- Real-time agent conversation display
- User-friendly controls and status updates

**Reference:** Course usage of Gradio for UI development

---

## Key Learning Outcomes Applied

1. ✅ **Multi-Agent Collaboration**: Agents working together toward common goals
2. ✅ **Role Specialization**: Each agent has distinct expertise and communication style
3. ✅ **Model Selection**: Choosing appropriate LLMs for specific tasks
4. ✅ **Configuration Management**: Clean separation of LLM configs
5. ✅ **Conversation Management**: Using GroupChat for coordinated discussions
6. ✅ **Best Practices**: Professional Python project structure

---

## Adaptation to Asset Management Domain

While the course used a **sustainable shoe brand marketing** use case, this project adapts the concepts to **thematic ETF analysis and marketing**:

| Course Example | This Project |
|----------------|--------------|
| Sustainable Shoe Brand | Thematic Equity ETFs |
| Chief Marketing Officer | Chief Investment Officer |
| Brand Marketer | Portfolio Analyst |
| Social Media Strategist | Market Research Specialist |
| (Optional) | Marketing Strategist |
| Marketing Campaigns | Investment Analysis & Marketing |

---

## Original Course Structure Referenced

The course notebook structure that informed this project:

1. **TASK 1**: Project Overview - From Agents to Interactive Teams
2. **TASK 2**: AutoGen 101
3. **TASK 3**: Create an AI Agent with Similar LLM
4. **TASK 4**: Test AI Agents Conversation
5. **TASK 5**: Configure Multi-Model Agents (Gemini + GPT)
6. **TASK 6**: Trigger AI Agents Conversation (Multi-Model Team)
7. **TASK 7**: Adding Human Guidance & Leveraging GroupChat

---

## Enhancements Beyond Course Material

This project extends the course concepts with:

1. **Production-Ready Structure**
   - Modular package architecture
   - Configuration management system
   - Factory pattern for agent creation

2. **Domain Expertise**
   - Financial services and asset management context
   - Thematic investing focus (AI & Technology)
   - Compliance-aware marketing considerations

3. **Enhanced UI**
   - Polished Gradio interface
   - Status indicators and initialization flow
   - Sample prompts and documentation

4. **Professional Documentation**
   - Comprehensive README
   - Clear setup instructions
   - Usage examples and customization guides

5. **Development Best Practices**
   - Type hints throughout
   - Error handling and validation
   - Environment variable management
   - Git workflow setup

---

## Gratitude

Thank you to **Dr. Ryan Ahmed** for creating an excellent, hands-on course that makes advanced AI concepts accessible and practical. The multi-agent system patterns learned in this course are directly applicable to real-world applications across many domains.

---

## Developer

**Arnaud Demes, CFA**

This project was developed as part of continuous learning in AI/ML applications for financial services.

---

## Educational Use

This project serves as a portfolio demonstration of:
- Completion of Dr. Ryan Ahmed's LLM Engineering course
- Understanding of AutoGen multi-agent framework
- Ability to adapt concepts to new domains (financial services)
- Professional software engineering practices
- Multi-model AI system design

**Course students and learners** are encouraged to explore this project as an example of applying the course concepts to a different vertical.

---

*Last Updated: January 2025*
