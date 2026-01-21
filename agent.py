import random
import os
import json
import boto3
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_fixed

# Load environment variables
load_dotenv()

class TicTacToeMove(BaseModel):
    move: int = Field(..., description="The index of the square to play (0-8)", ge=0, le=8)
    reasoning: str = Field(..., description="Short explanation of why this move was chosen")

class RandomPlayer:
    def __init__(self, letter):
        self.letter = letter

    def get_move(self, game):
        """
        Determine the move based on the game state.
        implements a random strategy as a placeholder.
        """
        square = random.choice(game.available_moves())
        return square
class LLMPlayer(RandomPlayer):
    """
    An AI player that uses AWS Bedrock (Claude) to decide moves.
    Falls back to Random if the LLM fails or plays illegally.
    """
    def __init__(self, letter):
        super().__init__(letter)
        try:
            self.bedrock = boto3.client(
                service_name='bedrock-runtime',
                region_name=os.getenv('AWS_REGION', 'us-east-1'),
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            self.model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-haiku-20240307-v1:0')
        except Exception as e:
            print(f"Error initializing Bedrock client: {e}")
            self.bedrock = None

    def get_move(self, game):
        if not self.bedrock:
            print("Bedrock client not available, falling back to Random.")
            return super().get_move(game)

        try:
            move_index = self._get_llm_move(game)
            print(f"LLM suggested move {move_index}")
            if move_index in game.available_moves():
                return move_index
            else:
                print(f"LLM suggested invalid move {move_index} (Occupied). Fallback.")
                return super().get_move(game)
        except Exception as e:
            print(f"LLM Error: {e}. Fallback to RandomPlayer.")
            return super().get_move(game)
        
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def _get_llm_move(self, game):
        # HELPER: Pre-calculate line states 
        line_analysis_text = self._analyze_board_lines(game)
        
        prompt = f"""
You are a Tic Tac Toe expert. 
Your goal is to win or draw. You NEVER lose if a block is possible.

You are playing as: '{self.letter}'
Opponent is: '{'O' if self.letter == 'X' else 'X'}'

CURRENT BOARD ANALYSIS:
{line_analysis_text}

AVAILABLE MOVES: {game.available_moves()}

STRATEGY PRIORITY (Follow Strictly):
1. **WIN**: If any line has 2 of YOUR pieces and 1 EMPTY, play the EMPTY spot immediately.
2. **BLOCK**: If any line has 2 OPPONENT pieces and 1 EMPTY, play the EMPTY spot immediately.
3. **CENTER**: If '4' is available, take it.
4. **CORNERS**: If 0, 2, 6, or 8 are available, take them.

INSTRUCTIONS:
- Read the "CURRENT BOARD ANALYSIS" above.
- Identify the most critical line.
- Output your reasoning inside <thinking> tags first.
- Output the final move in JSON.

Example Response:
<thinking>
Row 0 has 2 opponent pieces and index 2 is empty. This is a threat. I must BLOCK.
</thinking>
{{
    "reasoning": "Blocking opponent on Row 0",
    "move": 2
}}
"""
        
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 250,
            "messages": [
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "temperature": 0.1
        })

        response = self.bedrock.invoke_model(
            body=body, 
            modelId=self.model_id,
            accept='application/json',
            contentType='application/json'
        )
        
        response_body = json.loads(response.get('body').read())
        response_text = response_body.get('content')[0].get('text')
        
        # Parse JSON from the response (handling the thinking block)
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        if start != -1 and end != -1:
             return TicTacToeMove.model_validate_json(response_text[start:end]).move
        raise ValueError("No JSON found")

    def _analyze_board_lines(self, game):
        """
        Creates a text description of every winning line so the LLM
        doesn't have to spatially parse the grid.
        """
        lines = [
            (0,1,2), (3,4,5), (6,7,8), # Rows
            (0,3,6), (1,4,7), (2,5,8), # Cols
            (0,4,8), (2,4,6)           # Diagonals
        ]
        
        report = []
        board = game.board
        
        for a, b, c in lines:
            # Get values at these positions (e.g., ['X', ' ', 'O'])
            values = [board[a], board[b], board[c]]
            # Get indices that are empty
            empty_indices = [idx for idx, val in zip([a,b,c], values) if val == ' ']
            
            # Count X and O
            x_count = values.count('X')
            o_count = values.count('O')
            
            # Format a status string for the LLM
            line_name = f"Line [{a},{b},{c}]"
            status = f"Contains: {values}"
            
            # Add explicit Hints
            if x_count == 2 and len(empty_indices) == 1:
                status += f" -> WIN OPPORTUNITY for X at {empty_indices[0]}"
            elif o_count == 2 and len(empty_indices) == 1:
                status += f" -> WIN OPPORTUNITY for O at {empty_indices[0]}"
            
            report.append(f"{line_name}: {status}")
            
        # Explicitly mention Center
        if board[4] == ' ':
            report.append("CENTER CELL (4) IS EMPTY AND AVAILABLE.")
        else:
            report.append(f"Center cell (4) is taken by {board[4]}.")

        return "\n".join(report)
