import streamlit as st
from game_logic import TicTacToe
from agent import RandomPlayer
import time

st.set_page_config(page_title="Tic Tac Toe AI", page_icon="🎮", layout="centered")

# --- Custom CSS for Premium Styling ---
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #1e1e2f 0%, #2b2b40 100%);
        color: #ffffff;
        font-family: 'Helvetica Neue', sans-serif;
    }
    
    h1 {
        text-align: center;
        color: #00e5ff;
        text-shadow: 0 0 10px rgba(0, 229, 255, 0.5);
        font-weight: 800;
        margin-bottom: 10px;
    }
    
    p {
        text-align: center;
        font-size: 1.2rem;
        color: #b0b0c0;
    }

    /* Game Board Styles */
    .stButton > button {
        width: 100%;
        aspect-ratio: 1 / 1; 
        font-size: 2.5rem;
        font-weight: bold;
        background: rgba(255, 255, 255, 0.05);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background: rgba(255, 255, 255, 0.1);
        border-color: rgba(255, 255, 255, 0.3);
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
    }

    /* Player Specific Colors (This relies on Streamlit's disabling logic or manual styling if possible, 
       hard to inject specific classes per button easily, so we rely on global overrides or specific logic) */
    
    /* Center the board */
    div[data-testid="column"] {
        display: flex;
        align-items: center;
        justify-content: center; 
    }
    
    /* Winning Message */
    .winner-box {
        padding: 20px;
        background: rgba(0, 229, 255, 0.2);
        border: 2px solid #00e5ff;
        border-radius: 15px;
        text-align: center;
        margin-top: 20px;
        animation: fadeIn 1s ease-in-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.title("🎮 Tic Tac Toe vs AI")
st.markdown("<p>Challenge the artificial intelligence. Can you win?</p>", unsafe_allow_html=True)

# --- Initialize Session State ---
if 'game' not in st.session_state:
    st.session_state.game = TicTacToe()
if 'board' not in st.session_state:
    st.session_state.board = st.session_state.game.board
if 'current_turn' not in st.session_state:
    st.session_state.current_turn = 'X' # User usually plays X
if 'winner' not in st.session_state:
    st.session_state.winner = None
if 'game_over' not in st.session_state:
    st.session_state.game_over = False

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Settings")
    opponent_type = st.selectbox(
        "Choose Opponent", 
        ["Random"]
    )
    st.markdown("---")
    
    def reset_game():
        st.session_state.game = TicTacToe()
        st.session_state.board = st.session_state.game.board
        st.session_state.current_turn = 'X'
        st.session_state.winner = None
        st.session_state.game_over = False
        st.toast("Game has been reset!", icon="🔄")

    if st.button("🔄 New Game", use_container_width=True):
        reset_game()
        st.rerun()

    st.markdown("### 📝 Rules")
    st.info("You are **X**. The Computer is **O**.\nGet 3 in a row to win!")

# --- Game Logic ---
def make_move(index):
    if st.session_state.game.board[index] == " " and not st.session_state.game_over:
        st.session_state.game.make_move(index, st.session_state.current_turn)
        st.session_state.board = st.session_state.game.board
        
        if st.session_state.game.current_winner:
            st.session_state.winner = st.session_state.current_turn
            st.session_state.game_over = True
        elif not st.session_state.game.empty_squares():
            st.session_state.game_over = True 
        else:
            st.session_state.current_turn = 'O'

# --- Computer Turn ---
if st.session_state.current_turn == 'O' and not st.session_state.game_over:
    with st.spinner("🤖 Computer is thinking..."):
        time.sleep(0.6) 
        ai_player = None
        if opponent_type == "Random":
            ai_player = RandomPlayer('O')

        
        if ai_player:
            move = ai_player.get_move(st.session_state.game)
            st.session_state.game.make_move(move, 'O')
            st.session_state.board = st.session_state.game.board
            
            if st.session_state.game.current_winner:
                st.session_state.winner = 'O'
                st.session_state.game_over = True
            elif not st.session_state.game.empty_squares():
                 st.session_state.game_over = True 
            else:
                st.session_state.current_turn = 'X'
            st.rerun()

# --- Board Layout ---
# Use columns to center the grid effectively
c1, c2, c3 = st.columns([1, 2, 1])

with c2:
    # 3x3 Grid
    for i in range(0, 9, 3):
        cols = st.columns(3)
        for j in range(3):
            idx = i + j
            with cols[j]:
                val = st.session_state.board[idx]
                if val == 'X':
                    st.button("❌", key=f"btn_{idx}", disabled=True)
                elif val == 'O':
                    st.button("⭕", key=f"btn_{idx}", disabled=True)
                else:
                    if not st.session_state.game_over:
                        st.button(" ", key=f"btn_{idx}", on_click=make_move, args=(idx,))
                    else:
                        st.button(" ", key=f"btn_{idx}", disabled=True)

# --- Status Messages ---
st.markdown("---")
if st.session_state.game_over:
    if st.session_state.winner == 'X':
        st.markdown('<div class="winner-box"><h2 style="margin:0; color: #00e5ff;">🎉 VICTORY! 🎉</h2><p style="margin:0;">You defeated the AI!</p></div>', unsafe_allow_html=True)
        st.balloons()
    elif st.session_state.winner == 'O':
        st.markdown('<div class="winner-box" style="border-color: #ff0055; background: rgba(255, 0, 85, 0.2);"><h2 style="margin:0; color: #ff0055;">💻 DEFEAT 💻</h2><p style="margin:0;">The AI outsmarted you.</p></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="winner-box" style="border-color: #ffd700; background: rgba(255, 215, 0, 0.2);"><h2 style="margin:0; color: #ffd700;">🤝 DRAW 🤝</h2><p style="margin:0;">No winner this time.</p></div>', unsafe_allow_html=True)
else:
    # Turn Indicator
    if st.session_state.current_turn == 'X':
        st.markdown('<div style="text-align: center; padding: 10px; border-radius: 10px; background: rgba(0, 229, 255, 0.1); border: 1px solid #00e5ff;">👉 <strong>Your Turn</strong> (X)</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="text-align: center; padding: 10px; border-radius: 10px; background: rgba(255, 0, 85, 0.1); border: 1px solid #ff0055;">🤖 <strong>AI Turn</strong> (O)</div>', unsafe_allow_html=True)
