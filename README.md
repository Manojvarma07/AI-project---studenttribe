Multi-Tool Agent with Human Approval
A Streamlit-powered intelligent agent that executes various tools with mandatory human approval for every action.

Features
Human-in-the-Loop System

Every tool requires approval before execution
Edit parameters before running
Review generated code
Cancel operations anytime
Full transparency

Available Tools
Python Interpreter - Execute Python code safely

Examples: "factorial of 10", "count dots in ..........."

Calculator - Evaluate math expressions

Examples: "125 * 48", "calculate 15 + 37"

Weather API - Get real-time weather data

Examples: "weather in Tokyo"

Crypto Prices - Fetch cryptocurrency prices

Examples: "bitcoin price", "ethereum price"

Country Info - Get country statistics

Examples: "capital of France", "population of India"

Current Time - Display current date and time

Examples: "what time is it?", "today's date"


Installation
Step 1: Install Dependencies
bashpip install streamlit groq requests wikipedia-api
Step 2: Run the Application
bashstreamlit run app.py

Quick Start
1. Configure API Keys

Enter your Groq API Key in the sidebar
Optionally enter OpenWeatherMap API Key for weather features
Select your preferred Llama model

2. Try These Queries
Python Operations
count the dots in ............
count all characters in this message
factorial of 10
fibonacci sequence 15
prime numbers up to 50
is racecar a palindrome
reverse hello world
even numbers to 30
square of 25
sum of 5 10 15 20
Calculator
125 * 48
calculate 15 + 37 - 8
compute 100 / 4
Weather
weather in London
what's the weather like in Mumbai
Cryptocurrency
bitcoin price
ethereum price
how much is cardano
Country Information
capital of Japan
population of Brazil
tell me about Germany
3. Approve or Cancel

Review the tool and parameters
Edit code or inputs if needed
Click "Approve & Execute" or "Cancel"


Python Interpreter Capabilities
Character Analysis

Count specific characters (dots, commas, spaces)
Count letters, digits, vowels, consonants
Character frequency analysis
Uppercase/lowercase counting

Mathematical Operations

Factorials: factorial of 5 → 120
Fibonacci: fibonacci sequence 10 → [0, 1, 1, 2, 3, 5, 8...]
Prime Numbers: primes up to 50 → [2, 3, 5, 7, 11...]
Even/Odd: even numbers to 20 → [2, 4, 6, 8...]
Powers: square of 7 → 49, cube of 3 → 27

String Operations

Reverse: reverse hello → "olleh"
Palindrome Check: is racecar palindrome → True
Character transformations

Statistics

Sum, average, mean, median
Maximum, minimum, range
Number analysis


Security Features
Python Interpreter Security

Sandboxed execution with limited built-ins
No file system access
No network operations
No dangerous imports
Safe mathematical operations only

API Safety

Timeout limits (5 seconds)
Error handling for all requests
API key validation


How to Add Custom Tools
pythondef my_custom_tool(param1: str) -> str:
    """Your custom tool description."""
    try:
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

Example Sessions
Example 1: Character Analysis
User: count all characters in Hello World!

Agent shows Python code for analysis

User approves

Result:
Total characters: 12
Letters: 10
Spaces: 1
Uppercase: 2
Lowercase: 8
Example 2: Mathematical Operations
User: factorial of 5

Agent shows factorial calculation code

User approves

Result:
5! = 120
Calculation: 1 × 2 × 3 × 4 × 5 = 120
Example 3: Weather Query
User: weather in Paris

Agent shows API call parameters

User approves

Result:
Weather in Paris: 18°C (feels like 16°C), partly cloudy, Humidity: 65%
