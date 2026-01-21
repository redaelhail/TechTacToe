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
        
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def _get_llm_move(self, game):
        # Prepare Data Views
        board_visual = self._format_board(game)
        # Create a list view like ['X', '1', '2', 'O'...]
        board_list = [x if x != " " else str(i) for i, x in enumerate(game.board)]
        
        opponent = 'O' if self.letter == 'X' else 'X'

        # Construct the Chain-of-Thought Prompt
        prompt = f"""
You are a Tic Tac Toe expert engine. You are playing as '{self.letter}'. Opponent is '{opponent}'.

BOARD STATE (Visual):
{board_visual}

BOARD STATE (List):
{board_list}

AVAILABLE MOVES: 
{game.available_moves()}

WINNING LINES (Indices):
Rows: [0,1,2], [3,4,5], [6,7,8]
Cols: [0,3,6], [1,4,7], [2,5,8]
Diagonals: [0,4,8], [2,4,6]

INSTRUCTIONS:
You must think step-by-step inside <thinking> tags before outputting JSON.

1. **Check for Win**: Look at all winning lines. Do you have 2 pieces in a line with the 3rd empty? If yes, take it.
2. **Check for Block**: Does the opponent ('{opponent}') have 2 pieces in a line with the 3rd empty? If yes, BLOCK it immediately.
3. **Strategic Play**: If no win or block, prefer the Center (4), then Corners (0,2,6,8).

FORMAT:
First, output your analysis in <thinking> tags.
Then, output the move in strict JSON.

Example Response:
<thinking>
Checking row [0,1,2]. I have 0. Opponent has 1. 2 is empty. No immediate threat.
Checking diagonal [0,4,8]. Opponent has 0 and 8. 4 is empty. I MUST BLOCK index 4.
</thinking>
{{
    "reasoning": "Opponent has a winning fork on diagonal, blocking at 4.",
    "move": 4
}}
"""
        
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000, # Increase to allow for thinking
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
        
        # Clean up response to ensure pure JSON
        start = response_text.find('{')
        end = response_text.rfind('}') + 1

        # Debug: Print the reasoning to see the LLM thinking
        print(f"\n--- LLM THOUGHTS ---\n{response_text}\n--------------------\n")
        
        if start != -1 and end != -1:
             json_str = response_text[start:end]
        else:
             raise ValueError("No JSON found in response")

        # Validate with Pydantic
        move_data = TicTacToeMove.model_validate_json(json_str)
        return move_data.move

    def _format_board(self, game):
        # Convert list to a visual grid for the LLM
        b = [x if x != " " else str(i) for i, x in enumerate(game.board)]
        return f"""
{b[0]} | {b[1]} | {b[2]}
--+---+--
{b[3]} | {b[4]} | {b[5]}
--+---+--
{b[6]} | {b[7]} | {b[8]}
"""
