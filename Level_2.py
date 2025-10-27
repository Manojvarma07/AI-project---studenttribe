import streamlit as st
from groq import Groq
import requests
from datetime import datetime
import re
import wikipedia

# Page configuration
st.set_page_config(page_title="Multi-Tool Agent", page_icon="🤖", layout="wide")

# Sidebar for API Keys
with st.sidebar:
    st.title("⚙️ Configuration")
    groq_api_key = st.text_input("Groq API Key", type="password")
    weather_api_key = st.text_input("OpenWeatherMap API Key (Optional)", type="password")
    
    # Model selection
    model_name = st.selectbox(
        "Select Llama Model",
        ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
        index=0
    )
    
    st.divider()
    st.markdown("### 🛠️ Available Tools")
    st.markdown("""
    - 🐍 **Python Interpreter**
    - 🧮 Calculator
    - 🌤️ Weather
    - 📚 Wikipedia
    - 💰 Crypto Prices
    - 🌍 Country Info
    - 🕐 Current Time
    """)
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Tool Functions
def python_interpreter(code: str) -> str:
    """Execute Python code safely."""
    try:
        import io
        import sys
        
        # Whitelist safe built-ins
        safe_builtins = {
            'print': print, 'range': range, 'len': len, 'sum': sum,
            'max': max, 'min': min, 'abs': abs, 'round': round,
            'sorted': sorted, 'list': list, 'dict': dict, 'set': set,
            'str': str, 'int': int, 'float': float, 'bool': bool,
            'enumerate': enumerate, 'zip': zip, 'map': map, 'filter': filter,
        }
        
        # Capture output
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        
        # Execute with restricted environment
        exec(code, {"__builtins__": safe_builtins}, {})
        
        output = buffer.getvalue()
        sys.stdout = old_stdout
        
        return output if output else "Code executed successfully (no output)"
        
    except Exception as e:
        import sys
        sys.stdout = old_stdout
        return f"Error: {str(e)}"

def calculator(expression: str) -> str:
    """Evaluate mathematical expressions."""
    try:
        import ast
        import operator
        
        ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
        }
        
        def eval_expr(node):
            if isinstance(node, ast.Num):
                return node.n
            elif isinstance(node, ast.Constant):
                return node.value
            elif isinstance(node, ast.BinOp):
                return ops[type(node.op)](eval_expr(node.left), eval_expr(node.right))
            elif isinstance(node, ast.UnaryOp):
                return ops[type(node.op)](eval_expr(node.operand))
            else:
                raise TypeError(node)
        
        result = eval_expr(ast.parse(expression, mode='eval').body)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"

def get_weather(city: str) -> str:
    """Get current weather for a city."""
    if not weather_api_key:
        return "Weather API key not configured."
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if response.status_code == 200:
            temp = data['main']['temp']
            desc = data['weather'][0]['description']
            humidity = data['main']['humidity']
            feels_like = data['main']['feels_like']
            return f"Weather in {city}: {temp}°C (feels like {feels_like}°C), {desc}, Humidity: {humidity}%"
        else:
            return f"Error: {data.get('message', 'Unknown error')}"
    except Exception as e:
        return f"Error: {str(e)}"

def get_crypto_price(crypto: str) -> str:
    """Get cryptocurrency price."""
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto.lower()}&vs_currencies=usd&include_24hr_change=true"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if crypto.lower() in data:
            price = data[crypto.lower()]['usd']
            change = data[crypto.lower()].get('usd_24h_change', 0)
            change_symbol = "📈" if change > 0 else "📉"
            return f"{crypto.capitalize()}: ${price:,.2f} USD {change_symbol} ({change:.2f}% 24h)"
        else:
            return f"'{crypto}' not found. Try: bitcoin, ethereum, cardano, solana"
    except Exception as e:
        return f"Error: {str(e)}"

def get_country_info(country: str) -> str:
    """Get country information."""
    try:
        url = f"https://restcountries.com/v3.1/name/{country}"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if response.status_code == 200 and len(data) > 0:
            c = data[0]
            name = c['name']['common']
            capital = c.get('capital', ['N/A'])[0]
            population = c.get('population', 'N/A')
            region = c.get('region', 'N/A')
            area = c.get('area', 'N/A')
            return f"{name}: Capital - {capital}, Population - {population:,}, Region - {region}, Area - {area:,} km²"
        else:
            return f"Could not find '{country}'"
    except Exception as e:
        return f"Error: {str(e)}"

