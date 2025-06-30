const { createApp } = Vue;

const app = createApp({
    data() {
        return {
            registers: {},
            memory: [],
            log: [],
            editor: null,
            isRunning: false,
            error: null
        };
    },
    mounted() {
        this.$nextTick(() => {
            const textarea = document.querySelector('#code-editor');
            
            this.editor = CodeMirror.fromTextArea(textarea, {
                mode: 'gas',
                theme: 'monokai',
                lineNumbers: true,
                tabSize: 4,
                indentUnit: 4,
                lineWrapping: true,
                // removed autofocus
                cursorHeight: 1,
                matchBrackets: true,
                autoCloseBrackets: true,
                styleActiveLine: true,
                direction: 'ltr',
                scrollbarStyle: 'native',
                fixedGutter: true,
                dragDrop: true,
                firstLineNumber: 1,
                keyMap: 'default',
                extraKeys: {
                    "Enter": (cm) => {
                        const cursor = cm.getCursor();
                        const currentLine = cursor.line;
                        cm.replaceRange('\n', cursor);
                        cm.setCursor({
                            line: currentLine + 1,
                            ch: 0
                        });
                        cm.scrollIntoView();
                    },
                    "Tab": (cm) => {
                        if (cm.somethingSelected()) cm.indentSelection("add");
                        else cm.replaceSelection("    ", "end");
                    }
                }
            });

            // Set initial value with two blank lines after first line
            this.editor.setValue('');  // Start with two blank lines
            this.editor.setCursor(0, 0); // Place cursor at start
            
            this.editor.focus();
            // Initial reset
            this.resetVM();
        });
    },
    methods: {
        focusEditorToEnd() {
            const lastLine = this.editor.lineCount() - 1;
            const lastChar = this.editor.getLine(lastLine).length;
            this.editor.setCursor({ line: lastLine, ch: lastChar });
            this.editor.focus();
            this.editor.refresh();
        },
        async runCode() {
            this.isRunning = true;
            this.error = null;
            try {
                const response = await fetch('/execute', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code: this.editor.getValue() })
                });
                const data = await response.json();
                this.updateUI(data);
            } catch (err) {
                this.error = `Execution error: ${err.message}`;
            }
            this.isRunning = false;
        },
        async resetVM() {
            this.isRunning = true;
            try {
                const response = await fetch('/reset', { method: 'POST' });
                const data = await response.json();
                this.updateUI(data);
            } catch (err) {
                this.error = `Reset error: ${err.message}`;
            }
            this.isRunning = false;
        },
        updateUI(data) {
            this.registers = data.registers;
            this.memory = data.memory;
            this.log = data.log;
            
            this.updateRegisters();
            this.updateMemory();
            this.updateLog();
        },
        updateRegisters() {
            const registerDiv = document.getElementById('registers');
            registerDiv.innerHTML = Object.entries(this.registers)
                .map(([reg, val]) => 
                    `<div class="register-entry">
                        <span class="register-name">${reg.toUpperCase()}</span>: 
                        <span class="register-value">0x${val.toString(16).padStart(8, '0')}</span> 
                        <span class="register-decimal">(${val})</span>
                    </div>`
                ).join('');
        },
        updateMemory() {
            const memoryDiv = document.getElementById('memory');
            memoryDiv.innerHTML = this.memory
                .map((val, i) => 
                    `<div class="memory-entry">
                        [${i.toString(16).padStart(4, '0')}]: 0x${val.toString(16).padStart(2, '0')}
                    </div>`
                ).join('');
        },
        updateLog() {
            const logDiv = document.getElementById('log');
            logDiv.innerHTML = this.log
                .map(entry => `<div class="log-entry">${entry}</div>`)
                .join('');
            logDiv.scrollTop = logDiv.scrollHeight;
        }
    }
});

app.mount('#app');