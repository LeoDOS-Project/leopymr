class HungarianState {
    constructor(matrix) {
        // Basic setup
        this.originalMatrix = JSON.parse(JSON.stringify(matrix)); // Deep copy
        this.n = matrix.length;
        this.m = matrix[0].length;
        this.dim = Math.max(this.n, this.m);

        // Pad matrix if necessary
        this.costMatrix = this.padMatrix(matrix, this.dim);

        // Algorithm State
        this.step = 0; // 0: Start, 1: Reduce Rows, 2: Reduce Cols, ...
        this.rowCovered = new Array(this.dim).fill(false);
        this.colCovered = new Array(this.dim).fill(false);
        this.marks = Array.from({ length: this.dim }, () => new Array(this.dim).fill(0)); // 0: none, 1: star, 2: prime

        this.pathStart = null;
        this.path = [];

        this.stateDescription = "Ready to start.";
        this.stepName = "INIT";

        // UI Helpers
        this.highlightRows = [];
        this.highlightCols = [];
        this.activeCell = null; // {r, c}
    }

    padMatrix(matrix, dim) {
        let padded = Array.from({ length: dim }, () => new Array(dim).fill(0));
        let maxVal = 0;

        if (matrix.length < dim || matrix[0].length < dim) {
            for (let row of matrix) for (let val of row) maxVal = Math.max(maxVal, val);
        }

        for (let r = 0; r < dim; r++) {
            for (let c = 0; c < dim; c++) {
                if (r < matrix.length && c < matrix[0].length) {
                    padded[r][c] = matrix[r][c];
                } else {
                    padded[r][c] = maxVal;
                }
            }
        }
        return padded;
    }

    next() {
        this.clearHighlights();

        switch (this.stepName) {
            case "INIT":
                this.step_reduce_rows();
                break;
            case "REDUCE_ROWS":
                this.step_reduce_cols();
                break;
            case "REDUCE_COLS":
                this.step_find_initial_stars();
                break;
            case "FIND_INITIAL_STARS":
                this.step_cover_columns();
                break;
            case "COVER_COLUMNS":
                // Decision point handled in step_cover_columns
                break;
            case "PRIME_ZEROS":
                // Loop or transition handled internally
                this.step_prime_zeros();
                break;
            case "AUGMENT_PATH":
                this.step_augment_path();
                break;
            case "ADJUST_MATRIX":
                this.step_adjust_matrix();
                break;
            case "DONE":
                this.stateDescription = "Algorithm Complete! Final Assignment Found.";
                break;
        }
    }

    clearHighlights() {
        this.highlightRows = [];
        this.highlightCols = [];
        this.activeCell = null;
    }

    // --- Steps ---

    step_reduce_rows() {
        this.stateDescription = "Subtracting row minimums from each row.";
        for (let r = 0; r < this.dim; r++) {
            let minVal = Math.min(...this.costMatrix[r]);
            for (let c = 0; c < this.dim; c++) {
                this.costMatrix[r][c] -= minVal;
            }
        }
        this.stepName = "REDUCE_ROWS";
    }

    step_reduce_cols() {
        this.stateDescription = "Subtracting column minimums from each column.";
        for (let c = 0; c < this.dim; c++) {
            let minVal = Infinity;
            for (let r = 0; r < this.dim; r++) minVal = Math.min(minVal, this.costMatrix[r][c]);

            for (let r = 0; r < this.dim; r++) {
                this.costMatrix[r][c] -= minVal;
            }
        }
        this.stepName = "REDUCE_COLS";
    }

    step_find_initial_stars() {
        this.stateDescription = "Finding initial independent zeros to Star (★).";
        let rowHasStar = new Array(this.dim).fill(false);
        let colHasStar = new Array(this.dim).fill(false);

        for (let r = 0; r < this.dim; r++) {
            for (let c = 0; c < this.dim; c++) {
                if (this.costMatrix[r][c] === 0 && !rowHasStar[r] && !colHasStar[c]) {
                    this.marks[r][c] = 1; // Star
                    rowHasStar[r] = true;
                    colHasStar[c] = true;
                }
            }
        }
        this.stepName = "FIND_INITIAL_STARS";
    }

    step_cover_columns() {
        this.stateDescription = "Covering all columns containing a Starred zero.";
        this.colCovered.fill(false);
        let coveredCount = 0;

        for (let r = 0; r < this.dim; r++) {
            for (let c = 0; c < this.dim; c++) {
                if (this.marks[r][c] === 1) {
                    this.colCovered[c] = true;
                }
            }
        }

        coveredCount = this.colCovered.filter(x => x).length;

        if (coveredCount >= this.dim) {
            this.stepName = "DONE";
            this.stateDescription = "All columns covered with unique stars. Optimal solution found!";
        } else {
            this.stepName = "PRIME_ZEROS";
            this.stateDescription = `Covered ${coveredCount} columns. Need ${this.dim}. Proceeding to Prime Zeros.`;
        }
    }

    step_prime_zeros() {
        // Find an uncovered zero
        let r = -1, c = -1;

        outerLoop:
        for (let i = 0; i < this.dim; i++) {
            if (!this.rowCovered[i]) {
                for (let j = 0; j < this.dim; j++) {
                    if (!this.colCovered[j] && this.costMatrix[i][j] === 0) {
                        r = i;
                        c = j;
                        break outerLoop;
                    }
                }
            }
        }

        if (r === -1) {
            // No uncovered zeros found
            this.stepName = "ADJUST_MATRIX";
            this.stateDescription = "No uncovered zeros found. Adjusting matrix values.";
            return;
        }

        // We found an uncovered zero at r, c
        this.marks[r][c] = 2; // Prime it
        this.activeCell = { r, c };
        this.stateDescription = `Found uncovered zero at (${r}, ${c}). Priming it (').`;

        // Check if there is a star in this row
        let starCol = -1;
        for (let j = 0; j < this.dim; j++) {
            if (this.marks[r][j] === 1) {
                starCol = j;
                break;
            }
        }

        if (starCol !== -1) {
            this.rowCovered[r] = true;
            this.colCovered[starCol] = false;
            this.stateDescription += ` Star found in row ${r} at col ${starCol}. Covering row, uncovering col.`;
            // Stay in PRIME_ZEROS state to find next zero
            this.stepName = "PRIME_ZEROS";
        } else {
            // No star in row - Augment path
            this.pathStart = { r, c };
            this.stepName = "AUGMENT_PATH";
            this.stateDescription += ` No star in row ${r}. Starting Augment Path from (${r}, ${c}).`;
        }
    }

    step_augment_path() {
        this.stateDescription = "Constructing alternating path of Stars and Primes, then flipping them.";
        this.path = [this.pathStart];
        let curr = this.pathStart;

        while (true) {
            // Find star in column of current prime
            let starRow = -1;
            for (let i = 0; i < this.dim; i++) {
                if (this.marks[i][curr.c] === 1) {
                    starRow = i;
                    break;
                }
            }

            if (starRow === -1) break;

            this.path.push({ r: starRow, c: curr.c });

            // Find prime in row of found star
            let primeCol = -1;
            for (let j = 0; j < this.dim; j++) {
                if (this.marks[starRow][j] === 2) {
                    primeCol = j;
                    break;
                }
            }

            this.path.push({ r: starRow, c: primeCol });
            curr = { r: starRow, c: primeCol };
        }

        // Augment
        for (let p of this.path) {
            if (this.marks[p.r][p.c] === 1) {
                this.marks[p.r][p.c] = 0;
            } else {
                this.marks[p.r][p.c] = 1;
            }
        }

        // Clear covers and primes
        this.rowCovered.fill(false);
        this.colCovered.fill(false);
        for (let i = 0; i < this.dim; i++) {
            for (let j = 0; j < this.dim; j++) {
                if (this.marks[i][j] === 2) this.marks[i][j] = 0;
            }
        }

        this.stepName = "COVER_COLUMNS"; // Go back to covering columns
        this.stateDescription += " Path augmented. Cleared primes and covers. Returning to Step 2.";
    }

    step_adjust_matrix() {
        let minUncovered = Infinity;
        for (let r = 0; r < this.dim; r++) {
            if (!this.rowCovered[r]) {
                for (let c = 0; c < this.dim; c++) {
                    if (!this.colCovered[c]) {
                        minUncovered = Math.min(minUncovered, this.costMatrix[r][c]);
                    }
                }
            }
        }

        this.stateDescription = `Adjusting matrix: subtract ${minUncovered} from uncovered, add to double covered via intersection.`;

        for (let r = 0; r < this.dim; r++) {
            for (let c = 0; c < this.dim; c++) {
                if (this.rowCovered[r]) {
                    this.costMatrix[r][c] += minUncovered;
                }
                if (!this.colCovered[c]) {
                    this.costMatrix[r][c] -= minUncovered;
                }
            }
        }

        this.stepName = "PRIME_ZEROS"; // Go back to finding zeros
    }
}

