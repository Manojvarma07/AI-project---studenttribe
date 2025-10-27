# AI-project---studenttribe

🤖 Level 3: Multi-Tool Agent with Human Approval
A Streamlit-powered intelligent agent that executes various tools with mandatory human approval for every action. This ensures complete control and transparency over all tool executions.
✨ Features
🛡️ Human-in-the-Loop System

Every tool requires approval before execution
Edit parameters before execution
Review generated code before running
Cancel operations at any time
Full transparency of tool inputs

🛠️ Available Tools
ToolDescriptionExample Query🐍 Python InterpreterExecute Python code safely with sandboxed environment"factorial of 10", "count dots in ........."🧮 CalculatorEvaluate mathematical expressions"125 * 48", "calculate 15 + 37"🌤️ Weather APIGet real-time weather data for any city"weather in Tokyo"💰 Crypto PricesFetch cryptocurrency prices (24h change)"bitcoin price", "ethereum price"🌍 Country InfoGet country statistics and information"capital of France", "population of India"🕐 Current TimeDisplay current date and time"what time is it?", "today's date"
📋 Prerequisites
Required

Python 3.8+
Groq API Key (Get one here)

Optional

OpenWeatherMap API Key (Get one here)

🚀 Installation
1. Clone or Download
bash# Save the script as app.py
2. Install Dependencies
bashpip install streamlit groq requests wikipedia-api
3. Run the Application
bashstreamlit run app.py
🎯 Quick Start Guide
1. Configure API Keys

Open the app in your browser (usually http://localhost:8501)
Enter your Groq API Key in the sidebar
(Optional) Enter OpenWeatherMap API Key for weather features
Select your preferred Llama model

2. Ask Questions
Simply type natural language queries:
🐍 Python Operations
"count the dots in ............"
"count all characters in this message"
"factorial of 10"
"fibonacci sequence 15"
"prime numbers up to 50"
"is racecar a palindrome"
"reverse hello world"
"even numbers to 30"
"square of 25"
"sum of 5 10 15 20"
🧮 Calculator
"125 * 48"
"calculate 15 + 37 - 8"
"compute 100 / 4"
🌤️ Weather
"weather in London"
"what's the weather like in Mumbai"
💰 Cryptocurrency
"bitcoin price"
"ethereum price"
"how much is cardano"
🌍 Country Information
"capital of Japan"
"population of Brazil"
"tell me about Germany"
3. Approve/Edit Tool Execution

Review the tool and parameters
Edit code or inputs if needed
Click ✅ Approve & Execute or ❌ Cancel

🔧 Python Interpreter Capabilities
Supported Operations
📊 Character Analysis

Count specific characters (dots, commas, spaces)
Count letters, digits, vowels, consonants
Character frequency analysis
Uppercase/lowercase counting

🔢 Mathematical Operations

Factorials: factorial of 5 → 120
Fibonacci: fibonacci sequence 10 → [0, 1, 1, 2, 3, 5, 8...]
Prime Numbers: primes up to 50 → [2, 3, 5, 7, 11...]
Even/Odd: even numbers to 20 → [2, 4, 6, 8...]
Powers: square of 7 → 49, cube of 3 → 27

📝 String Operations

Reverse: reverse hello → "olleh"
Palindrome Check: is racecar palindrome → True
Character transformations

📈 Statistics

Sum, average, mean, median
Maximum, minimum, range
Number analysis

Safety Features

Sandboxed execution with limited built-ins
No file system access
No network operations
No dangerous imports
Safe mathematical operations only

🏗️ Architecture
Workflow
User Query → Query Analysis → Tool Selection → Approval UI → Execution → Display Result
                                    ↓
                            [Edit Parameters]
                                    ↓
                          [✅ Approve / ❌ Cancel]
Key Components

Query Analyzer (analyze_query)

Pattern matching with extensive keyword lists
Automatic parameter extraction
Intelligent tool routing


Tool Functions

python_interpreter(): Safe code execution
calculator(): AST-based math evaluation
get_weather(): OpenWeatherMap API
get_crypto_price(): CoinGecko API
get_country_info(): REST Countries API
get_current_time(): System datetime


Approval System

Parameter display and editing
Session state management
Two-button approval interface



🔒 Security Features
Python Interpreter

Whitelist approach: Only safe built-ins allowed
No imports: Cannot import external modules
Isolated execution: No access to main program scope
Output capture: Redirected stdout

API Safety

Timeout limits (5 seconds)
Error handling for all requests
API key validation
Rate limiting awareness

🎨 Customization
Add New Tools
pythondef my_custom_tool(param1: str) -> str:
    """Your custom tool description."""
    try:
        # Your tool logic
        result = f"Processed: {param1}"
        return result
    except Exception as e:
        return f"Error: {str(e)}"

# Add to analyze_query() function
if 'custom_keyword' in query_lower:
    return {
        "tool": "My Custom Tool",
        "function": my_custom_tool,
        "params": {"param1": "value"},
        "display_params": {"param1": "value"}
    }
Modify Models
Change the model selection in sidebar:
pythonmodel_name = st.selectbox(
    "Select Llama Model",
    ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "llama-3.1-8b-instant"],
    index=0
)
📊 Example Sessions
Session 1: Character Analysis
User: "count all characters in Hello World!"
Agent: [Shows Python code for comprehensive analysis]
User: [Approves]
Result:
  Total characters: 12
  Letters: 10
  Spaces: 1
  Uppercase: 2
  Lowercase: 8
  ...
Session 2: Mathematical Operations
User: "factorial of 5"
Agent: [Shows factorial calculation code]
User: [Approves]
Result:
  5! = 120
  Calculation: 1 × 2 × 3 × 4 × 5 = 120
Session 3: Weather Query
User: "weather in Paris"
Agent: [Shows API call parameters]
User: [Approves]
Result: Weather in Paris: 18°C (feels like 16°C), partly cloudy, Humidity: 65%
