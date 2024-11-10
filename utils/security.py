import streamlit as st
import pandas as pd
from typing import Tuple, Optional
import hashlib
import time
import random
import string

# Constants
MAX_CSV_SIZE_MB = 10
MAX_ROWS = 10000
REQUIRED_COLUMNS = ["DateTime", "Return", "Max Opposite Excursion"]
CHALLENGE_TIMEOUT = 300  # 5 minutes


def validate_csv_file(file) -> Tuple[bool, Optional[str], Optional[pd.DataFrame]]:
    """
    Validate CSV file contents and structure
    Returns: (is_valid, error_message, dataframe)
    """
    try:
        # Check file size
        file_size_mb = file.size / (1024 * 1024)
        if file_size_mb > MAX_CSV_SIZE_MB:
            return False, f"File size exceeds {MAX_CSV_SIZE_MB}MB limit", None

        # Read CSV and perform validations
        df = pd.read_csv(file)

        # Strip whitespace from column names
        df.columns = df.columns.str.strip()

        # Verify required columns
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            return False, f"Missing required columns: {', '.join(missing_cols)}", None

        # Validate data types
        try:
            df["Return"] = pd.to_numeric(df["Return"])
            df["Max Opposite Excursion"] = pd.to_numeric(df["Max Opposite Excursion"])
            pd.to_datetime(df["DateTime"])
        except Exception as e:
            return False, f"Invalid data types in CSV: {str(e)}", None

        # Check for reasonable values
        if df["Return"].abs().max() > 1000 or df["Max Opposite Excursion"].abs().max() > 1000:
            return False, "Values outside reasonable range", None

        return True, None, df

    except pd.errors.EmptyDataError:
        return False, "File is empty", None
    except pd.errors.ParserError:
        return False, "Invalid CSV format", None
    except Exception as e:
        return False, f"Error processing file: {str(e)}", None


class ChallengeSystem:
    """Simple challenge-response system to prevent automated abuse"""

    def __init__(self):
        self.challenges = {}
        self._cleanup_old_challenges()

    def _cleanup_old_challenges(self):
        """Remove expired challenges"""
        current_time = time.time()
        self.challenges = {
            k: v for k, v in self.challenges.items()
            if current_time - v['timestamp'] < CHALLENGE_TIMEOUT
        }

    def generate_challenge(self) -> Tuple[str, str]:
        """Generate a new challenge"""
        challenge = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        challenge_hash = hashlib.sha256(challenge.encode()).hexdigest()

        self.challenges[challenge_hash] = {
            'timestamp': time.time(),
            'attempts': 0
        }

        return challenge, challenge_hash

    def verify_response(self, challenge_hash: str, response: str, max_attempts: int = 3) -> bool:
        """Verify a challenge response"""
        self._cleanup_old_challenges()

        if challenge_hash not in self.challenges:
            return False

        challenge_data = self.challenges[challenge_hash]

        if challenge_data['attempts'] >= max_attempts:
            del self.challenges[challenge_hash]
            return False

        if time.time() - challenge_data['timestamp'] > CHALLENGE_TIMEOUT:
            del self.challenges[challenge_hash]
            return False

        challenge_data['attempts'] += 1

        response_hash = hashlib.sha256(response.encode()).hexdigest()
        if response_hash == challenge_hash:
            del self.challenges[challenge_hash]
            return True

        return False


def init_challenge_system():
    """Initialize challenge system in session state"""
    if 'challenge_system' not in st.session_state:
        st.session_state.challenge_system = ChallengeSystem()
    return st.session_state.challenge_system


def check_rate_limit() -> bool:
    """
    Simple rate limiting based on session state
    Returns: True if allowed, False if limit exceeded
    """
    current_time = time.time()

    if 'last_request_time' not in st.session_state:
        st.session_state.last_request_time = current_time
        st.session_state.request_count = 1
        return True

    # Reset counter after 1 hour
    if current_time - st.session_state.last_request_time > 3600:
        st.session_state.last_request_time = current_time
        st.session_state.request_count = 1
        return True

    # Limit to 10 requests per hour
    if st.session_state.request_count >= 10:
        return False

    st.session_state.request_count += 1
    return True


def init_session_state():
    """Initialize all required session state variables"""
    if 'challenge_verified' not in st.session_state:
        st.session_state.challenge_verified = False
    if 'run_simulation' not in st.session_state:
        st.session_state.run_simulation = False
    if 'current_params' not in st.session_state:
        st.session_state.current_params = None
    if 'current_strategy' not in st.session_state:
        st.session_state.current_strategy = None
    if 'current_csv' not in st.session_state:
        st.session_state.current_csv = None

def clear_session_state():
    """Clear simulation-related session state variables"""
    st.session_state.current_params = None
    st.session_state.current_strategy = None
    st.session_state.current_csv = None
    st.session_state.run_simulation = False


@st.dialog("Security Verification")
def display_challenge():
    """Display challenge form in a modal dialog"""
    challenge_system = init_challenge_system()

    if 'challenge' not in st.session_state:
        challenge, challenge_hash = challenge_system.generate_challenge()
        st.session_state.challenge = challenge
        st.session_state.challenge_hash = challenge_hash

    st.write("To prevent automated abuse, please enter the verification code below:")

    st.markdown(
        f"""
        <div style="
            font-size: 32px;
            font-weight: bold;
            text-align: center;
            padding: 20px;
            font-family: monospace;
            letter-spacing: 3px;
        ">
            {st.session_state.challenge}
        </div>
        """,
        unsafe_allow_html=True
    )

    response = st.text_input("Verification code:", key="challenge_response")

    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("Submit", type="primary"):
            if challenge_system.verify_response(st.session_state.challenge_hash, response):
                st.session_state.challenge_verified = True
                st.session_state.run_simulation = True
                del st.session_state.challenge
                del st.session_state.challenge_hash
                st.rerun()
            else:
                st.markdown("")
                st.error("Invalid code. Please try again.", icon="🚫")