// --- UI Application Logic ---

const App = {
    solver: null,
    animationSpeed: 1000,
    intervalId: null,

    init() {
        this.cacheDOM();
        this.bindEvents();
        this.generateRandomMatrix(3);
    },

    cacheDOM() {
        this.container = document.getElementById('matrix-container');
        this.stepDesc = document.getElementById('step-description');
        this.btnNext = document.getElementById('btn-next');
        this.btnPrev = document.getElementById('btn-prev'); // Not implemented yet (hard for state machine)
        this.btnPlay = document.getElementById('btn-play');
        this.btnReset = document.getElementById('btn-reset');
        this.btnGenerate = document.getElementById('btn-generate');
        this.btnInput = document.getElementById('btn-input');
        this.inputSize = document.getElementById('matrix-size');
        this.inputSpeed = document.getElementById('speed-range');

        // Modal
        this.modal = document.getElementById('input-modal');
        this.btnApplyInput = document.getElementById('btn-apply-input');
        this.btnCancelInput = document.getElementById('btn-cancel-input');
        this.txtInput = document.getElementById('manual-matrix-input');
    },

    bindEvents() {
        this.btnNext.addEventListener('click', () => this.nextStep());
        this.btnReset.addEventListener('click', () => this.reset());
        this.btnPlay.addEventListener('click', () => this.togglePlay());
        this.btnGenerate.addEventListener('click', () => {
            const size = parseInt(this.inputSize.value) || 3;
            this.generateRandomMatrix(size);
        });

        this.inputSpeed.addEventListener('input', (e) => {
            this.animationSpeed = 2100 - e.target.value; // Invert logic for better feel
            if (this.intervalId) {
                this.stopPlay();
                this.startPlay();
            }
        });

        // Modal
        this.btnInput.addEventListener('click', () => this.modal.classList.add('visible'));
        this.btnCancelInput.addEventListener('click', () => this.modal.classList.remove('visible'));
        this.btnApplyInput.addEventListener('click', () => this.parseInput());
    },

    generateRandomMatrix(n) {
        let matrix = [];
        for (let i = 0; i < n; i++) {
            let row = [];
            for (let j = 0; j < n; j++) {
                row.push(Math.floor(Math.random() * 20) + 1);
            }
            matrix.push(row);
        }
        this.startNewSolver(matrix);
    },

    parseInput() {
        try {
            const text = this.txtInput.value.trim();
            const rows = text.split('\n');
            const matrix = rows.map(r => r.split(',').map(n => parseInt(n.trim())));

            // Validate jagged arrays
            const cols = matrix[0].length;
            if (matrix.some(r => r.length !== cols)) throw new Error("Rows must have equal length");
            if (matrix.some(r => r.some(isNaN))) throw new Error("Invalid number");

            this.startNewSolver(matrix);
            this.modal.classList.remove('visible');
        } catch (e) {
            alert("Invalid Matrix Format: " + e.message);
        }
    },

    startNewSolver(matrix) {
        this.stopPlay();
        this.solver = new HungarianState(matrix);
        this.render();
    },

    reset() {
        if (this.solver) {
            this.startNewSolver(this.solver.originalMatrix);
        }
    },

    nextStep() {
        if (!this.solver) return;
        if (this.solver.stepName === 'DONE') return;

        this.solver.next();
        this.render();
    },

    togglePlay() {
        if (this.intervalId) {
            this.stopPlay();
        } else {
            this.startPlay();
        }
    },

    startPlay() {
        this.btnPlay.textContent = "⏸";
        this.intervalId = setInterval(() => {
            if (this.solver.stepName === 'DONE') {
                this.stopPlay();
                return;
            }
            this.nextStep();
        }, this.animationSpeed);
    },

    stopPlay() {
        this.btnPlay.textContent = "▶";
        clearInterval(this.intervalId);
        this.intervalId = null;
    },

    render() {
        const s = this.solver;
        this.stepDesc.textContent = s.stateDescription;

        this.container.style.gridTemplateColumns = `repeat(${s.dim}, var(--cell-size))`;
        this.container.innerHTML = '';

        for (let r = 0; r < s.dim; r++) {
            for (let c = 0; c < s.dim; c++) {
                const cell = document.createElement('div');
                cell.className = 'matrix-cell';
                cell.textContent = s.costMatrix[r][c];

                if (s.marks[r][c] === 1) cell.classList.add('starred');
                if (s.marks[r][c] === 2) cell.classList.add('primed');
                if (s.rowCovered[r]) cell.classList.add('covered-row');
                if (s.colCovered[c]) cell.classList.add('covered-col');

                if (s.activeCell && s.activeCell.r === r && s.activeCell.c === c) {
                    cell.classList.add('active-val');
                }

                if (s.stepName === 'DONE' && s.marks[r][c] === 1) {
                    cell.classList.add('final-assignment');
                }

                this.container.appendChild(cell);
            }
        }
    }
};

// Start
App.init();
