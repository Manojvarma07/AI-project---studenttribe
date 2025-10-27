import streamlit as st
from groq import Groq
import requests
from datetime import datetime
import re
import wikipedia


# Page configuration
st.set_page_config(page_title="Multi-Tool Agent with Approval", page_icon="🤖", layout="wide")


# Sidebar for API Keys
with st.sidebar:
    st.title("⚙️ Configuration")
    
    groq_api_key = st.text_input("Groq API Key", type="password")
    weather_api_key = st.text_input("OpenWeatherMap API Key (Optional)", type="password")
    
    # Model selection
    model_name = st.selectbox(
        "Select Llama Model",
        ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "llama-3.1-8b-instant"],
        index=0
    )
    
    st.divider()
    st.markdown("### 🛠️ Available Tools")
    st.markdown("""
    - 🐍 **Python Interpreter** ✅
    - 🧮 **Calculator** ✅
    - 🌤️ **Weather** ✅
    - 💰 **Crypto Prices** ✅
    - 🌍 **Country Info** ✅
    """)
    
    st.info("💡 **Every tool requires approval!**")
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.session_state.pending_approval = None
        st.rerun()


# Tool Functions
def python_interpreter(code: str) -> str:
    """Execute Python code safely."""
    try:
        import io
        import sys
        
        safe_builtins = {
            'print': print, 'range': range, 'len': len, 'sum': sum,
            'max': max, 'min': min, 'abs': abs, 'round': round,
            'sorted': sorted, 'list': list, 'dict': dict, 'set': set,
            'str': str, 'int': int, 'float': float, 'bool': bool,
            'enumerate': enumerate, 'zip': zip, 'map': map, 'filter': filter,
        }
        
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        
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
        import operator as op
        
        ops = {
            ast.Add: op.add,
            ast.Sub: op.sub,
            ast.Mult: op.mul,
            ast.Div: op.truediv,
            ast.Pow: op.pow,
            ast.USub: op.neg,
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


def analyze_query(query: str) -> dict:
    """Analyze query and determine which tool to use."""
    query_lower = query.lower()
    
    # ============ MASSIVE PYTHON KEYWORDS LIST ============
    python_keywords = [
        # General Python
        'python', 'code', 'script', 'program', 'execute', 'run', 'compile',
        'coding', 'programming', 'write code', 'run code',
        
        # Common algorithms
        'factorial', 'fibonacci', 'prime', 'palindrome', 'armstrong',
        'perfect number', 'lcm', 'gcd', 'hcf',
        
        # Math operations
        'square', 'cube', 'power', 'root', 'sqrt', 'exponent',
        'sum', 'average', 'mean', 'median', 'mode', 'total',
        'multiply', 'divide', 'add', 'subtract',
        
        # Number operations
        'even', 'odd', 'positive', 'negative', 'natural', 'whole',
        'factor', 'multiple', 'divisor', 'remainder', 'modulo',
        
        # Sequences
        'sequence', 'series', 'pattern', 'generate', 'create',
        
        # Counting & Finding
        'count', 'how many', 'number of', 'total of', 'find',
        'search', 'locate', 'detect', 'identify',
        
        # String operations
        'string', 'text', 'character', 'char', 'letter', 'word',
        'sentence', 'reverse', 'uppercase', 'lowercase', 'capitalize',
        'replace', 'remove', 'extract', 'parse',
        
        # Special characters
        'dot', 'dots', 'period', 'comma', 'semicolon', 'colon',
        'space', 'digit', 'number', 'symbol', 'special character',
        
        # Data structures
        'list', 'array', 'dictionary', 'dict', 'tuple', 'set',
        'collection', 'data structure',
        
        # Control flow
        'loop', 'for loop', 'while loop', 'if', 'else', 'elif',
        'condition', 'iterate', 'iteration', 'function', 'def',
        
        # Processing
        'process', 'transform', 'convert', 'change', 'modify',
        'format', 'filter', 'sort', 'order', 'arrange',
        
        # Analysis
        'analyze', 'calculate', 'compute', 'determine', 'check',
        'verify', 'test', 'validate',
    ]
    
    # Check if any Python keyword is in query
    if any(kw in query_lower for kw in python_keywords):
        
        # ========== UNIVERSAL CHARACTER COUNTER ==========
        if any(word in query_lower for word in ['count', 'how many', 'number of', 'total']):
            query_escaped = query.replace('"', '\\"').replace("'", "\\'")
            
            # Determine what to count
            count_targets = []
            
            # Check for specific characters/patterns
            if any(word in query_lower for word in ['dot', 'period', '.']):
                count_targets.append(('dots (.)', '.'))
            if any(word in query_lower for word in ['comma', ',']):
                count_targets.append(('commas (,)', ','))
            if any(word in query_lower for word in ['space', 'spaces']):
                count_targets.append(('spaces', ' '))
            if any(word in query_lower for word in ['letter', 'letters', 'alphabet']):
                count_targets.append(('letters', 'alpha'))
            if any(word in query_lower for word in ['digit', 'digits', 'number']):
                count_targets.append(('digits', 'digit'))
            if any(word in query_lower for word in ['word', 'words']):
                count_targets.append(('words', 'word'))
            if any(word in query_lower for word in ['vowel', 'vowels']):
                count_targets.append(('vowels', 'vowel'))
            if any(word in query_lower for word in ['consonant', 'consonants']):
                count_targets.append(('consonants', 'consonant'))
            if any(word in query_lower for word in ['uppercase', 'capital']):
                count_targets.append(('uppercase letters', 'upper'))
            if any(word in query_lower for word in ['lowercase', 'small']):
                count_targets.append(('lowercase letters', 'lower'))
            if 'character' in query_lower or 'char' in query_lower:
                count_targets.append(('characters', 'char'))
            
            # If no specific target, count everything
            if not count_targets:
                count_targets = [('everything', 'all')]
            
            # Generate comprehensive counting code
            code = f"""# Universal Character Counter
text = "{query_escaped}"

print("=" * 50)
print("CHARACTER ANALYSIS")
print("=" * 50)

# Total counts
print(f"\\nTotal characters: {{len(text)}}")
print(f"Total words: {{len(text.split())}}")

# Character type counts
letters = sum(c.isalpha() for c in text)
digits = sum(c.isdigit() for c in text)
spaces = sum(c.isspace() for c in text)
uppercase = sum(c.isupper() for c in text)
lowercase = sum(c.islower() for c in text)

print(f"\\nLetters: {{letters}}")
print(f"Digits: {{digits}}")
print(f"Spaces: {{spaces}}")
print(f"Uppercase: {{uppercase}}")
print(f"Lowercase: {{lowercase}}")

# Vowels and consonants
vowels = 'aeiouAEIOU'
vowel_count = sum(c in vowels for c in text)
consonant_count = sum(c.isalpha() and c not in vowels for c in text)

print(f"\\nVowels: {{vowel_count}}")
print(f"Consonants: {{consonant_count}}")

# Special characters
dots = text.count('.')
commas = text.count(',')
exclamations = text.count('!')
questions = text.count('?')

print(f"\\nSPECIAL CHARACTERS:")
print(f"  Dots (.): {{dots}}")
print(f"  Commas (,): {{commas}}")
print(f"  Exclamations (!): {{exclamations}}")
print(f"  Questions (?): {{questions}}")

# Character frequency (top 10)
from collections import Counter
char_freq = Counter(text)
print(f"\\nTOP 10 CHARACTERS:")
for char, count in char_freq.most_common(10):
    if char == ' ':
        print(f"  'space': {{count}}")
    elif char == '\\n':
        print(f"  'newline': {{count}}")
    else:
        print(f"  '{{char}}': {{count}}")
"""
            return {"tool": "Python Interpreter", "function": python_interpreter, "params": {"code": code}, "display_params": {"code": code}}
        
        # ========== SPECIFIC PATTERNS ==========
        
        # Factorial
        elif 'factorial' in query_lower:
            match = re.search(r'(\d+)', query_lower)
            n = match.group(1) if match else '10'
            code = f"""# Factorial Calculator
n = {n}
result = 1
for i in range(1, n + 1):
    result *= i

print(f"Factorial of {{n}}:")
print(f"{{n}}! = {{result}}")
print(f"\\nCalculation: 1", end="")
for i in range(2, n + 1):
    print(f" × {{i}}", end="")
print(f" = {{result}}")"""
            return {"tool": "Python Interpreter", "function": python_interpreter, "params": {"code": code}, "display_params": {"code": code}}
        
        # Fibonacci
        elif 'fibonacci' in query_lower:
            match = re.search(r'(\d+)', query_lower)
            n = match.group(1) if match else '10'
            code = f"""# Fibonacci Sequence Generator
def fibonacci(n):
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib

n = {n}
result = fibonacci(n)

print(f"First {{n}} Fibonacci numbers:")
print(result)
print(f"\\nSum: {{sum(result)}}")
print(f"Last number: {{result[-1]}}")"""
            return {"tool": "Python Interpreter", "function": python_interpreter, "params": {"code": code}, "display_params": {"code": code}}
        
        # Prime numbers
        elif 'prime' in query_lower:
            match = re.search(r'(\d+)', query_lower)
            n = match.group(1) if match else '50'
            code = f"""# Prime Number Finder
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

limit = {n}
primes = [num for num in range(2, limit+1) if is_prime(num)]

print(f"Prime numbers up to {{limit}}:")
print(primes)
print(f"\\nTotal count: {{len(primes)}}")
print(f"Largest prime: {{max(primes) if primes else 'None'}}")"""
            return {"tool": "Python Interpreter", "function": python_interpreter, "params": {"code": code}, "display_params": {"code": code}}
        
        # Palindrome check
        elif 'palindrome' in query_lower:
            # Extract text after common phrases
            text_match = re.search(r'(?:check|is|palindrome)\s+["\']?([a-zA-Z0-9\s]+)["\']?', query_lower)
            if text_match:
                text = text_match.group(1).strip()
            else:
                text = "racecar"
            
            code = f"""# Palindrome Checker
text = "{text}"
cleaned = ''.join(c.lower() for c in text if c.isalnum())
is_palindrome = cleaned == cleaned[::-1]

print(f"Text: {{text}}")
print(f"Cleaned: {{cleaned}}")
print(f"Reversed: {{cleaned[::-1]}}")
print(f"\\nIs palindrome? {{is_palindrome}}")"""
            return {"tool": "Python Interpreter", "function": python_interpreter, "params": {"code": code}, "display_params": {"code": code}}
        
        # Even/Odd numbers
        elif ('even' in query_lower or 'odd' in query_lower) and ('number' in query_lower or 'numbers' in query_lower):
            match = re.search(r'(\d+)', query_lower)
            n = match.group(1) if match else '30'
            
            if 'even' in query_lower:
                code = f"""# Even Numbers Generator
limit = {n}
even_numbers = [i for i in range(1, limit+1) if i % 2 == 0]

print(f"Even numbers from 1 to {{limit}}:")
print(even_numbers)
print(f"\\nCount: {{len(even_numbers)}}")
print(f"Sum: {{sum(even_numbers)}}")"""
            else:
                code = f"""# Odd Numbers Generator
limit = {n}
odd_numbers = [i for i in range(1, limit+1) if i % 2 != 0]

print(f"Odd numbers from 1 to {{limit}}:")
print(odd_numbers)
print(f"\\nCount: {{len(odd_numbers)}}")
print(f"Sum: {{sum(odd_numbers)}}")"""
            
            return {"tool": "Python Interpreter", "function": python_interpreter, "params": {"code": code}, "display_params": {"code": code}}
        
        # Sum/Average of numbers
        elif any(word in query_lower for word in ['sum', 'average', 'mean', 'total']) and not 'count' in query_lower:
            numbers = re.findall(r'\d+', query)
            if numbers and len(numbers) > 1:
                nums_str = ', '.join(numbers)
                code = f"""# Number Statistics Calculator
numbers = [{nums_str}]

total = sum(numbers)
average = total / len(numbers)
maximum = max(numbers)
minimum = min(numbers)

print(f"Numbers: {{numbers}}")
print(f"\\nStatistics:")
print(f"  Sum: {{total}}")
print(f"  Average: {{average:.2f}}")
print(f"  Count: {{len(numbers)}}")
print(f"  Maximum: {{maximum}}")
print(f"  Minimum: {{minimum}}")
print(f"  Range: {{maximum - minimum}}")"""
                return {"tool": "Python Interpreter", "function": python_interpreter, "params": {"code": code}, "display_params": {"code": code}}
        
        # Square/Cube/Power
        elif any(word in query_lower for word in ['square', 'cube', 'power', 'exponent']):
            match = re.search(r'(\d+)', query_lower)
            if match:
                n = match.group(1)
                if 'square' in query_lower:
                    code = f"""# Square Calculator
n = {n}
result = n ** 2

print(f"Square of {{n}}:")
print(f"{{n}}² = {{result}}")
print(f"\\nAlso:")
print(f"  Square root of {{result}} = {{result ** 0.5:.2f}}")"""
                elif 'cube' in query_lower:
                    code = f"""# Cube Calculator
n = {n}
result = n ** 3

print(f"Cube of {{n}}:")
print(f"{{n}}³ = {{result}}")
print(f"\\nAlso:")
print(f"  Cube root of {{result}} = {{result ** (1/3):.2f}}")"""
                else:
                    code = f"""# Power Calculator
n = {n}

print(f"Powers of {{n}}:")
for exp in range(1, 11):
    print(f"{{n}}^{{exp}} = {{n**exp}}")"""
                
                return {"tool": "Python Interpreter", "function": python_interpreter, "params": {"code": code}, "display_params": {"code": code}}
        
        # Reverse string
        elif 'reverse' in query_lower:
            # Try to extract text to reverse
            text_match = re.search(r'reverse\s+["\']?([^"\']+)["\']?', query, re.IGNORECASE)
            if text_match:
                text = text_match.group(1).strip()
            else:
                text = query.replace('reverse', '').strip()
            
            text_escaped = text.replace('"', '\\"').replace("'", "\\'")
            code = f"""# String Reverser
text = "{text_escaped}"
reversed_text = text[::-1]

print(f"Original: {{text}}")
print(f"Reversed: {{reversed_text}}")
print(f"\\nLength: {{len(text)}}")
print(f"Is palindrome: {{text.lower() == reversed_text.lower()}}")"""
            return {"tool": "Python Interpreter", "function": python_interpreter, "params": {"code": code}, "display_params": {"code": code}}
        
        # Generic Python request
        else:
            code = f"""# Python Code Execution
# Your query: {query}

# Edit this code to do what you want
print("Python interpreter is ready!")
print("Modify the code below:")
print()

# Example operations:
text = "Hello World"
print(f"Text: {{text}}")
print(f"Uppercase: {{text.upper()}}")
print(f"Lowercase: {{text.lower()}}")
print(f"Length: {{len(text)}}")

# Math example:
numbers = [1, 2, 3, 4, 5]
print(f"\\nNumbers: {{numbers}}")
print(f"Sum: {{sum(numbers)}}")
print(f"Average: {{sum(numbers)/len(numbers)}}")"""
            return {"tool": "Python Interpreter", "function": python_interpreter, "params": {"code": code}, "display_params": {"code": code}}
    
    # Calculator
    calc_patterns = [r'\d+\s*[\+\-\*\/\^]\s*\d+', r'calculate', r'compute']
    if any(re.search(pattern, query_lower) for pattern in calc_patterns):
        match = re.search(r'(\d+\s*[\+\-\*\/\^]\s*\d+)', query)
        if match:
            expr = match.group(1)
            return {"tool": "Calculator", "function": calculator, "params": {"expression": expr}, "display_params": {"expression": expr}}
    
    # Weather
    if 'weather' in query_lower:
        words = query.split()
        for i, word in enumerate(words):
            if word.lower() == 'in' and i + 1 < len(words):
                city = ' '.join(words[i+1:]).strip('?.!')
                return {"tool": "Weather API", "function": get_weather, "params": {"city": city}, "display_params": {"city": city}}
    
    # Crypto
    crypto_keywords = ['bitcoin', 'ethereum', 'crypto', 'btc', 'eth', 'price', 'cryptocurrency']
    if any(kw in query_lower for kw in crypto_keywords):
        for crypto in ['bitcoin', 'ethereum', 'cardano', 'solana', 'dogecoin']:
            if crypto in query_lower or crypto[:3] in query_lower:
                return {"tool": "Crypto Price", "function": get_crypto_price, "params": {"crypto": crypto}, "display_params": {"crypto": crypto}}
    
    # Country
    if 'country' in query_lower or 'capital of' in query_lower or 'population of' in query_lower:
        words = query.replace('?', '').replace('.', '').split()
        if 'of' in words:
            idx = words.index('of')
            if idx + 1 < len(words):
                country = ' '.join(words[idx+1:])
                return {"tool": "Country Info", "function": get_country_info, "params": {"country": country}, "display_params": {"country": country}}
    
    # Time
    if 'time' in query_lower or 'date' in query_lower or 'today' in query_lower or 'now' in query_lower:
        return {"tool": "Current Time", "function": get_current_time, "params": {}, "display_params": {}}
    
    return None


def main():
    st.title("🤖 Multi-Tool Agent with Human Approval")
    st.markdown("*Every tool requires your approval before execution*")
    
    # Check API key
    if not groq_api_key:
        st.warning("⚠️ Please enter your Groq API key in the sidebar!")
        st.info("""
        **Try asking:**
        
        🐍 **Python Operations:**
        - "count the dots ..........."
        - "count all characters in this message"
        - "how many vowels in hello world"
        - "factorial of 10"
        - "fibonacci sequence 15"
        - "prime numbers up to 50"
        - "even numbers to 30"
        - "reverse hello world"
        - "is racecar a palindrome"
        - "square of 25"
        
        🧮 **Other Tools:**
        - "125 * 48" (calculator)
        - "weather in Tokyo"
        - "bitcoin price"
        - "capital of France"
        """)
        return
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "pending_approval" not in st.session_state:
        st.session_state.pending_approval = None
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Show approval UI if pending
    if st.session_state.pending_approval:
        st.divider()
        approval_data = st.session_state.pending_approval
        
        with st.container():
            st.warning(f"⏸️ **Approval Required: {approval_data['tool']}**")
            
            # Show tool inputs
            st.markdown("**Tool will execute with these parameters:**")
            
            # Create editable fields
            edited_params = {}
            for key, value in approval_data['display_params'].items():
                if key == "code":
                    edited_params[key] = st.text_area(f"📝 {key}:", value=str(value), height=250, key=f"edit_{key}")
                else:
                    edited_params[key] = st.text_input(f"📝 {key}:", value=str(value), key=f"edit_{key}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✅ Approve & Execute", type="primary", use_container_width=True):
                    try:
                        # Execute the tool with edited params
                        tool_function = approval_data['function']
                        result = tool_function(**edited_params)
                        
                        st.session_state.messages.append({"role": "assistant", "content": result})
                        st.session_state.pending_approval = None
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Execution error: {str(e)}")
            
            with col2:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.messages.append({"role": "assistant", "content": "❌ Tool execution cancelled by user"})
                    st.session_state.pending_approval = None
                    st.rerun()
    
    # Chat input
    if prompt := st.chat_input("Ask me anything...", disabled=st.session_state.pending_approval is not None):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("🤔 Analyzing query..."):
                try:
                    # Analyze query
                    tool_info = analyze_query(prompt)
                    
                    if tool_info:
                        # Set pending approval
                        st.session_state.pending_approval = tool_info
                        st.info("⏸️ Waiting for your approval...")
                        st.rerun()
                    else:
                        # No tool matched
                        response = """I couldn't match that to a specific tool. Try:
                        
🐍 **Python:** count characters, factorial, fibonacci, prime numbers, palindrome, even/odd, reverse, square, cube, sum, average
🧮 **Calculator:** 5+3, 10*2, 125/5
🌤️ **Weather:** weather in [city]
💰 **Crypto:** bitcoin price, ethereum price
🌍 **Country:** capital of [country]
🕐 **Time:** what time is it?"""
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})


if __name__ == "__main__":
    main()
