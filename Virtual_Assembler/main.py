from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize register state
registers = {
    'eax': 0,
    'ebx': 0,
    'ecx': 0,
    'edx': 0,
    'esi': 0,
    'edi': 0,
    'ebp': 0,
    'esp': 0
}

# Initialize memory (simplified)
memory = [0] * 1024

# Execution log
execution_log = []

def reset_state():
    """Reset registers and memory to initial state"""
    global registers, memory, execution_log
    registers = {reg: 0 for reg in registers}
    memory = [0] * 1024
    execution_log = []

def parse_value(val):
    """Parse a value which could be a register, immediate value, or memory reference"""
    val = val.strip()
    
    # Check if it's a register
    if val in registers:
        return registers[val]
    
    # Check if it's a memory reference [reg]
    if val.startswith('[') and val.endswith(']'):
        inner = val[1:-1]
        if inner in registers:
            addr = registers[inner]
            return memory[addr]
        else:
            # Handle direct memory access [number]
            try:
                addr = int(inner)
                return memory[addr]
            except ValueError:
                execution_log.append(f"Error: Invalid memory reference {val}")
                return 0
    
    # Otherwise, treat as immediate value
    try:
        if val.startswith('0x'):
            return int(val, 16)
        else:
            return int(val)
    except ValueError:
        execution_log.append(f"Error: Can't parse value {val}")
        return 0

def execute_mov(dest, src):
    """Execute MOV instruction"""
    value = parse_value(src)
    
    if dest in registers:
        registers[dest] = value
        execution_log.append(f"MOV: Set {dest} = {value}")
    elif dest.startswith('[') and dest.endswith(']'):
        inner = dest[1:-1]
        if inner in registers:
            addr = registers[inner]
            memory[addr] = value
            execution_log.append(f"MOV: Set memory[{addr}] = {value}")
        else:
            try:
                addr = int(inner)
                memory[addr] = value
                execution_log.append(f"MOV: Set memory[{addr}] = {value}")
            except ValueError:
                execution_log.append(f"Error: Invalid memory reference {dest}")
    else:
        execution_log.append(f"Error: Invalid destination {dest}")

# Add this function before the route definitions
def execute_instruction(line):
    """Execute a single assembly instruction"""
    # Remove comments and whitespace
    line = line.split(';')[0].strip()
    if not line:
        return

    # Parse instruction
    parts = re.split(r'[\s,]+', line)
    opcode = parts[0].lower()
    operands = parts[1:]

    # Execute based on opcode
    if opcode == 'mov':
        if len(operands) == 2:
            execute_mov(operands[0], operands[1])
        else:
            execution_log.append(f"Error: MOV requires 2 operands, got {len(operands)}")
    
    elif opcode == 'add':
        if len(operands) == 2:
            dest = operands[0]
            value = parse_value(operands[1])
            if dest in registers:
                registers[dest] += value
                execution_log.append(f"ADD: {dest} += {value}")
            else:
                execution_log.append(f"Error: Invalid destination register {dest}")
        else:
            execution_log.append(f"Error: ADD requires 2 operands, got {len(operands)}")

    elif opcode == 'sub':
        if len(operands) == 2:
            dest = operands[0]
            value = parse_value(operands[1])
            if dest in registers:
                registers[dest] -= value
                execution_log.append(f"SUB: {dest} -= {value}")
            else:
                execution_log.append(f"Error: Invalid destination register {dest}")
        else:
            execution_log.append(f"Error: SUB requires 2 operands, got {len(operands)}")

    elif opcode == 'push':
        if len(operands) == 1:
            value = parse_value(operands[0])
            registers['esp'] -= 4  # Decrement stack pointer
            memory[registers['esp']] = value
            execution_log.append(f"PUSH: {value} to stack at ESP={registers['esp']}")
        else:
            execution_log.append(f"Error: PUSH requires 1 operand, got {len(operands)}")

    elif opcode == 'pop':
        if len(operands) == 1:
            dest = operands[0]
            if dest in registers:
                registers[dest] = memory[registers['esp']]
                registers['esp'] += 4  # Increment stack pointer
                execution_log.append(f"POP: {dest} = {registers[dest]}")
            else:
                execution_log.append(f"Error: Invalid destination register {dest}")
        else:
            execution_log.append(f"Error: POP requires 1 operand, got {len(operands)}")

    else:
        execution_log.append(f"Error: Unknown instruction {opcode}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/execute', methods=['POST'])
def execute_code():
    """API endpoint to execute assembly code"""
    data = request.json
    code = data.get('code', '')
    
    reset_state()
    
    # Execute each instruction
    lines = code.split('\n')
    for line in lines:
        execute_instruction(line)
    
    return jsonify({
        'registers': registers,
        'memory': memory[:64],  # Return first 64 bytes of memory for display
        'log': execution_log
    })

@app.route('/reset', methods=['POST'])
def reset():
    """API endpoint to reset the virtual machine state"""
    reset_state()
    return jsonify({
        'registers': registers,
        'memory': memory[:64],
        'log': execution_log
    })

if __name__ == '__main__':
    app.run(debug=True)