def get_current_time() -> str:
    """Get current date and time."""
    current = datetime.now()
    return f"Current: {current.strftime('%A, %B %d, %Y at %H:%M:%S')}"

def search_wikipedia(query: str) -> str:
    """Search Wikipedia."""
    try:
        result = wikipedia.summary(query, sentences=3)
        return result
    except Exception as e:
        return f"Error: {str(e)}"

def process_query(query: str, client, model_name) -> str:
    """Process user query and route to appropriate tool."""
    query_lower = query.lower()
    
    # Check for Python code execution requests
    python_keywords = ['python code', 'write python', 'execute python', 'factorial', 'fibonacci', 'python script', 'for loop', 'while loop']
    if any(kw in query_lower for kw in python_keywords):
        # Check for factorial
        if 'factorial' in query_lower:
            # Extract number if specified
            match = re.search(r'factorial of (\d+)', query_lower)
            n = match.group(1) if match else '10'
            code = f"""
n = {n}
result = 1
for i in range(1, n + 1):
    result *= i
print(f"Factorial of {{n}} is {{result}}")
"""
            return python_interpreter(code)
        
        # Check for fibonacci
        elif 'fibonacci' in query_lower:
            match = re.search(r'(\d+)', query_lower)
            n = match.group(1) if match else '10'
            code = f"""
def fibonacci(n):
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib

result = fibonacci({n})
print(f"First {n} Fibonacci numbers: {{result}}")
"""
            return python_interpreter(code)
        
        # Check for even numbers
        elif 'even' in query_lower and 'numbers' in query_lower:
            code = """
even_numbers = [i for i in range(1, 21) if i % 2 == 0]
print(f"Even numbers from 1 to 20: {even_numbers}")
"""
            return python_interpreter(code)
    
    # Check for calculator requests
    calc_patterns = [r'\d+\s*[\+\-\*\/\^]\s*\d+', r'calculate', r'compute', r'what is \d+']
    if any(re.search(pattern, query_lower) for pattern in calc_patterns):
        match = re.search(r'(\d+\s*[\+\-\*\/\^]\s*\d+)', query)
        if match:
            return calculator(match.group(1))
    
    # Check for weather
    if 'weather' in query_lower:
        words = query.split()
        for i, word in enumerate(words):
            if word.lower() == 'in' and i + 1 < len(words):
                city = ' '.join(words[i+1:]).strip('?.!')
                return get_weather(city)
    
    # Check for crypto
    crypto_keywords = ['bitcoin', 'ethereum', 'crypto', 'btc', 'eth', 'price of']
    if any(kw in query_lower for kw in crypto_keywords):
        for crypto in ['bitcoin', 'ethereum', 'cardano', 'solana', 'dogecoin']:
            if crypto in query_lower:
                return get_crypto_price(crypto)
    
    # Check for country info
    if 'country' in query_lower or 'capital of' in query_lower or 'population of' in query_lower:
        words = query.replace('?', '').replace('.', '').split()
        if 'of' in words:
            idx = words.index('of')
            if idx + 1 < len(words):
                country = ' '.join(words[idx+1:])
                return get_country_info(country)
    
    # Check for time
    if 'time' in query_lower or 'date' in query_lower:
        return get_current_time()
    
    # Check for Wikipedia
    wiki_keywords = ['who is', 'what is', 'tell me about', 'wikipedia', 'information about']
    if any(kw in query_lower for kw in wiki_keywords):
        return search_wikipedia(query)
    
    # Default: Use LLM
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": query}],
            temperature=0.7,
            max_tokens=1024
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    st.title("🤖 Multi-Tool Agent with Python Interpreter")
    st.markdown("*Powered by Groq with 7 Powerful Tools*")
    
    # Check API key
    if not groq_api_key:
        st.warning("⚠️ Please enter your Groq API key in the sidebar!")
        st.info("""
        💡 **How to get Groq API Key:**
        1. Visit: [https://console.groq.com](https://console.groq.com)
        2. Sign up for free
        3. Create API key
        
        **Try asking:**
        - "Calculate factorial of 10 using Python"
        - "Generate fibonacci sequence of 15 numbers"
        - "What's 125 * 48?"
        - "Weather in Tokyo"
        - "Bitcoin price"
        - "Who is Albert Einstein?"
        - "What time is it?"
        """)
        return
    
    # Initialize Groq client
    try:
        client = Groq(api_key=groq_api_key)
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                try:
                    response = process_query(prompt, client, model_name)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

if __name__ == "__main__":
    main()
