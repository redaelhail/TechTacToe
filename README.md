# TechTacToe
#  Tic Tac Toe vs AI

A modern, interactive Tic Tac Toe game built with **Python**  **Streamlit** and an AI player agent.

##  Features

- **Multiple Opponents**:
  - **Random**: A basic opponent that makes random moves. Great for casual play.
   - **LLM**: An opponent powered by a Large Language Model.


## Technology Stack

- **Language**: Python 3.10+
- **Frontend Framework**: [Streamlit](https://streamlit.io/)

##  Getting Started

Follow these instructions to run the game locally:

### Prerequisites

- Python 3

### Installation

1. **Clone the repository** (or download usage files):
   ```bash
   git clone https://github.com/redaelhail/TechTacToe
   cd TechTacToe
   ```

2. **Create a Virtual Environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the App

Execute the following command to start the Streamlit server:

```bash
streamlit run app.py
```

The game will automatically open in your default web browser at `http://localhost:8501`.

## Project Structure

- `app.py`: Streamlit UI and interaction logic.
- `game_logic.py`: TicTacToe game logic, rules and possible moves
- `agent.py`: The opponent players, Random player with random moves, AI player making a strategy with an LLM.

## Summary

- My initial approach of just showing the model a text-based grid failed pretty hard because it lacked the spatial reasoning to spot diagonal threats. 
- The real turning point was feeding the AI a report that explicitly listed which lines were about to win or needed blocking. 
- I also saw a huge jump in performance when I forced the model to write out its thought process step-by-step before committing to a final move.
- On the technical side, building a retry loop was essential for catching random formatting glitches, but I learned that restricting the response length too aggressively actually backfired by cutting off the model's reasoning mid-sentence.
- The LLM can still be improved by adding a memory to learn  from its wrong and good moves.