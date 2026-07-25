# NEPSE Averaging Down & FD Comparison Engine

A Streamlit-based decision support tool for NEPSE investors that compares stock averaging-down strategies against risk-free fixed deposit returns. The project enables interactive portfolio input, recovery scenario mapping, and visual analysis using Plotly charts.

## Overview

This application helps investors model their current NEPSE stock holdings, estimate break-even and recovery prices, and determine whether deploying new capital into averaging down makes more sense than investing in a low-risk fixed deposit alternative. The UI is designed to support:

- Portfolio input and transaction history capture
- Weighted average cost and break-even analytics
- Comparisons between Fixed Deposit returns and averaged portfolio outcomes
- Recovery milestone scenario generation
- Interactive Plotly charts for visual decision support

## Key Features

- **FD vs Averaging Down Comparison**
  - Interactive input for additional cash, FD annual rate, and investment horizon
  - Side-by-side grouped Plotly bar chart comparing FD final value and averaged portfolio value

- **Target Average Extractor**
  - Calculates the number of shares required at a new purchase price to hit a desired average cost

- **Milestone Recovery Scenarios**
  - Displays recovery-step projections including target price, projected portfolio value, and net result
  - Adds a horizontal Plotly bar chart showing unrealized gain/loss at each recovery milestone

## Architecture

The project is organized in a modular architecture with a clean separation between UI, domain logic, and calculations.

```text
+----------------------+      +------------------------+
|  Streamlit Frontend   |----->|  PortfolioAnalyzer     |
|  (Avg-ETL/app.py)     |      |  (Avg-ETL/src/analyzer.py) |
+----------------------+      +------------------------+
            |                           |
            |                           v
            |                 +------------------------+
            |                 |  Calculations & Models  |
            |                 |  (Avg-ETL/src/models.py, |
            |                 |   Avg-ETL/src/calculations.py) |
            |                 +------------------------+
            v
+----------------------+      +------------------------+
|  Plotly/Visualization |<-----|  Data processing layer |
|  (Interactive charts) |      +------------------------+
+----------------------+      
```

### Architectural Notes

- `Avg-ETL/app.py` is the front-end entrypoint and uses Streamlit to render UI components and charts.
- `Avg-ETL/src/models.py` defines the portfolio and transaction domain objects.
- `Avg-ETL/src/analyzer.py` orchestrates scenario generation, averaging calculations, and FD comparisons.
- Calculations are built to remain separated from presentation so the same logic can be reused, extended, or tested independently.

## Installation

1. Clone the repository:

```bash
git clone <repo-url>
cd <repository-root>
```

2. Create and activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
python3 -m pip install --upgrade pip
python3 -m pip install streamlit pandas plotly
```

## Running the App

From the repository root, run:

```bash
streamlit run Avg-ETL/app.py
```

Then open the browser page that Streamlit launches to explore the app.

## Project Structure

- `Avg-ETL/app.py` - Streamlit application entrypoint and UI layout
- `Avg-ETL/src/models.py` - Portfolio and transaction data models
- `Avg-ETL/src/analyzer.py` - Business logic for recoveries, averaging, and FD comparison
- `Avg-ETL/src/calculations.py` - Supporting mathematical calculation functions
- `Avg-ETL/tests/` - Test cases for validating core logic

## Notes

- The app is tailored for NEPSE-style stock averaging and recovery analysis, but the design can be extended for other equity markets.
- Plotly charts provide interactive, hover-enabled analytics for both strategy comparisons and recovery milestone mapping.

## Contribution

Contributions are welcome. Please open an issue or pull request for any enhancements, bug fixes, or new visualization ideas.
